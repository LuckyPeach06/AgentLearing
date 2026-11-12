# myCode —— 学习代码目录

按章节组织:第四章手写底层实现,第七章用框架重写。

## 目录结构

```
base/myCode/
├── ch4/                     # 第四章:手写底层实现
│   ├── core/                # Agent / Config / Message / HelloAgentsLLM
│   ├── react/               # ReAct 范式 + 工具执行器 + SerpApi 搜索
│   ├── reflection/          # Reflection 范式 + Memory
│   └── plan_and_solve/      # Plan-and-Solve 范式(Planner / Executor)
├── ch7/                     # 第七章:框架版实现
│   ├── agents/              # 四大范式的框架重写(my_*_agent.py)
│   ├── common/              # 公共记忆模块 MyMemory
│   ├── llm/                 # 自定义 LLM(ModelScope Provider)
│   ├── tests/               # 四个智能体的测试脚本
│   └── vllm/                # 本地 vLLM 启动脚本 / 接入示例 / 说明
└── README.md
```

## 运行方式

所有脚本都通过 `__file__` 把项目根目录加入 `sys.path`,在任意目录下执行均可;
`.env` 放在项目根目录。

### 第四章:手写版

```bash
.venv-linux/bin/python base/myCode/ch4/react/ReAct.py
.venv-linux/bin/python base/myCode/ch4/reflection/ReflectionAgent.py
.venv-linux/bin/python base/myCode/ch4/plan_and_solve/PlanAndSolveAgent.py
```

### 第七章:框架版测试

```bash
.venv-linux/bin/python base/myCode/ch7/tests/test_simple_agent.py
.venv-linux/bin/python base/myCode/ch7/tests/test_react_agent.py
.venv-linux/bin/python base/myCode/ch7/tests/test_reflection_agent.py
.venv-linux/bin/python base/myCode/ch7/tests/test_plan_solve_agent.py
```

### 本地 vLLM

见 [ch7/vllm/README.md](ch7/vllm/README.md)。
