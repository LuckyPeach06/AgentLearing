"""
第七章 7.2.2 本地模型调用 —— 接入本地 vLLM 服务

前置:
  1. vLLM 已装在 .venv-vllm(独立环境,与主环境隔离)
  2. 已启动本地服务:
       HF_ENDPOINT=https://hf-mirror.com \
       .venv-vllm/bin/python -m vllm.entrypoints.openai.api_server \
           --model Qwen/Qwen1.5-0.5B-Chat --host 127.0.0.1 --port 8000 \
           --gpu-memory-utilization 0.6 --max-model-len 4096

运行(主环境 .venv-linux 即可,不需要 vllm 依赖):
  .venv-linux/bin/python base/myCode/ch7/vllm_test.py
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

# 注意:这里不加载项目 .env(否则 LLM_BASE_URL 会指向 DeepSeek),改为显式传参
from hello_agents import HelloAgentsLLM


def main() -> None:
    # 显式指定 provider / model / base_url,避免被 .env 覆盖
    llm_client = HelloAgentsLLM(
        provider="vllm",
        model="Qwen/Qwen1.5-0.5B-Chat",
        base_url="http://127.0.0.1:8000/v1",
        api_key="vllm",  # 本地服务不需要真实 Key,填任意非空字符串
    )

    print(f"模型: {llm_client.model} | 端点: {llm_client.base_url}\n")

    # 注意:框架版 think() 返回流式生成器(Iterator[str]),不是字符串
    chunks = llm_client.think(
        [{"role": "user", "content": "用一句话介绍一下你自己。"}],
        temperature=0.7,
    )
    response = "".join(chunks)

    print("\n=== 本地模型响应 ===")
    print(response)


if __name__ == "__main__":
    main()
