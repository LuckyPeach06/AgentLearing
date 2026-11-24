from dotenv import load_dotenv

load_dotenv()

from hello_agents.evaluation import GAIADataset
import os

# HF_TOKEN 从项目根目录 .env 读取（GAIA 是 gated dataset）
# 国内直连 HuggingFace 不通时，运行前设置 HF_ENDPOINT=https://hf-mirror.com

# 自动下载到 ./data/gaia/
dataset = GAIADataset(
    dataset_name="gaia-benchmark/GAIA",
    split="validation",  # 或 "test"
    level=1  # 可选: 1, 2, 3, None(全部)
)
items = dataset.load()

print(f"加载了 {len(items)} 个测试样本")
# 输出: 加载了 53 个测试样本 (Level 1)