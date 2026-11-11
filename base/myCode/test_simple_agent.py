from dotenv import load_dotenv
from hello_agents import CalculatorTool, HelloAgentsLLM, ToolRegistry

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from base.myCode.my_simple_agent import MySimpleAgent


load_dotenv()

# 创建LLM实例
llm = HelloAgentsLLM()

# 测试1：基础对话Agent(无工具)
print("=== 测试1:基础对话 ===")
basic_agent = MySimpleAgent(
    name="基础助手",
    llm=llm,
    system_prompt="你是一个友好的AI助手，请用简洁明了的方式回答问题。"
)

response1 = basic_agent.run("你好，请介绍一下你自己")
print(f"基础对话响应: {response1}\n")





# 测试2:带工具的Agent
tool_registey = ToolRegistry()
calculate = CalculatorTool()

tool_registey.register_tool(calculate)

enhanced_agent = MySimpleAgent(
    name="增强助手",
    llm=llm,
    system_prompt="你是一个智能助手，可以使用工具来帮助用户。",
    tool_registry=tool_registey,
    enable_tool_calling=True
)

response2 = enhanced_agent.run("请帮我计算 20 * 6 + 95 - 4")
print(f"工具增强响应: {response2}\n")




# 测试3：流式响应
print("=== 测试3:流式响应 ===")
print("流式响应: ", end="")

for chunk in basic_agent.stream_run("请解释什么是人工智能"):
    pass



# 测试4：动态添加工具
print("\n=== 测试4:动态工具管理 ===")

print(f"添加工具前: {basic_agent.has_tools()}")

basic_agent.add_tool(calculate)

print(f"添加工具后: {basic_agent.has_tools()}")
print(f"可用工具: {basic_agent.list_tools()}")



# 查看对话历史
print(f"\n对话历史: {len(basic_agent.get_history())} 条消息")