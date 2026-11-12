# test_reflection_agent.py
from pathlib import Path
import sys

from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from base.myCode.ch7.agents.my_reflection_agent import MyReflectionAgent

load_dotenv()
llm = HelloAgentsLLM()

# 使用默认通用提示词
general_agent = MyReflectionAgent(name="我的反思助手", llm=llm)

# 使用自定义代码生成提示词（类似第四章）
code_prompts = {
    "initial": "你是Python专家，请编写函数：{task}",
    "reflect": "请审查代码的算法效率：\n任务：{task}\n代码：{content}",
    "refine": "请根据反馈优化代码：\n任务：{task}\n反馈：{feedback}"
}
code_agent = MyReflectionAgent(
    name="我的代码生成助手",
    llm=llm,
    custom_prompts=code_prompts
)

# 测试使用
result = code_agent.run("用java写一个判断a=3，b=4，c=5三个变量是否能组成三角形的程序")
print(f"最终结果: {result}")