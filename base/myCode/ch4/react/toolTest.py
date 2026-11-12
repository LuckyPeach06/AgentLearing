import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from base.myCode.ch4.react.ToolExecutor import ToolExecutor
from base.myCode.ch4.react.searchTool import search


load_dotenv()

if __name__ == "__main__":
    toolExecutor = ToolExecutor()

    search_description = "一个网页搜索引擎。"

    # 注册工具
    toolExecutor.registerTool("Search", search_description, search)

    # 打印可用工具
    print(toolExecutor.getAvailableTools())

    print("\n---Action：Search['英伟达最新的GPU型号是什么']---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"
    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 ---")
        print(observation)
    else:
        print(f"Error：未找到名为'{tool_name}'的工具")