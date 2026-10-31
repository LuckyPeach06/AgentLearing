"""
ReAct 智能体 —— Agent 开发最经典的范式,几乎是所有 Agent 的骨架。

ReAct = Reasoning(推理) + Acting(行动),核心是一个循环:

    ① 把 问题 + 工具清单 + 历史 拼成提示词 → 问 LLM
    ② LLM 输出 Thought(思考)+ Action(行动)
    ③ 代码解析 Action → 执行对应工具 → 得到 Observation(观察结果)
    ④ Observation 写回历史 → 回到 ①
    循环直到 LLM 输出 Finish[最终答案] 或步数耗尽

本实现是"提示词驱动"的经典版本:靠提示词约定 LLM 按
"Thought:/Action:" 格式输出,再用正则解析。
下一课会学它的进化版——函数调用(Function Calling):
由 API 协议原生保证参数格式,不再靠正则猜。

工程细节(面试常问):
  1. max_steps 兜底:防止 LLM 陷入死循环,也防止无限烧 token
  2. temperature=0:输出靠正则解析,必须稳定
  3. 每一步的 Observation 必须写回历史,否则 LLM 会"失忆"
  4. 解析失败不能崩:提示模型重新按格式输出,而不是直接报错
"""
import re
from typing import List, Optional, Tuple

from HelloAgentsLLM import HelloAgentsLLM
from tools import ToolExecutor, calculator, get_current_time

# 提示词模板:注意 .format() 的转义规则——{{ }} 会被替换成字面量 { }
REACT_PROMPT_TEMPLATE = """
请注意,你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程,用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动,必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
  当你收集到足够的信息、能够回答用户的最终问题时,
  你必须在 Action 字段后使用 Finish[最终答案] 输出最终答案。

现在,请开始解决以下问题:
Question: {question}
History: {history}
"""


class ReActAgent:
    """提示词驱动的 ReAct 智能体。"""

    def __init__(self, llm: HelloAgentsLLM, tools: ToolExecutor, max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history: List[str] = []

    def run(self, question: str) -> Optional[str]:
        """执行 ReAct 循环,返回最终答案。"""
        self.history = []  # 每次新问题,清空历史

        for step in range(1, self.max_steps + 1):
            print(f"\n{'=' * 20} 第 {step} 步 {'=' * 20}")

            # 组装提示词:工具清单 + 原问题 + 已积累的历史
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=self.tools.get_available_tools(),
                question=question,
                history="\n".join(self.history) or "(暂无)",
            )

            # temperature=0:解析靠正则,输出必须稳定,不允许"自由发挥"
            response_text = self.llm.think(
                [{"role": "user", "content": prompt}], temperature=0
            )
            if not response_text:
                print("❌ LLM 未能返回有效响应,流程终止。")
                break

            thought, action = self._parse_output(response_text)
            if thought:
                print(f"🤔 思考: {thought}")
            if not action:
                print("⚠️ 未能解析出 Action,流程终止。")
                break

            # 模型决定收工:提取最终答案
            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)\]", action, re.DOTALL).group(1)
                print(f"\n🎉 最终答案: {final_answer}")
                return final_answer

            # 模型决定调用工具
            tool_name, tool_input = self._parse_action(action)
            if not tool_name:
                # 兜底:格式不对不崩,把错误作为观察写回,让模型自我纠正
                self.history.append("Observation: 无效的 Action 格式,请严格按照要求格式输出。")
                continue

            print(f"🎬 行动: {tool_name}[{tool_input}]")
            func = self.tools.get_tool(tool_name)
            if func is None:
                observation = f"错误:未找到名为 '{tool_name}' 的工具。"
            else:
                observation = func(tool_input) if tool_input else func()
            print(f"👀 观察: {observation}")

            # 关键一步:把行动和观察结果写回历史,下一步 LLM 才能"记得"发生了什么
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print(f"\n⏰ 已达到最大步数 {self.max_steps},流程终止。")
        return None

    @staticmethod
    def _parse_output(text: str) -> Tuple[Optional[str], Optional[str]]:
        """从 LLM 输出中解析 Thought 和 Action 两个字段。"""
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    @staticmethod
    def _parse_action(action_text: str) -> Tuple[Optional[str], str]:
        # 如 'calculator[(3+5)*2]' -> ('calculator', '(3+5)*2')
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        return (match.group(1), match.group(2)) if match else (None, "")


# --- ReAct 智能体演示 ---
if __name__ == "__main__":
    llm = HelloAgentsLLM()
    tools = ToolExecutor()
    tools.register_tool(
        "calculator",
        "计算数学表达式的值,如 calculator[(3+5)*2]。仅当需要精确计算时使用。",
        calculator,
    )
    tools.register_tool(
        "get_current_time",
        "获取当前日期和时间。当用户询问现在几点、今天几号时使用。",
        get_current_time,
    )

    agent = ReActAgent(llm, tools)

    print("=" * 50)
    print("问题 1:现在几点了?")
    print("=" * 50)
    agent.run("现在几点了?")

    print("\n\n" + "=" * 50)
    print("问题 2:(3.14 * 2 + 7) / 3 等于多少?")
    print("=" * 50)
    agent.run("(3.14 * 2 + 7) / 3 等于多少?")
