# 本地模型(vLLM)

## 第一步:启服务

```bash
bash base/myCode/ch7/vllm/start_vllm.sh
```

> 首次请求约需 30 秒(Triton 算子 JIT 编译,一次性开销),之后恢复正常速度。

## 第二步:代码里接入

```python
llm_client = HelloAgentsLLM(
    provider="vllm",
    model="Qwen/Qwen1.5-0.5B-Chat",
    base_url="http://127.0.0.1:8000/v1",
    api_key="vllm",
)
```

> 注意:框架版 `think()` 返回**流式生成器**,要用 `"".join(chunks)` 才能得到完整文本。

## 第三步:关闭服务

### 前台启动的

在运行 `start_vllm.sh` 的终端按 **`Ctrl + C`**。

### 后台启动的(推荐:按进程名精确匹配)

```bash
pgrep -f "^/home/user/venvs/vllm/bin/python -m vllm" | xargs -r kill
```

若 10 秒内仍未退出,再补一刀:

```bash
pgrep -f "^/home/user/venvs/vllm/bin/python -m vllm" | xargs -r kill -9
```

### 或者按 PID 关

```bash
# 先查 PID
pgrep -af "^/home/user/venvs/vllm/bin/python -m vllm"

# 再按 PID 关闭
kill <PID>
```

### 确认是否已停止

```bash
# 1) 进程应为空
pgrep -f "^/home/user/venvs/vllm/bin/python -m vllm" || echo "已停止"

# 2) 端口应无响应
curl -s --max-time 2 http://127.0.0.1:8000/v1/models || echo "端口无响应"

# 3) 显存应回落到 ~2.7GB(服务运行时约 12.6GB)
nvidia-smi --query-gpu=memory.used --format=csv,noheader
```

## ⚠️ 注意事项

1. **不要用** `pkill -f "vllm.entrypoints.openai.api_server"`——这个模式会连同启动它的 bash 一起匹配,把自己的 shell 也杀掉(表现为退出码 144)。用上面带 `^` 锚定的写法最稳。
2. vLLM 环境必须放在 WSL 原生 ext4 盘(`/home/user/venvs/vllm`);放 `/mnt/d` 会因 9p 文件系统慢到像卡死。
3. 模型缓存位于 `~/.cache/huggingface`(Qwen/Qwen1.5-0.5B-Chat,约 1.2G)。
4. HuggingFace 直连被墙,启动脚本里已设置 `HF_ENDPOINT=https://hf-mirror.com`。
