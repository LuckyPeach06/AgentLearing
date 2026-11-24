from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.tools import MCPTool


agent = SimpleAgent(name = "test", llm = HelloAgentsLLM())

# MCP 工具的自动展开机制
mcp_tool = MCPTool(name="calculator")
agent.add_tool(mcp_tool)
# MCP工具 'calculator' 已展开为 6 个独立工具
# calculator_add 
# calculator_subtract 
# calculator_multiply 
# calculator_divide 
# calculator_greet 
# calculator_get_system_info 

response = agent.run("计算 25 乘 16")
print(response)  # 输出：25 乘 16 的结果是 400



# 连接外部MCP服务器

# 连接到社区提供的文件系统server
fs_tool = MCPTool(
    name="filesystem",
    description="访问本地文件系统",
    server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]
)
agent.add_tool(fs_tool)

# 连接到自定义Python服务器
custom_tool = MCPTool(
    name="custom_server",
    description="自定义业务逻辑服务器",
    server_command=["python", "my_mcp_server.py"]
)
agent.add_tool(custom_tool)

response = agent.run("请读取README.md文件，并总结其中的主要内容")
print(response)

# 当使用多个 MCP 服务器时，务必为每个 MCPTool 指定不同的 name
# 这个 name 会作为前缀添加到展开的工具名前，避免冲突

