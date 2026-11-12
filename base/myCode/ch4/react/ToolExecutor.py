from typing import Any, Dict


class ToolExecutor:

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    """
        注册新工具
    """
    def registerTool(self, name: str, description: str, func: callable):
        if name in self.tools:
            print(f"Error：名为'{name}'的工具已注册，将被覆盖")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具'{name}'已注册.")

    """
        根据工具名获取工具
    """
    def getTool(self, name: str) -> callable:
        return self.tools.get(name, {}).get("func")

    """
        获取所有工具列表
    """
    def getAvailableTools(self) -> str:
        
        return "\n".join([
            f"-{name} : {info['description']}"
            for name, info in self.tools.items()
        ])