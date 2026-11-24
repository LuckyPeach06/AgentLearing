import random

from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.protocols import ANPDiscovery, register_service
from hello_agents.tools import ANPTool


load_dotenv()

llm = HelloAgentsLLM()

# 创建注册中心
discovery = ANPDiscovery()

# 注册节点
for i in range(10):
    register_service(
        discovery=discovery,
        service_id=f"node_{i}",
        service_name="节点{i}",
        service_type="compute",
        capabilities=["data_processing", "ml_training"],
        endpoint=f"http://node{i}:8000",
        metadata={
            "load": random.uniform(0.1, 0.9),
            "cpu_cores": random.choice([4, 8, 16]),
            "memory_gb": random.choice([16, 32, 64]),
            "gpu": random.choice([True, False])
        }
    )

print(f"注册了 {len(discovery.list_all_services())} 个计算节点")

agent = SimpleAgent(
    name="任务调度器",
    llm=llm,
    system_prompt="""你是一个智能任务调度器，负责：
1. 分析任务需求
2. 选择最合适的计算节点
3. 分配任务

选择节点时考虑：负载、CPU核心数、内存、GPU等因素。"""
)

anp_tool = ANPTool(
    name="service_discovery",
    description="服务发现工具，可以查找和选择计算节点",
    discovery=discovery
)

agent.add_tool(anp_tool)

# 分配任务
def assign_task(task_desp):
    print(f"\n任务：{task_desp}")
    print("=" * 50)

    resp = agent.run(f"""
    请为以下任务选择最合适的计算节点：
    {task_desp}

    要求：
    1. 传入 action="discover_services" 获取所有节点列表
    2. 分析每个节点的特点
    3. 选择最合适的节点
    4. 说明选择理由
    """)
    print(resp)
    print("=" * 50)


# 测试
# assign_task("训练一个大型深度学习模型，需要GPU支持")
assign_task("处理大量文本数据，需要高内存")
# assign_task("运行轻量级数据分析任务")