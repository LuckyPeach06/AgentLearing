#!/bin/bash
# 第七章 7.2.2 · 启动本地 vLLM 服务(OpenAI 兼容)
#
# 背景:WSL 里没有 gcc / python3.14-dev,所以额外做了三件事:
#   1. 用 pip 包 ziglang 充当 C/C++ 编译器(包装器 cc-zig / cxx-zig)
#   2. 从 CPython 3.14.4 源码 configure 出一套 Python 头文件
#   3. 禁用 FlashInfer 采样器(它要求 nvcc 现场编译),改用原生采样器
# 另外:vLLM 环境放在 ext4(/home/user/venvs/vllm),不要放 /mnt/d,9p 会慢到像卡死。

set -e

VENV=/home/user/venvs/vllm
MODEL=${VLLM_MODEL:-Qwen/Qwen1.5-0.5B-Chat}
PORT=${VLLM_PORT:-8000}

export CC=$VENV/bin/cc-zig
export CXX=$VENV/bin/cxx-zig
export C_INCLUDE_PATH=/home/user/python-headers/include/python3.14
export CPATH=/home/user/python-headers/include/python3.14
export VLLM_USE_FLASHINFER_SAMPLER=0
export HF_ENDPOINT=https://hf-mirror.com

echo "启动 vLLM: model=$MODEL port=$PORT"
echo "首次请求会做算子 JIT 编译(约 30 秒),之后恢复正常速度。"

exec $VENV/bin/python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --host 127.0.0.1 \
    --port "$PORT" \
    --gpu-memory-utilization 0.6 \
    --max-model-len 4096 \
    --enforce-eager
