"""
工具(Tool)模块 —— Agent 的"手和眼"。

核心约定:任何工具都是一个普通 Python 函数,输入是字符串,输出是字符串。
为什么必须是字符串?因为 LLM 只能读写文本,工具和 LLM 之间的一切
通信都要经过文本序列化。这一点是理解 Agent 的钥匙。

本文件包含:
  1. calculator / get_current_time 两个示例工具
  2. ToolExecutor:负责注册工具、查找工具、生成工具清单描述
"""
import re
from datetime import datetime
from typing import Any, Callable, Dict, Optional


def calculator(expression: str) -> str:
    """
    计算数学表达式的值,如 "(3.14 * 2 + 7) / 3"。
    只支持数字和 + - * / ( ) 运算符。
    """
    print(f"🧮 正在执行 [calculator] 工具: {expression}")
    # 容错:LLM 偶尔会给参数包上引号,先剥掉
    expression = expression.strip().strip('"').strip("'")

    # 安全第一:eval 执行任意代码极其危险(和 SQL 注入一个道理)。
    # 这里用白名单正则先校验,只放行数字和运算符,字母、引号一律拒绝。
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression):
        return "错误:表达式包含非法字符,仅支持数字和 + - * / ( ) 运算符。"
    try:
        return str(eval(expression))  # 白名单校验通过后,eval 才是安全的
    except Exception as e:
        return f"计算出错: {e}"


def get_current_time() -> str:
    """获取当前日期和时间。当用户询问"现在几点/今天几号"时使用。"""
    print("🕐 正在执行 [get_current_time] 工具")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ToolExecutor:
    """
    工具执行器:注册工具、查找工具、生成给 LLM 看的工具清单。

    相当于一个极简的"服务注册中心":register 就是服务注册,
    get_available_tools 就是把服务清单告诉"大脑"。
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, func: Callable) -> None:
        """注册工具。description 是给 LLM 看的,写得好坏直接决定模型会不会调用它。"""
        self.tools[name] = {"description": description, "func": func}

    def get_tool(self, name: str) -> Optional[Callable]:
        """按名称取工具的执行函数。"""
        return self.tools.get(name, {}).get("func")

    def get_available_tools(self) -> str:
        """生成工具清单文本,会被塞进提示词告诉 LLM 它有哪些能力。"""
        return "\n".join(
            f"- {name}: {info['description']}" for name, info in self.tools.items()
        )


# --- 工具自测 ---
if __name__ == "__main__":
    executor = ToolExecutor()
    executor.register_tool(
        "calculator", "计算数学表达式的值,如 calculator[(3+5)*2]。", calculator
    )
    executor.register_tool(
        "get_current_time", "获取当前日期和时间。", get_current_time
    )

    print("--- 工具清单 ---")
    print(executor.get_available_tools())
    print("\n--- 自测 ---")
    print(calculator("(3+5)*2"))
    print(get_current_time())
