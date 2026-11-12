from pathlib import Path
import sys

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from hello_agents import HelloAgentsLLM

from base.myCode.ch7.tool.my_calculator_tool import create_calculator_registry

load_dotenv()

def test_calculator_tool():
    """测试自定义计算器工具"""

    # 创建包含计算器的注册表
    registry = create_calculator_registry()

    print("测试自定义计算器工具\n")

    # 简单测试用例
    test_cases = [
        "2 + 3",           # 基本加法
        "10 - 4",          # 基本减法
        "5 * 6",           # 基本乘法
        "15 / 3",          # 基本除法
        "sqrt(16)",        # 平方根
    ]

    for i, expression in enumerate(test_cases, 1):
        print(f"测试 {i}: {expression}")
        result = registry.execute_tool("my_calculator", expression)
        print(f"结果: {result}\n")

def test_with_simple_agent():
    """测试与SimpleAgent的集成"""

    # 创建LLM客户端
    llm = HelloAgentsLLM()

    # 创建包含计算器的注册表
    registry = create_calculator_registry()

    question = "请帮我计算 sqrt(16) + 2 * 3"

    print(f"用户问题: {question}")

    result = registry.execute_tool("my_calculator", "sqrt(16) + 2 * 3")

    print(f"计算结果: {result}")

    messages = [
        {
            "role": "user", 
            "content": f"计算结果是 {result}，请用自然语言回答用户的问题:{question}"
        }
    ]

    print("\nSimpleAgent的回答:")
    response = llm.think(messages)

    for chunk in response:
        # print(chunk, end="", flush=True)
        pass

    print("\n")

if __name__ == "__main__":
    test_calculator_tool()
    test_with_simple_agent()
