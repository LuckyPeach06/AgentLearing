from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.context import ContextBuilder, ContextConfig
from hello_agents.tools import MemoryTool, RAGTool


class ContextAwareAgent(SimpleAgent):
    """具备上下文感知能力的Agent"""
    def __init__(self, name: str, llm: HelloAgentsLLM, **kwargs):
        super().__init__(name=name, llm=llm, system_prompt=kwargs.get("system_prompt", ""))

        self.memory_tool = MemoryTool(user_id = kwargs.get("user_id", "default"))
        self.rag_tool = RAGTool(knowledge_base_path=kwargs.get("knowledge_base_path", "./kb"))
        # 初始化上下文builder
        self.context_builder = ContextBuilder(
            memory_tool= self.memory_tool,
            rag_tool= self.rag_tool,
            config= ContextConfig(max_tokens=4000)
        )
        self.conversation_history = []

    def run(self, user_input: str) -> str:
        """运行 Agent，自动构建优化的上下文"""
        context = self.context_builder.build(
            user_query= user_input,
            conversation_history= self.conversation_history,
            system_instructions= self.system_prompt
        )

        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_input}
        ]

        response = self.llm.invoke(messages)

        from hello_agents.core.message import Message
        from datetime import datetime

        self.conversation_history.append(
            Message(content=user_input, role="user", timestamp=datetime.now())
        )
        self.conversation_history.append(
            Message(content=response, role="assistant", timestamp=datetime.now())
        )

        self.memory_tool.run({
            "action": "add",
            "content": f"Q: {user_input}\nA: {response[:200]}...",  # 摘要
            "memory_type": "episodic",
            "importance": 0.6
        })

        return response


agent = ContextAwareAgent(
    name="数据分析顾问",
    llm=HelloAgentsLLM(),
    system_prompt="你是一位资深的Python数据工程顾问。",
    user_id="user123",
    knowledge_base_path="./data_science_kb"
)

response = agent.run("如何优化Pandas的内存占用?")
print(response)