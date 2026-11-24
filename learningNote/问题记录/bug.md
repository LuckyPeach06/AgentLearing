1、在调用谷歌搜索引擎时，搜索“英伟达最新GPU型号”，发现搜索结果是旧新闻数据

排查过程中，将模糊查询换为精确查询“NVIDIA RTX 50系列 发布时间”，显示结果正常，证明搜索引擎没有问题，怀疑是提示词或者地区的问题，将地区从gl=cn, hl=zh-cn更改为gl=us, hl=en之后，再次搜索“英伟达最新GPU型号”，结果为最新的50系列，查询结果正确。

所以是中文在谷歌搜索引擎下，新闻的时效性弱于英文，被地区化过滤，“最新”命中了旧文章的标题，导致出现幻觉

2、在Reflection教程代码运行中，发现：第 3 轮的走向:评审明明说"不宜直接判定为无需改进"，但程序却打印了"反思认为代码已无需改进,任务完成",提前收工了

检查发现，原因是停止条件这行代码:
if "无需改进" in feedback:
评审的否定句"不宜直接判定为'无需改进'"里恰好包含"无需改进"四个字,子串匹配出了问题。

修复：
在 REFLECT 提示词末尾加一句:"请在输出的最后一行单独给出结论,格式严格为:结论:需要改进 或 结论:无需改进"
停止判断改为:if feedback.strip().endswith("无需改进"):(或匹配最后一行)



# ch10中itgt_customer_service.py执行时，报错：未安装a2a-sdk
执行pip install a2a-sdk

再次运行，依旧提示未安装

怀疑是版本兼容问题，问了AI，AI说：
    我装的a2a-sdk 1.3.1，1.x 是新 API，这里把 A2AClient 从 a2a.client 里移走了，可以尝试安装0.x版本

重新安装0.3.26版本：pip install a2a-sdk==0.3.26

重新运行，依旧报错。

没有排查出来，继续问AI：
    结论是：工具参数名问题
    装好后脚本能跑，但专家转接仍然失败。抓到的实际调用参数是：
    {'input': '请问你们的API如何调用？'}
    {'action': '回答客户咨询', 'question': '...'}
    {'action': 'query', 'question': '...'}

    A2ATool 只认 action="ask" 和 action="get_info"，模型却自由发挥成了 query、input、回答客户咨询。这是 SimpleAgent 文本约定式工具调用的通病。

    在 hello_agents/tools/builtin/protocol_tools.py 里加兼容层：
    question = parameters.get("question") or parameters.get("query") or parameters.get("input")
    if action not in ("ask", "get_info") and question:
        action = "ask"

执行正常

# agent性能评估中，测试GAIA时，数据集加载失败
原因：
    GAIA 数据集在 HuggingFace 上已经改成 parquet 格式：
    data/gaia/2023/validation/metadata.parquet

    但 hello-agents 的 GAIADataset 只找：
    data/gaia/2023/validation/metadata.jsonl

    找不到就返回 0 条样本，所以评估失败。

解决：
    给 GAIADataset 加了 parquet 支持：
        本地加载时，如果没有 JSON，就读取 metadata*.parquet
        HuggingFace 下载后如果没有 metadata.jsonl，同样回退到 parquet
        把 parquet 里的 Level 字符串转成整数，否则按 level=1 过滤会得到 0 条