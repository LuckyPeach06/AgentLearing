import re
from typing import List, Optional

from hello_agents import Config, HelloAgentsLLM, Message, ReActAgent, ToolRegistry


MY_REACT_PROMPT = """
你是一个具备推理和行动能力的AI助手。
你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确答案。

## 可用工具：
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤:

Thought: 分析当前问题，思考需要什么信息或采取什么行动
Action: 选择一个行动，格式必须是以下之一：
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你认为有足够的信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用必须严格遵循: 工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或者相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动:
"""

class MyReActAgent(ReActAgent):
    def __init__(self, 
                 name: str, 
                 llm: HelloAgentsLLM, 
                 tool_registry: ToolRegistry, 
                 system_prompt: Optional[str] = None, 
                 config: Optional[Config] = None, 
                 max_steps: int = 5, 
                 custom_prompt = Optional[str] = None
    ):
        super().__init__(name, 
                         llm, 
                         system_prompt, 
                         config
        )
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.custom_history = List[str] = []
        self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT

        print(f"{name} 初始化完成，最大步数: {max_steps}")

    """
        运行LLM回答一个问题
    """
    def run(self, input_text: str, **kwargs) -> str:
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第{current_step}步 ---")

            # 1.格式化提示词
            tool_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.history)

            prompt = self.prompt_template.format(
                tools = tool_desc,
                question = input_text,
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
            response_content = self.llm.invoke(messages = messages, **kwargs)
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
                final_answer = self._parse_action_input()
                self.add_message(Message(input_text, "user"))
                self.add_message(Message(final_answer, "assistant"))
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_input or not tool_name:
                continue
            print(f"Action:{tool_name}[{tool_input}]")

            tool_function = self.tool_registry.get_tool(tool_name)
            if not tool_function:
                observation = f"ERROR: 未找到名为'{tool_name}'的工具"
            else:
                observation = self.tool_registry.execute_tool(tool_input)

            print(f"Observation: {observation}")

            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        # 达到最大步数
        final_answer = "抱歉，我无法在限定步数内完成这个任务。"
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer, "assistant"))
        return final_answer

    

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