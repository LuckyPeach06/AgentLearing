import os

from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.tools import MCPTool


load_dotenv()

def create_weather_assistant():
    """创建天气助手"""
    llm = HelloAgentsLLM()
    assistant = SimpleAgent(
        name="天气助手",
        llm=llm,
        system_prompt="""你是天气助手，可以查询城市天气。
使用 mcp_get_weather 工具查询天气，支持中文城市名。
"""
    )
    server_script = os.path.join(os.path.dirname(__file__), "custom_mcp.py")
    weather_tool = MCPTool(server_command=["python", server_script])

    # 显示展开并注册MCP
    expanded_tools = weather_tool.get_expanded_tools()
    if not expanded_tools:
        raise RuntimeError("未发现天气 MCP 子工具，请检查服务脚本、依赖和启动日志。")
    
    for expanded_tool in expanded_tools:
        assistant.add_tool(expanded_tool)

    return assistant

if __name__ == "__main__":
    assistant = create_weather_assistant()
    print("\n查询上海天气：")
    response = assistant.run("伤害今天天气怎么样？")
    print(f"回答: {response}\n")