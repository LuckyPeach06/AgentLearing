"""
    Agent 基类
"""
from abc import ABC, abstractmethod

from pathlib import Path
import sys
from typing import Optional
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from base.myCode import Config, Message
from base.myCode.HelloAgentsLLM import HelloAgentsLLM


class Agent(ABC):
    def __init__(self, 
                 name: str, 
                 llm: HelloAgentsLLM, 
                 system_prompt: Optional[str] = None, 
                 config: Optional[Config] = None
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self.history = list[Message] = []

    @abstractmethod
    def run(self, user_input: str, **kwargs) -> str:
        """
            运行Agent
        """
        pass

    def add_message(self, message: Message):
        """
            添加消息到历史记录
        """
        self.history.append(message)

    def clear_history(self):
        """
            清空历史记录
        """
        self.history.clear()

    def get_history(self) -> list[Message]:
        """
            获取历史记录
        """
        return self.history.copy()

    def __str__(self) -> str:
        return f"Agent(name={self.name}, provider={self.llm.provider})"