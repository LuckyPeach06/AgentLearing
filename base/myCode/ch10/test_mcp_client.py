import asyncio
import sys
from pathlib import Path

from hello_agents.protocols import MCPClient

async def connect_to_server():
    # 连接到社区提供的文件系统服务器
    # npx自动下载运行@modelcontextprotocol/server-filesystem包
    client = MCPClient([
        "npx",
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "."
    ])

    async with client:
        tools = await client.list_tools()
        print(f"可用工具: {[t['name'] for t in tools]}")


# asyncio.run(connect_to_server())


async def discover_tools():
    client = MCPClient(["npx", "-y", "@modelcontextprotocol/server-filesystem", "."])

    async with client:
        # 获取所有可用工具
        tools = await client.list_tools()

        print(f"服务器提供了 {len(tools)} 个工具：")
        for tool in tools:
            print(f"\n工具名称: {tool['name']}")
            print(f"描述: {tool.get('description', '无描述')}")

            # 打印参数信息
            if 'inputSchema' in tool:
                schema = tool['inputSchema']
                if 'properties' in schema:
                    print("参数:")
                    for param_name, param_info in schema['properties'].items():
                        param_type = param_info.get('type', 'any')
                        param_desc = param_info.get('description', '')
                        print(f"  - {param_name} ({param_type}): {param_desc}")

# asyncio.run(discover_tools())



async def use_tools():
    client = MCPClient(["npx", "-y", "@modelcontextprotocol/server-filesystem", "."])

    async with client:
        # 读取文件
        result = await client.call_tool("read_file", {"path": "README.md"})
        print(f"文件内容：\n{result}")

        # 列出目录
        result = await client.call_tool("list_directory", {"path": "."})
        print(f"当前目录文件：{result}")

        # 写入文件
        result = await client.call_tool("write_file", {
            "path": "output.txt",
            "content": "Hello from MCP!"
        })
        print(f"写入结果：{result}")

# asyncio.run(use_tools())


PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .../agentLearning
SERVER = PROJECT_ROOT / "hello-agents" / "code" / "chapter10" / "my_mcp_server.py"

async def test_mcp():
    # 用当前虚拟环境的 python 启动服务器，避免用到系统 python
    client = MCPClient([sys.executable, str(SERVER)])

    async with client:
        # 1. 工具
        tools = await client.list_tools()
        print(f"可用工具：{[t['name'] for t in tools]}")

        # 2. 资源
        resources = await client.list_resources()
        print(f"可用资源：{[r['uri'] for r in resources]}")
        if resources:
            content = await client.read_resource(resources[0]["uri"])
            print(f"资源内容：{str(content)[:200]}")

        # 3. 提示词
        prompts = await client.list_prompts()
        print(f"可用提示：{[p['name'] for p in prompts]}")
        if prompts:
            prompt = await client.get_prompt(prompts[0]["name"])
            print(f"提示内容：{prompt}")

        # 4. 调用工具
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print(f"add(1, 2) = {result}")


asyncio.run(test_mcp())


# 2. 文件系统服务器 @modelcontextprotocol/server-filesystem 只有工具和资源，
#    没有 prompts，调用 list_prompts 会报 Method not found。
# 3. 文件系统服务器的资源 URI 必须形如 file:///D:/Work/agentLearning/README.md，
#    而且必须在启动时指定的允许目录内，否则会拒绝访问。
