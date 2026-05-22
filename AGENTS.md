Always respond in Chinese-simplified

# 仓库级常驻规则

- 涉及 Python 数据处理、回归、诊断脚本、测试、绘图时，优先使用全局 skill：
  `~/.codex/skills/research-engineering/SKILL.md`
- 路径定位必须基于 `pathlib.Path` 与 `__file__`，禁止依赖 `cwd` 或裸相对路径。
- 默认先写 `_test_*.py` 或最小诊断脚本，再决定是否修改核心代码。
- 遇到巨型文本文件、JSON/JSONL/CSV 等大数据文件时，默认只做头部预览、抽样读取或流式读取；禁止无必要整文件加载到内存或上下文。若确需全量读取，必须先说明理由，并优先采用分块/迭代方案。
- 结果文件、日志、图表、缓存应沿脚本所在目录或其父目录拼接输出。
- 运行环境优先 `uv + venv`；若项目内无可用虚拟环境且 `conda` base 无法运行，再使用：
  `source "F:/global_venv/.venv/bin/activate"`
- 在Windows电脑上使用powershell运行代码时（尤其是Get-Content），要指定 `-Encoding UTF8`

# 项目上下文获取

- 需要项目背景、研究口径、目录映射、近期状态、历史决策时，优先查看
  `docs` 下面的动态文档系统，而不是依赖此文件中硬编码的项目说明。
- 建议优先阅读顺序：
  - `docs/README.md`：文档系统入口
  - `docs/OVERVIEW.md`：项目整体概览
  - `docs/MAP.md`：代码、数据、分析目录映射
  - `docs/project/STATUS.md` 与 `docs/REPO_STATUS.md`：当前进展与仓库状态
  - `docs/DECISIONS.md` 与 `docs/CONVENTIONS.md`：关键决策与约定
  - `docs/RUNBOOK.md`：常见执行流程
  - `docs/GLOSSARY.md`：术语定义
- 如果 live docs 还不够，再按需继续查看：
  - `docs/SHORT_MEMORY/`：近期上下文与临时记忆
  - `docs/archive/`：历史项目日志、索引、旧方案、数据目录说明
  - 相关代码、测试脚本、结果表和日志文件
- 当 live docs、archive 与代码不一致时，优先以当前代码和最新结果为准，并把不一致之处明确指出。
