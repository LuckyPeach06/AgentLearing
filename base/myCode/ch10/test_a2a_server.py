import threading
import time

from hello_agents.protocols import A2AServer


researcher = A2AServer(
    name="researcher",
    description="负责搜索和分析资料的agent",
    version="1.0.0"
)

# 定义技能
@researcher.skill("research")
def handle_research(text: str) -> str:
    """处理研究请求"""
    import re
    match = re.search(r'research\s+(.+)', text, re.IGNORECASE)
    topic = match.group(1).strip() if match else text
    
    # 实际的研究逻辑（这里简化）
    result = {
        "topic": topic,
        "findings": f"关于{topic}的研究结果...",
        "sources": ["来源1", "来源2", "来源3"]
    }
    return str(result)

def start_server():
    researcher.run(host="localhost", port=5000)


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n服务已停止")