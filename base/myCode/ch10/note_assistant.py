"""
多Agent协作的智能文档助手

使用两个SimpleAgent分工协作：
- Agent1：GitHub搜索专家
- Agent2：文档生成专家
"""

from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.tools import MCPTool


load_dotenv()

"""
    github 搜索Agent
"""
github_agent = SimpleAgent(
    name="Github搜索专家",
    llm=HelloAgentsLLM(),
    system_prompt="""你是一个GitHub搜索专家。
你的任务是搜索GitHub仓库并返回结果。
请返回清晰、结构化的搜索结果，包括：
- 仓库名称
- 简短描述

保持简洁，不要添加额外的解释。"""
)

github_tool = MCPTool(
    name="search_repositories",
    server_command=["npx", "-y", "@modelcontextprotocol/server-github"]
)

github_agent.add_tool(github_tool)

"""
    文档生成Agent
"""
file_generate_agent = SimpleAgent(
    name="文档生成专家",
    llm=HelloAgentsLLM(),
    system_prompt="""你是一个文档生成专家。
你的任务是根据提供的信息生成结构化的Markdown报告。

报告应该包括：
- 标题
- 简介
- 主要内容（分点列出，包括项目名称、描述等）
- 总结

请直接输出完整的Markdown格式报告内容，不要使用工具保存。"""
)

fs_tool = MCPTool(
    name="fs",
    server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]
)
file_generate_agent.add_tool(fs_tool)



try:
    # 搜索github
    search_task = "搜索关于'Java Spring'的GitHub仓库，返回前5个最相关的结果"
    search_results = github_agent.run(search_task)
    print(search_results)

    # 生成文档
    report_task = f"""
根据以下GitHub搜索结果，生成一份Markdown格式的研究报告：

{search_results}

报告要求：
1. 标题：# Java Spring研究报告
2. 简介：说明这是关于Java Spring的GitHub项目调研
3. 主要发现：列出找到的项目及其特点（包括名称、描述等）
4. 总结：总结这些项目的共同特点

请直接输出完整的Markdown格式报告。
"""

    report_content = file_generate_agent.run(report_task)
    print(report_content)

    import os
    try:
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        print("已保存到 report.md")

        # 验证文件
        file_size = os.path.getsize("report.md")
        print(f"文件大小: {file_size} 字节")
    except Exception as e:
        print(f"保存失败: {e}")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()