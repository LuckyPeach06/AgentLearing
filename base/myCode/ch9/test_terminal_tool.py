from pathlib import Path

from hello_agents.tools import TerminalTool

# 获取脚本所在目录: .../base/myCode/ch9
SCRIPT_DIR = Path(__file__).parent.absolute()
# 项目根目录，也就是 D:\Work\agentLearning（WSL 里是 /mnt/d/Work/agentLearning）
PROJECT_ROOT = SCRIPT_DIR.parents[0]

# find 要跳过的目录：两个虚拟环境、Git 元数据、教程仓库、缓存
FIND_EXCLUDES = (
    "-path './.venv' -prune -o "
    "-path './.venv-linux' -prune -o "
    "-path './.git' -prune -o "
    "-path './hello-agents' -prune -o "
    "-path './helloagents-framework' -prune -o "
    "-path '*/__pycache__' -prune -o"
)

# grep 要跳过的目录
GREP_EXCLUDES = (
    "--exclude-dir=.venv --exclude-dir=.venv-linux --exclude-dir=.git "
    "--exclude-dir=hello-agents --exclude-dir=helloagents-framework "
    "--exclude-dir=__pycache__"
)

if __name__ == "__main__":
    """演示代码库分析"""
    print("\n" + "=" * 80)
    print("场景4: 代码库分析")
    print("=" * 80 + "\n")

    # workspace 是 TerminalTool 的沙箱根目录，后面的命令都在这里执行
    # 默认超时 30 秒，项目稍大时建议调大
    terminal = TerminalTool(workspace=str(PROJECT_ROOT), timeout=60)

    # 统计代码行数（排除虚拟环境和第三方教程代码）
    print("1. 统计代码行数:")
    result = terminal.run({
        "command": f"find . {FIND_EXCLUDES} -name '*.py' -exec wc -l {{}} + | tail -n 1"
    })
    print(result)

    # 查找所有 TODO 注释
    print("\n2. 查找所有 TODO 注释:")
    result = terminal.run({
        "command": f"grep -rn 'TODO' --include='*.py' {GREP_EXCLUDES} ."
    })
    print(result)

    # 查找特定函数的定义
    print("\n3. 查找特定函数的定义:")
    result = terminal.run({
        "command": f"grep -rn 'def read_note' --include='*.py' {GREP_EXCLUDES} ."
    })
    print(result)
