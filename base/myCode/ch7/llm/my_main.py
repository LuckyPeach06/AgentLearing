from pathlib import Path
import sys

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from base.myCode.ch7.llm.my_llm import MyLLM


load_dotenv()

llm = MyLLM(provider="modelscope")

messages = [
    {
        "role" : "user",
        "content": "你好，请介绍一下你自己。"
    }
]

response = llm.think(messages)

print("ModelScope Response:")