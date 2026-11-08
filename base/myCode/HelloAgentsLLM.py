import os
from typing import Dict, Optional

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
            self.apiKey = api_key or os.getenv("LLM_API_KEY")
            self.model = model or os.getenv("LLM_MODEL_ID")
            self.baseUrl = base_url or os.getenv("LLM_BASE_URL")
            self.timeOut = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        except Exception as e:
            print(f"初始化失败，错误信息：{e}")
            return None

        """
            校验密钥、服务地址、模型ID
        """
        if not all([self.model, self.apiKey, self.baseUrl]):
                raise ValueError("API密钥、服务地址、模型ID必须提供或者在环境中定义")

        self.client = OpenAI(api_key = self.apiKey, base_url = self.baseUrl, timeout = self.timeOut)

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
     