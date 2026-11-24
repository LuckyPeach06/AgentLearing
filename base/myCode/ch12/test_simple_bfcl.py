from dotenv import load_dotenv

load_dotenv()

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import BFCLEvaluationTool

llm = HelloAgentsLLM()
agent = SimpleAgent(name="TestAgent", llm=llm)

bfcl_tool = BFCLEvaluationTool()

results = bfcl_tool.run(
    agent=agent,
    category="simple_python",
    max_samples=5
)

print(f"准确率: {results['overall_accuracy']:.2%}")
print(f"正确数: {results['correct_samples']}/{results['total_samples']}")

# 输出报错:未找到bfcl命令,请先安装: pip install bfcl-eval
# 这不是报错，脚本本身已经 EXIT=0。
# 它只是提示：官方 BFCL 评分工具 bfcl-eval 没装，所以跳过了“用官方 CLI 复核”这一步。
# 这不是环境配置的问题，是 bfcl-eval 目前不支持 Python 3.14。
