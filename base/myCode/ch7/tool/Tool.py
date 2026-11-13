from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .ToolParameter import ToolParameter

class Tool(ABC):
    """
        工具基类
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, parameters: Dict[str, Any]) -> str:
        """
            执行工具
        """
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """
            获取工具参数定义
        """
        pass