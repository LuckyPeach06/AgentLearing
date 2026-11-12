from typing import Any, Callable, Dict

from base.myCode.ch7.tool.Tool import Tool


class ToolRegistry:
    """
        HelloAgents工具注册表
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        """
            注册Tool
        """
        if tool.name in self._tools:
            print(f"Alert: 工具 '{tool.name}' 已存在，将被覆盖。")
        self._tools[tool.name] = tool
        print(f"工具 '{tool.name}' 已注册。")

    def register_function(self, 
                          name: str, 
                          description: str, 
                          func: Callable[[str], str]
    ):
        """
            直接注册函数作为工具（简便方式）

            Args:
                name: 工具名称
                description: 工具描述
                func: 工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            print(f"Alert: 工具 '{name}' 已存在，将被覆盖。")

        self._functions[name] = {
            "description": description,
            "func": func
        }
        print(f"工具 '{name}' 已注册。")

    def execute_tool(self, name: str, input_text: str) -> str:
        """
            执行工具:支持 Tool 对象和普通函数两种注册方式
        """
        tool = self._tools.get(name)
        if tool:
            # Tool 对象需要字典参数;这里做一个最简映射
            return tool.run({"input": input_text})

        info = self._functions.get(name)
        if info:
            return info["func"](input_text)

        return f"错误:未找到工具 '{name}'"

    def get_tools_description(self) -> str:
        """
            获取所有可用工具的格式化描述字符串
        """

        description = []

        for tool in self._tools.values():
            description.append(f"- {tool.name}: {tool.description}")

        for name, info in self._functions.items():
            description.append(f"- {name}: {info['description']}")

        return "\n".join(description) if description else "暂无可用工具"

