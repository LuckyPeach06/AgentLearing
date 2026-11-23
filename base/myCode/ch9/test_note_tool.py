from hello_agents.tools import NoteTool

notes = NoteTool(workspace="./project_notes")

note_id = notes.run({
    "action": "create",
    "title": "Agent项目 - 第一阶段",
    "content": """## 完成情况
已完成范式学习，学习进度：15%。

## 下一步
学习记忆与检索""",
    "note_type": "task_state",
    "tags": ["agentlearning", "phase1"]
})

print(f"✅ 笔记创建成功,ID: {note_id}")