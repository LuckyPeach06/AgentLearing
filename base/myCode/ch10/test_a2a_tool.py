from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.tools import A2ATool


load_dotenv()
llm = HelloAgentsLLM()

coordinator = SimpleAgent(name="协调者", llm=llm)

researcher_tool = A2ATool(
    name="researcher",
    description="研究员Agent，可以搜索和分析资料",
    agent_url="http://localhost:5000"
)

coordinator.add_tool(researcher_tool)

response = coordinator.run("请让研究员帮我研究AI在教育领域的应用")
print(response)