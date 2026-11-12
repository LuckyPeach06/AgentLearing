from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from base.myCode.ch4.core.HelloAgentsLLM import HelloAgentsLLM
from base.myCode.ch4.reflection.Memory import Memory


INITIAL_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。请根据以下要求，编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

要求: {task}

请直接输出代码，不要包含任何额外的解释。
"""

REFLECT_PROMPT_TEMPLATE = """
你是一位极其严格的代码评审专家和资深算法工程师，对代码的性能有极致的要求。
你的任务是审查以下Python代码，并专注于找出其在算法效率上的主要瓶颈。

# 原始任务:
{task}

# 待审查的代码:
```python
{code}
```

请分析该代码的时间复杂度，并思考是否存在一种算法上更优的解决方案来显著提升性能。
如果存在，请清晰地指出当前算法的不足，并提出具体的、可行的改进算法建议（例如，使用筛法替代试除法）。
如果代码在算法层面已经达到最优，才能回答“无需改进”。

请直接输出你的反馈，不要包含任何额外的解释。
在反馈的最后一行，必须单独给出结论，格式严格为以下两种之一（不要输出其他内容）：
结论:需要改进
或
结论:无需改进
"""

REFINE_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。你正在根据一位代码评审专家的反馈来优化你的代码。

# 原始任务:
{task}

# 你上一轮尝试的代码:
{last_code_attempt}
评审员的反馈：
{feedback}

请根据评审员的反馈，生成一个优化后的新版本代码。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。
请直接输出优化后的代码，不要包含任何额外的解释。
"""

class ReflectionAgent:
    def __init__(self, llm_client: HelloAgentsLLM, max_iterations: int = 5):
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations

    def run(self, task: str):
        print(f"\n--- 开始处理任务 ---\n任务: {task}")

        # --- 1. 初始执行 ---
        print("\n--- 正在进行初始尝试 ---")
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task = task)
        initial_code = self.get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)

        # --- 2. 迭代循环:反思与优化 ---
        for i in range(self.max_iterations):
            print(f"\n--- 第 {i+1}/{self.max_iterations} 轮迭代 ---")

            # a. 反思
            print("\n-> 正在进行反思...")

            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task = task, code = last_code)
            feedback = self.get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            # b. 检查是否需要停止
            # 只看最后一行结论,避免"不宜判定为无需改进"这类否定句被子串误匹配
            if feedback.strip().endswith("无需改进") or feedback.strip().endswith("no need for improvement"):
                print("\n反思认为代码已无需改进，任务完成。")
                break
            # c. 优化
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task = task,
                last_code_attempt = last_code,
                feedback = feedback
            )
            refined_code = self.get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)

        final_code = self.memory.get_last_execution() or ""
        # 模型输出的代码可能自带 ```python 围栏,剥掉,避免与打印层的围栏重复
        if final_code.strip().startswith("```"):
            first_newline = final_code.find("\n")
            final_code = final_code[first_newline + 1:] if first_newline != -1 else final_code[3:]
            final_code = final_code.rsplit("```", 1)[0].strip()
        print(f"\n--- 任务完成 ---\n最终生成的代码:\n```python\n{final_code}\n```")
        return final_code

    def get_llm_response(self, prompt) -> str:
        """
            一个辅助方法，用于调用LLM并获取完整的流式响应。
        """
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages) or ""

        return response_text    


if __name__ == "__main__":
    helloAgentsLLM = HelloAgentsLLM()

    task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"

    reflectionAgent = ReflectionAgent(llm_client = helloAgentsLLM)
    reflectionAgent.run(task= task)