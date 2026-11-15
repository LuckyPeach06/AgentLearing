# 清空知识库

from hello_agents.tools import RAGTool
tool = RAGTool()
print(tool.run({"action": "clear", "confirm": True}))
