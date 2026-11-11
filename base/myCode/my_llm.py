import os
from typing import Optional

from pathlib import Path
import sys

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from base.myCode.HelloAgentsLLM import HelloAgentsLLM


class MyLLM(HelloAgentsLLM):
    """
        一个自定义的LLM客户端，通过继承增加了对ModelScope的支持。
    """  
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: Optional[str] = None, 
                 base_url: Optional[str] = None, 
                 provider: Optional[str] = "auto",
                 **kwargs
    ):
        if provider == "modelscope":
            print("正在使用自定义的 ModelScope Provider")
            self.provider = "modelscope"

            # 解析ModerScope凭证
            self.api_key = api_key or os.getenv("MODELSCOPE_API_KEY")
            self.base_url = base_url or "https://api-inference.modelscope.cn/v1/"

            # 验证凭证是否存在
            if not self.api_key:
                raise ValueError("ModelScope API key not found. Please set MODELSCOPE_API_KEY environment variable.")

            # 设置默认模型和其他参数
            self.model = model or os.getenv("LLM_MODEL_ID") or "Qwen/Qwen3-8B"
            self.temperature = kwargs.get('temperature', 0.7)
            self.max_tokens = kwargs.get('max_tokens')
            self.timeout = kwargs.get('timeout')

            # 创建OpenAI客户端实例
            self.client = OpenAI(api_key=self.api_key, base_url= self.base_url, timeout=self.timeout)
        else:
            super().__init__(api_key = api_key, 
                             model = model, 
                             base_url = base_url, 
                             provider = provider,
                             **kwargs
            )