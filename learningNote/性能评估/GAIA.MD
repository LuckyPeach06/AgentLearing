# GAIA (General AI Assistants)
通用AI助手能力评估

专注于评估 AI 助手的通用能力

与 BFCL 专注于工具调用不同，GAIA 评估的是智能体在真实世界任务中的综合表现。

GAIA 的设计理念是：真实世界的问题往往需要多种能力的综合运用。一个优秀的 AI 助手不仅需要调用工具，还需要：

多步推理：将复杂问题分解为多个子问题
知识运用：利用内置知识和外部知识库
多模态理解：处理文本、图片、文件等多种输入
网页浏览：从互联网获取最新信息
文件操作：读取和处理各种格式的文件

# 准精确匹配算法
核心思想是：先对答案进行归一化处理，然后进行精确匹配


# 评估指标
1. 精确匹配率
精确匹配率是 GAIA 的核心指标，定义为准精确匹配成功的样本比例
2. 分级准确率
对于每个难度级别，计算该级别的准确率
3. 难度递进下降率
衡量智能体在难度增加时的性能衰减
4. 平均推理步骤数
评估智能体完成任务所需的平均步骤数

# 官方系统提示词
GAIA 要求使用特定的系统提示词，确保模型输出符合评估格式:
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].

YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.

If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.

If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.

If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."""

GAIA 对答案格式有严格的要求：答案必须以FINAL ANSWER: [答案]的格式给出；对于数字类型的答案，不使用逗号分隔符和单位符号；对于字符串类型的答案，不使用冠词和缩写；对于列表类型的答案，使用逗号分隔并按字母顺序排列。