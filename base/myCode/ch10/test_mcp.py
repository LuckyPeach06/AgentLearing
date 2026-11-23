from hello_agents.tools import MCPTool


mcp_tool = MCPTool()
result = mcp_tool.run({
    "action": "call_tool",
    "tool_name": "add",
    "arguments": {"a": 10, "b": 20}
})

print(f"MCP计算结果:{result}")