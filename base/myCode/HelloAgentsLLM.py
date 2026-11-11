import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

class HelloAgentsLLM:

    """
        初始化客户端
    """
    def __init__(self, 
                 api_key: str = None, 
                 model: str = None, 
                 base_url: str = None,
                 timeout: int = None
    ):
  
        """
            入参赋值，如果未传参，则使用环境中的默认值
        """
        try:
            self.api_key = api_key or os.getenv("LLM_API_KEY")
            self.model = model or os.getenv("LLM_MODEL_ID")
            self.base_url = base_url or os.getenv("LLM_BASE_URL")
            self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        except Exception as e:
            print(f"初始化失败，错误信息：{e}")
            return None

        """
            校验密钥、服务地址、模型ID
        """
        if not all([self.model, self.api_key, self.base_url]):
                raise ValueError("API密钥、服务地址、模型ID必须提供或者在环境中定义")

        self.client = OpenAI(api_key = self.api_key, base_url = self.base_url, timeout = self.timeout)

    def think(self, 
              messages: List[Dict[str, str]], 
              temperature: float = 0
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages= messages,
                temperature= temperature,
                stream= True
            )
            collect_content = []
            for chunk in response:
                 if not chunk.choices:
                      continue
                 content = chunk.choices[0].delta.content or ""
                 print(content, end="", flush=True)
                 collect_content.append(content)
            print()
            return "".join(collect_content)
        except Exception as e:
            print(f"调用LLM API出错, 错误信息: {e}")
            return None


    def auto_detct_provider(self, 
                            api_key: Optional[str], 
                            base_url: Optional[str]
    ) -> str:
        """
            自动检测LLM提供商


            根据环境信息，按照下述优先级顺序，尝试自动推断服务商：

            最高优先级：检查特定服务商的环境变量 这是最直接、最可靠的判断依据。
                       框架会依次检查 MODELSCOPE_API_KEY, OPENAI_API_KEY, ZHIPU_API_KEY 
                       等环境变量是否存在。一旦发现任何一个，就会立即确定对应的服务商。

            次高优先级：根据 base_url 进行判断 如果用户没有设置特定服务商的密钥，
                       但设置了通用的 LLM_BASE_URL，框架会转而解析这个 URL。

                域名匹配：通过检查 URL 中是否包含 "api-inference.modelscope.cn", "api.openai.com" 等特征字符串来识别云服务商。
                端口匹配：通过检查 URL 中是否包含 :11434 (Ollama), :8000 (VLLM) 等本地服务的标准端口来识别本地部署方案。

            辅助判断：分析 API 密钥的格式 在某些情况下，如果上述两种方式都无法确定，
                     框架会尝试分析通用环境变量 LLM_API_KEY 的格式。
                     例如，某些服务商的 API 密钥有固定的前缀或独特的编码格式。不过，由于这种方式可能存在模糊性（例如多个服务商的密钥格式相似），因此它的优先级较低，仅作为辅助手段。
        """
         # 1. 检查特定提供商的环境变量 (最高优先级)
        if os.getenv("MODELSCOPE_API_KEY"): return "modelscope"
        if os.getenv("OPENAI_API_KEY"): return "openai"
        if os.getenv("ZHIPU_API_KEY"): return "zhipu"
        # ... 其他服务商的环境变量检查

        # 获取通用的环境变量
        actual_api_key = api_key or os.getenv("LLM_API_KEY")
        actual_base_url = base_url or os.getenv("LLM_BASE_URL")

        # 2. 根据 base_url 判断
        if actual_base_url:
            base_url_lower = actual_base_url.lower()
            if "api-inference.modelscope.cn" in base_url_lower: return "modelscope"
            if "open.bigmodel.cn" in base_url_lower: return "zhipu"
            if "localhost" in base_url_lower or "127.0.0.1" in base_url_lower:
                if ":11434" in base_url_lower: return "ollama"
                if ":8000" in base_url_lower: return "vllm"
                return "local" # 其他本地端口

        # 3. 根据 API 密钥格式辅助判断
        if actual_api_key:
            if actual_api_key.startswith("ms-"): return "modelscope"
            # ... 其他密钥格式判断

        # 4. 默认返回 'auto'，使用通用配置
        return "auto"

    def _resolve_credentials(self, 
                             api_key: Optional[str], 
                             base_url: Optional[str]
    ) -> tuple[str, str]:
        """
            根据provider解析API密钥和base_url
        """
        if self.provider == "openai":
            resolved_api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
            resolved_base_url = base_url or os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1"
            return resolved_api_key, resolved_base_url

        elif self.provider == "modelscope":
            resolved_api_key = api_key or os.getenv("MODELSCOPE_API_KEY") or os.getenv("LLM_API_KEY")
            resolved_base_url = base_url or os.getenv("LLM_BASE_URL") or "https://api-inference.modelscope.cn/v1/"
            return resolved_api_key, resolved_base_url
        
        # ... 其他服务商的逻辑
         

if __name__ == '__main__':
     try:
        llmClient = HelloAgentsLLM()

        messages = [
            {
                    "role": "system",
                    "content": "你是一个Agent开发者"
            },
            {
                "role": "user",
                "content": "用300字之内简单讲解一下什么是智能体,回答要简洁"
            }
        ]
        response = llmClient.think(messages=messages)

        if response:
            print("\n\n响应如下：")
            print(response)
     except Exception as e:
          print(e)
     