# 默认规划器提示词模板
import ast
from typing import Dict, Optional

from hello_agents import Config, HelloAgentsLLM, Message, PlanAndSolveAgent

DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

# 默认执行器提示词模板
DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""

class Planner:
    def __init__(self, llm: HelloAgentsLLM, prompt: str):
        self.llm = llm
        self.plan_prompt = prompt
    """s
        根据用户问题生成一个行动计划
    """
    def plan(self, question: str, **kwargs) -> list[str]:
        prompt = self.plan_prompt.format(question = question)

        messages = [
                {
                "role": "user", 
                "content": prompt
                }
            ]
        response_text = self.llm.invoke(messages = messages, **kwargs) or ""

        print(f"计划已生成:\n{response_text}")

        # 解析LLM输出的列表字符串
        try:
            # 找到```python和```之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # 使用ast.literal_eval来安全地执行字符串，将其转换为Python列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []


class Executor:
    def __init__(self, llm: HelloAgentsLLM, prompt: str):
        self.llm = llm
        self.executor_prompt = prompt
    """
        根据计划，逐步执行并解决问题。
    """
    def execute(self, 
                 question: str, 
                 plan: list[str],
                 **kwargs
    ) -> str:
        # 用于存储历史步骤和结果的字符串
        history = "" 
        print("\n--- 正在执行计划 ---")

        for i, step in enumerate(plan):
            print(f"\n-> 正在执行步骤 {i+1}/{len(plan)}: {step}")
            prompt = self.executor_prompt.format(
                question = question,
                plan = plan,
                history = history if history else "无",
                current_step = step
            )

            messages = [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]

            response_text = self.llm.invoke(messages=messages, **kwargs) or ""
            # 更新历史记录，为下一步做准备
            history += f"步骤 {i+1}: {step}\n结果: {response_text}\n\n"
            print(f"步骤 {i+1} 已完成，结果: {response_text}")

        # 最终答案
        final_answer = response_text
        return final_answer

class MyPlanSolveAgent(PlanAndSolveAgent):
    def __init__(
            self,
            name: str,
            llm: HelloAgentsLLM,
            system_prompt: Optional[str] = None,
            config: Optional[Config] = None,
            custom_prompts: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            name, 
            llm, 
            system_prompt, 
            config
        )
        if custom_prompts:
            planner_prompt = custom_prompts.get("planner")
            executor_prompt = custom_prompts.get("executor") 
        else:
            planner_prompt = DEFAULT_PLANNER_PROMPT
            executor_prompt = DEFAULT_EXECUTOR_PROMPT
        
        self.planner = Planner(llm = self.llm, prompt=planner_prompt)
        self.executor = Executor(llm = self.llm, prompt=executor_prompt)

    """
        运行智能体的完整流程:先规划，后执行。
    """
    def run(self, question: str, **kwargs) -> str:
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        plan = self.planner.plan(question, **kwargs)
        
        if not plan:
            print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return

        final_answer = self.executor.execute(question, plan, **kwargs)

        self.add_message(Message(question, "user"))
        self.add_message(Message(final_answer, "assistant"))

        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")

        return final_answer