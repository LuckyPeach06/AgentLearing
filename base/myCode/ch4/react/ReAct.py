import re
import sys
from pathlib import Path

# 先修路,再开车:路径修复必须放在 base 导入之前
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from base.myCode.ch4.core.HelloAgentsLLM import HelloAgentsLLM
from base.myCode.ch4.react.ToolExecutor import ToolExecutor
from base.myCode.ch4.react.searchTool import search

REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的AI智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回答：
Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{toolname}}[{{tool_input}}]`: 调用一个可用工具
- `Finish[最终答案]:当你认为已经获得最终答案时`
- 当你收集到足够信息，能够回答用户的最终问题时，你必须在Action:字段后使用Finish[最终答案]来输出最终答案

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""

class ReActAgent:
    def __init__(self, 
                 llm_client: HelloAgentsLLM,
                 tool_executor: ToolExecutor,
                 max_steps: int = 5
    ):
        self.client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    """
        运行LLM回答一个问题
    """
    def run(self, question: str):
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第{current_step}步 ---")

            # 1.格式化提示词
            tool_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)

            prompt = REACT_PROMPT_TEMPLATE.format(
                tools = tool_desc,
                question = question,
                history = history_str
            )

            # 2.调用LLM进行思考
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # ReAct 的输出要靠正则解析,格式必须稳定，temperature必须为0
            response_content = self.client.think(messages = messages)
            if not response_content:
                print(f"ERROR:LLM未收到有效返回内容")
                break

            # 解析LLM输出
            thought, action = self._parse_output(response_content)

            if thought:
                print(f"thinking:{thought}")

            if not action:
                print("Alert:未能解析出有效的Action.流程终止.")
                break

            # 执行Action
            if action.startswith("Finish"):
                # 如果是Finish，直接提取最终答案并结束
                # final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                # DOTALL:最终答案常常是多行的,必须让 . 匹配换行符
                match = re.match(r"Finish\[(.*)\]", action, re.DOTALL)
                if not match:
                    # 兜底:格式不完整也不能崩,把原文当答案返回
                    print("⚠️ Finish 格式不完整,无法提取答案。")
                    return action
                final_answer = match.group(1)
                print(f"最终答案: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_input or not tool_name:
                continue
            print(f"Action:{tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"ERROR: 未找到名为'{tool_name}'的工具"
            else:
                observation = tool_function(tool_input)

            print(f"Observation: {observation}")

            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止.")
        return None

    

    """
        解析LLM输出，提取Thought和Action
    """
    def _parse_output(self, text: str):
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action

    """
        解析Action字符串，提取工具名称和用户输入
    """
    def _parse_action(self, action_text: str):
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

if __name__ == "__main__":

    # 组装:LLM + 工具执行器 + 注册搜索工具
    llm = HelloAgentsLLM()
    tools = ToolExecutor()
    tools.registerTool(
        "Search",
        "一个网页搜索引擎。当你需要查询实时信息、新闻或不确定的事实时,应使用此工具。",
        search,
    )

    question = "苹果手机最新型号以及主要卖点"
    agent = ReActAgent(llm, tools)
    agent.run(question)