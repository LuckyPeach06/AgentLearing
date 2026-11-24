from pathlib import Path

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.evaluation import GAIADataset, GAIAEvaluator

# GAIA官方系统提示词（来自论文）
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].

YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.

If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.

If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.

If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."""


llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="TestAgent",
    llm=llm,
    system_prompt=GAIA_SYSTEM_PROMPT  # 关键：使用GAIA官方提示词
)

# 1. 加载数据集
# dataset = GAIADataset(level=1)
# items = dataset.load()
# print(f"加载了 {len(items)} 个样本")

# 本地加载数据集
PROJECT_ROOT = Path(__file__).resolve().parents[3]
GAIA_DATA_DIR = PROJECT_ROOT / "data" / "gaia"

# 2. 创建评估器
evaluator = GAIAEvaluator(local_data_dir=str(GAIA_DATA_DIR), level=1)

# 3. 运行评估
results = evaluator.evaluate(agent, max_samples=5)

# 4. 导出GAIA格式结果
evaluator.export_to_gaia_format(
    results,
    "gaia_results.jsonl",
    include_reasoning=True
)