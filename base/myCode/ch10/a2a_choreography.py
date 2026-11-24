import ast
import json
import re
import threading
import time

from hello_agents.protocols import A2AClient, A2AServer

# ================= 1. Agent 1 (供应商/服务端) =================
# Agent 1 只需被动接收提案并给出评估结果，不需要主动发起任何网络请求
agent1 = A2AServer(
    name="agent1",
    description="Agent1 (评估方)"
)

@agent1.skill("propose")
def handle_proposal(text: str) -> str:
    """处理协商提案"""
    match = re.search(r'propose\s+(.+)', text, re.IGNORECASE)
    proposal_str = match.group(1).strip() if match else text

    try:
        proposal = ast.literal_eval(proposal_str)
        task = proposal.get("task")
        deadline = proposal.get("deadline")
        
        # 核心业务逻辑：少于7天直接拒绝，并给出7天的反提案
        if deadline >= 7:
            result = {"accepted": True, "message": f"接受提案，将在 {deadline} 天内完成 {task}"}
        else:
            result = {
                "accepted": False,
                "message": f"时间太紧（{deadline}天），无法完成",
                "counter_proposal": {"deadline": 7}
            }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"accepted": False, "message": f"无效的提案格式: {e}"}, ensure_ascii=False)


# ================= 2. Agent 2 (业务方/客户端) =================
# Agent 2 是自治的，它内部会发起网络请求去找 Agent 1 谈判
agent2 = A2AServer(
    name="agent2",
    description="Agent 2 (发起方)"
)

@agent2.skill("negotiate")
def negotiate_task(text: str) -> str:
    """发起并完成整套协商流程"""
    match = re.search(r'negotiate\s+task:(.+?)\s+deadline:(\d+)', text, re.IGNORECASE)
    if not match:
        return json.dumps({"status": "error", "message": "无效的协商请求"}, ensure_ascii=False)
        
    task = match.group(1).strip()
    current_deadline = int(match.group(2))
    
    # 【关键】Agent 2 内部实例化 Client，主动去连接 Agent 1 (7000端口)
    a1_client = A2AClient("http://127.0.0.1:7000")
    
    negotiation_logs = []
    max_rounds = 3
    
    # 【核心】Agent 2 内部的自治协商循环
    for round_num in range(1, max_rounds + 1):
        proposal = {"task": task, "deadline": current_deadline}
        negotiation_logs.append(f"第 {round_num} 轮 - 我提出: {current_deadline}天")
        
        try:
            # 向 Agent 1 发起 RPC 调用
            response = a1_client.execute_skill("propose", f"propose {proposal}")
            res_dict = json.loads(response.get('result', '{}'))
            
            if res_dict.get("accepted"):
                negotiation_logs.append(f"对方接受: {res_dict.get('message')}")
                return json.dumps({
                    "status": "success",
                    "final_deadline": current_deadline,
                    "logs": negotiation_logs
                }, ensure_ascii=False)
            else:
                negotiation_logs.append(f"对方拒绝: {res_dict.get('message')}")
                counter = res_dict.get("counter_proposal", {})
                if counter:
                    new_deadline = counter.get("deadline")
                    negotiation_logs.append(f"对方反提案: 要求 {new_deadline}天")
                    # 自己决定妥协，更新期望时间进入下一轮
                    current_deadline = new_deadline
                    negotiation_logs.append(f"我决定妥协，接受 {current_deadline}天 的底线")
                else:
                    break
        except Exception as e:
            negotiation_logs.append(f"连接 Agent 1 失败: {e}")
            break
            
    return json.dumps({
        "status": "failed",
        "message": "经过多轮协商仍未达成一致",
        "logs": negotiation_logs
    }, ensure_ascii=False)

# ================= 3. 测试 =================

if __name__ == "__main__":
    # 启动服务
    threading.Thread(target=lambda: agent1.run(port=7000), daemon=True).start()
    threading.Thread(target=lambda: agent2.run(port=7001), daemon=True).start()
    
    time.sleep(1.5)
    print("✅ 服务启动成功！")
    print("Agent 1 运行在: http://127.0.0.1:7000")
    print("Agent 2 运行在: http://127.0.0.1:7001")

    # 主控端（用户）只呼叫一次 Agent 2，剩下的全交给 Agent 2 自己去办
    main_client = A2AClient("http://127.0.0.1:7001")
    
    print("\n--- 主控端下达指令给 Agent 2 ---")
    print("指令：去和供应商(Agent 1)谈判，开发新功能，我最多只给 3 天时间。")
    
    # 发送请求
    resp = main_client.execute_skill("negotiate", "negotiate task:开发新功能 deadline:3")
    
    # 打印 Agent 2 的最终返回结果（包含谈判过程和最终结果）
    final_result = json.loads(resp.get('result', '{}'))
    
    print("\n======== 谈判结果报告 (由 Agent 2 汇报) ========")
    for log in final_result.get("logs", []):
        print(f"👉 {log}")
        
    print(f"\n最终结论: {final_result.get('status').upper()}")
    if final_result.get('status') == "success":
        print(f"敲定的交付周期: {final_result.get('final_deadline')} 天")

    print("\n服务保持运行中，按 Ctrl+C 退出...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n服务已停止")