"""
任务:在 agentLearning 的 base 文件夹下生成一个 HelloAgentsLLM 的 Python 类,
类中需要为该项目定制一个 LLM 客户端,用于调用任何兼容 OpenAI 接口的服务,并默认使用流式响应。

学习来源:
  - 教程书《Hello-Agents 从零开始构建智能体》第四章 code/chapter4/llm_client.py
  - 自研框架 hello_agents 的 hello_agents/core/llm.py(本类是该类的最小原型)

核心知识点:
  1. OpenAI 兼容协议:任何实现了 POST {base_url}/chat/completions 的服务
     (DeepSeek、Qwen、Kimi、智谱、Ollama 本地模型……)都可以用 OpenAI SDK 调用,
     区别只在 base_url 和 model 名。
  2. 流式响应(SSE):请求带 stream=True,服务端按 chunk 推送增量文本,
     实现"打字机"效果。流式是 Agent 场景的默认选择——工具调用(第七章会学到)必须依赖流式。
  3. 配置优先级:显式传参 > 环境变量,这是框架的通用约定。
"""
import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Windows 控制台默认编码是 GBK,打印 emoji(🧠 等)会报 UnicodeEncodeError。
# 把当前进程的标准输出强制切换为 UTF-8(仅影响本进程,不影响系统设置)。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:  # 极少数非标准 stdout 环境不支持 reconfigure
    pass

# 从 .env 加载 LLM_MODEL_ID / LLM_API_KEY / LLM_BASE_URL 等环境变量
load_dotenv()


class HelloAgentsLLM:
    """为 HelloAgents 项目定制的 LLM 客户端,默认使用流式响应。"""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        初始化客户端。参数优先级:显式传参 > 环境变量(.env)。

        Args:
            model:    模型 ID,默认取 LLM_MODEL_ID 
            api_key:  API 密钥,默认取 LLM_API_KEY
            base_url: 服务地址,默认取 LLM_BASE_URL(OpenAI 兼容端点)
            timeout:  请求超时秒数,默认取 LLM_TIMEOUT,兜底 60
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", "60"))

        # 缺一不可,提前失败并给出可读的错误信息
        missing = [
            name
            for name, value in (
                ("model", self.model),
                ("api_key", self.api_key),
                ("base_url", self.base_url),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                f"缺少必要配置: {', '.join(missing)}。"
                "请通过构造参数传入,或在 .env 中定义 LLM_MODEL_ID / LLM_API_KEY / LLM_BASE_URL。"
            )

        # 底层真正干活的是 OpenAI SDK 的客户端,我们只是包一层统一配置
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def think(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = True,
    ) -> Optional[str]:
        """
        调用大语言模型进行思考,并返回其完整响应文本。

        Args:
            messages:    消息列表,形如 [{"role": "system", "content": "..."},
                                        {"role": "user", "content": "..."}]
            temperature: 采样温度,0=确定性强,越高越发散
            stream:      是否流式输出,默认 True

        Returns:
            完整响应文本;调用失败返回 None
        """
        print(f"🧠 正在调用 {self.model} ...")
        try:
            if stream:
                return self._think_stream(messages, temperature)
            return self._think_sync(messages, temperature)
        except Exception as e:
            print(f"❌ 调用 LLM API 时发生错误: {e}")
            return None

    def _think_stream(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """流式调用:边收 chunk 边打印,最后返回拼接的完整文本。"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,  # 关键:开启 SSE 流式响应
        )

        print("✅ 大语言模型响应成功:")
        collected: List[str] = []
        for chunk in response:
            # 某些服务商的 chunk 可能没有 choices(如首尾的心跳包),直接跳过
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            collected.append(content)
        print()  # 流式结束后换行
        return "".join(collected)

    def _think_sync(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """非流式调用:一次性返回完整响应(调试时偶尔用)。"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=False,
        )
        content = response.choices[0].message.content or ""
        print(content)
        return content

    def __repr__(self) -> str:
        return f"HelloAgentsLLM(model={self.model!r}, base_url={self.base_url!r})"


# --- 客户端使用示例 ---
if __name__ == "__main__":
    try:
        llm = HelloAgentsLLM()
        print(llm)

        messages = [
            {"role": "system", "content": "你是一个乐于助人的中文助手,回答要简洁。"},
            {"role": "user", "content": "用一句话解释什么是智能体(Agent)?"},
        ]

        # 默认流式调用
        full_text = llm.think(messages)
        print("\n--- 完整模型响应 ---")
        print(full_text)

    except ValueError as e:
        print(e)
