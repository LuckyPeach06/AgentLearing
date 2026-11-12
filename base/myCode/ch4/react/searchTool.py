
from serpapi import SerpApiClient

"""
    基于SerpApi的网页搜索工具
    可以智能的解析搜索结果，优先返回直接答案或者知识图谱
"""
import os

def search(query: str) -> str:
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Error: .env配置文件中未配置SERPAPI_API_KEY"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 国家代码
            "hl": "zh-cn", # 语言代码
            # "gl": "us",  # 国家代码
            # "hl": "en", # 语言代码
        }

        client = SerpApiClient(params)
        results = client.get_dict()

        # 优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"调用SerpApi失败，错误信息：{e}"
