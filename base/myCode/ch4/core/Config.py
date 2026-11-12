"""
    配置管理
"""
import os
from typing import Any, Dict, Optional

from pydantic import BaseModel


class Config(BaseModel):
    # LLM配置
    default_model: str = "deepseek-flash"
    default_provider: str = "openai"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # 系统配置
    debug: bool = False
    log_level: str = "INFO"

    # 其他配置
    max_history_length: int = 100

    @classmethod
    def from_env(cls) -> "Config":
        """
            从环境变量中读取配置
        """
        return cls(
            debug = os.getenv("DEBUG", "false").lower() == "true",
            log_level = os.getenv("LOG_LEVEL", "INFO"),
            temperature = float(os.getenv("TEMPERATURE", "0.7")),
            max_token = int(os.getenv("MAX_TOKEN", "0.7")) if os.getenv("MAX_TOKEN") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()