from hello_agents.tools import ANPTool


anp_tool = ANPTool()
result = anp_tool.run({
    "action": "register_service",
    "service_id": "calculator",
    "service_type": "math",
    "endpoint": "http://localhost:8080"
})

services = anp_tool.run({
    "action": "discover_services"
})

print(f"发现的服务: {services}")