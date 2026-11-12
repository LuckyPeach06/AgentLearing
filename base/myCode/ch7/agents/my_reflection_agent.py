DEFAULT_PROMPTS = {
    "initial": """
        请根据以下要求完成任务：

        任务:
        {task}

        请提供一个完整、准确的回答。
    """,
    "reflect": """
        请仔细审查以下回答，并找出可能的问题或改进空间:

        # 原始任务:
        {task}

        # 当前回答:
        {content}

        请给出反馈，分析这个回答的质量，如果有不足之处，请提出具体的改进建议，只有回答的质量已经很好，才能回答"无需改进"。
        在反馈的最后一行，必须单独给出结论，格式严格为以下两种之一（不要输出其他内容）：
        结论:需要改进
        或
        结论:无需改进
    """,
    "refine": """
        请根据反馈意见改进你的回答:

        # 原始任务:
        {task}
        
        # 上一轮回答:
        {last_attempt}

        # 反馈意见:
        {feedback}

        请提供一个改进后的回答。
    """
}

from pathlib import Path
import sys
from typing import Dict, Optional

from hello_agents import Config, HelloAgentsLLM, Message, ReflectionAgent

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from base.myCode.ch7.common.my_memory import MyMemory


class MyReflectionAgent(ReflectionAgent):
    def __init__(self, 
                 name: str, 
                 llm: HelloAgentsLLM, 
                 system_prompt: Optional[str] = None, 
                 config: Optional[Config] = None, 
                 max_iterations: int = 3, 
                 custom_prompts: Optional[Dict[str, str]] = None
    ):
        super().__init__(name, 
                         llm, 
                         system_prompt, 
                         config, 
                         max_iterations
        )
        self.prompts = custom_prompts if custom_prompts else DEFAULT_PROMPTS
        print(f"{name} 初始化已完成, 最大迭代次数:{max_iterations}")


    def run(self, task: str, **kwargs):
        self.memory = MyMemory()
        print(f"\n--- 开始处理任务 ---\n任务: {task}")

        # --- 1. 初始执行 ---
        print("\n--- 正在进行初始尝试 ---")
        initial_prompt = self.prompts["initial"].format(task = task)
        initial_answer = self._get_llm_response(initial_prompt, **kwargs)
        self.memory.add_record("execution", initial_answer)

        # --- 2. 迭代循环:反思与优化 ---
        for i in range(self.max_iterations):
            print(f"\n--- 第 {i+1}/{self.max_iterations} 轮迭代 ---")

            # a. 反思
            print("\n-> 正在进行反思...")

            last_answer = self.memory.get_last_execution()
            reflect_prompt = self.prompts["reflect"].format(task = task, content = last_answer)
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            # b. 检查是否需要停止
            # 只看最后一行结论,避免"不宜判定为无需改进"这类否定句被子串误匹配
            last_line = feedback.strip().splitlines()[-1] if feedback.strip() else ""
            if "无需改进" in last_line:
                print("\n反思认为代码已无需改进，任务完成。")
                break
            # if feedback.strip().endswith("无需改进"):
            #     print("\n反思认为代码已无需改进，任务完成。")
            #     break
            # c. 优化
            refine_prompt = self.prompts["refine"].format(
                task = task,
                last_attempt = last_answer,
                feedback = feedback
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)

        final_answer = self.memory.get_last_execution() or ""
        # 模型输出的代码可能自带 ```python 围栏,剥掉,避免与打印层的围栏重复
        if final_answer.strip().startswith("```"):
            first_newline = final_answer.find("\n")
            final_answer = final_answer[first_newline + 1:] if first_newline != -1 else final_answer[3:]
            final_answer = final_answer.rsplit("```", 1)[0].strip()

        self.add_message(Message(task, "user"))
        self.add_message(Message(final_answer, "assistant"))
        
        print(f"\n--- 任务完成 ---\n最终生成的代码:\n```python\n{final_answer}\n```")
        return final_answer