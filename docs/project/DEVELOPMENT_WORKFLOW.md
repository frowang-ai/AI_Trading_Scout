# 开发工作流

本文档补充 `AGENTS.md` 和 `spec/coding_standards.md`，用于日常开发、测试和文档维护。

## 环境

项目要求 Python 3.12+。Windows 上优先使用 `uv + venv`：

```powershell
uv --version
uv venv --python 3.12
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

后续运行脚本时优先直接使用虚拟环境里的 Python：

```powershell
.\.venv\Scripts\python.exe -m get_data_tushare.cli info
```

## 配置

根目录 `.env` 存放本地密钥，不提交到 Git。至少包括：

```env
TUSHARE_TOKEN=your_tushare_token_here
YUNWU_ROBUST_GEMINI_API_KEY=your_key_here
YUNWU_ROBUST_GPT_API_KEY=your_key_here
```

`.env.example` 用于维护变量名和说明，不写真实密钥。

## 测试先行

- 新增或修改核心逻辑前，优先创建 `_test_<模块或能力>.py`。
- 测试文件优先放在被测模块同级目录。
- 数据读取、接口契约、字段变化、输出结构都应先用 `_test_*.py` 固化。
- 如果测试脚本产生文件，输出文件也使用 `_test_` 前缀。

示例：

```powershell
.\.venv\Scripts\python.exe get_data_tushare\_test_fetch_daily.py
.\.venv\Scripts\python.exe production\utils\_test_step1_scorer.py
```

## 路径与 I/O

Python 代码统一使用：

```python
from pathlib import Path

current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()
```

禁止直接依赖 `os.getcwd()` 或裸相对路径来定位项目资源。读写文本默认 `encoding="utf-8"`，捕获 I/O 异常并给出明确路径。

## 常用命令

查看 Tushare 抓取配置：

```powershell
.\.venv\Scripts\python.exe -m get_data_tushare.cli info
```

按日期更新数据：

```powershell
.\.venv\Scripts\python.exe -m get_data_tushare.cli update --date 20251217
```

运行每日评分：

```powershell
.\.venv\Scripts\python.exe production\daily_runner.py --date 20251218 --top-n 50
```

生成每日 LLM 报告：

```powershell
.\.venv\Scripts\python.exe -m production.daily_llm_report --date 20251218 --history-window 3
```

运行回测入口：

```powershell
.\.venv\Scripts\python.exe backtest\run_backtest.py
```

## 文档更新

以下情况需要同步更新文档：

- 新增顶层目录或改变目录职责：更新 `docs/project/PROJECT_MAP.md`。
- 新增数据源、数据层或字段契约：更新 `docs/data/DATA_GOVERNANCE.md` 或 `docs/data/fetch_data_from_api/`。
- 改变生产流水线步骤：更新 `docs/architecture/daily_production_pipeline.md`。
- 改变回测输入输出：更新 `docs/architecture/backtest_architecture.md` 或 `backtest/README.md`。
- 阶段性完成、遗留问题或风险：更新 `docs/project/STATUS.md`。

## 完成标准

一次代码任务完成前至少检查：

- 相关 `_test_*.py` 已运行或说明无法运行的原因。
- 没有把密钥、日志、大数据、生产输出误提交。
- 路径定位符合 `pathlib + __file__` 约定。
- 新能力有入口说明或文档索引。
- `git status --short` 中只包含本次任务预期改动，既有用户改动不被回退。
