from hello_agents.protocols import A2AClient


client = A2AClient("http://localhost:5000")

response = client.execute_skill("research", "research AI在医疗领域的应用")

print(f"收到响应：{response.get('result')}")