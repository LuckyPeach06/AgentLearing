from dotenv import load_dotenv

load_dotenv()

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.evaluation import BFCLDataset, BFCLEvaluator


llm = HelloAgentsLLM()
agent = SimpleAgent(name="TestAgent", llm=llm)

# 加载数据集
dataset = BFCLDataset(
    bfcl_data_dir="./temp_gorilla/berkeley-function-call-leaderboard/bfcl_eval/data",
    category="simple_python"
)

data = dataset.load()

# 创建评估器
evaluator = BFCLEvaluator(
    dataset=dataset,
    category="simple_python",
    evaluation_mode="ast" # 使用AST匹配模式
)

# 运行评估
results = evaluator.evaluate(agent, max_samples=10)

print(f"准确率: {results['overall_accuracy']:.2%}")
print(f"正确数: {results['correct_samples']}/{results['total_samples']}")
