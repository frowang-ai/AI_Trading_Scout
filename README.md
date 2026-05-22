# AI Trading Scout —— 量化交易与 LLM 投研助手

AI Trading Scout 是一个围绕「日常交易与投研工作流」搭建的 Python 项目，用来把：
- 行业与个股数据抓取
- 因子与评分模型
- 回测分析
- 每日收盘后的自动化打分与 LLM 投研报告

这些环节串成一条可重复、可扩展的流水线。

---

## 一、整体架构概览

### 1.1 从直觉出发：我们在解决什么问题？

站在交易员 / 研究员的视角，这个项目想解决的是一件很具体的事：

- 每天收盘之后，**能不能有一条「从数据到结论」的固定流水线**，自动帮你：
  - 抓取并更新行情、行业、概念等原始数据  
  - 计算一套相对稳定的因子与综合得分  
  - 给出全市场排序和重点股票列表  
  - 再用大模型生成一份「像人写的一样」的盘后点评与操作建议  
- 同时又希望这套东西是：
  - **可回测**：你可以用历史数据复盘这套打分逻辑到底有没有用  
  - **可替换**：今天用的是某个打分模型，明天可以换别的因子、别的模型  
  - **可解释**：不只是给一个分数，而是能结合行业、概念、因子给出文字解释  

因此，项目被拆成几层：

1. **数据层**：`get_data_tushare` + `data/`  
   - 把 Tushare（以及后续可能的其他数据源）的数据抓干净、存好。
2. **因子 & 模型层**：`core/`、`cal_factors/`、`demo/demo1-逆向总分`  
   - 在数据的基础上做特征工程、因子构造、模型训练和监控。
3. **回测层**：`backtest/`  
   - 评估「这套打分/因子体系」在历史上到底赚不赚钱。
4. **生产流水线层**：`production/` + `production_output/`  
   - 每天定时跑一遍：更新数据 → 打分 → 生成 Top 列表 → 生成 LLM 报告。
5. **LLM 能力层**：`LLMClient_v2/`  
   - 提供统一的大模型调用接口，把不同厂商/模型屏蔽在内部。

你可以把它理解成一个「可插拔」的日常量化投研框架：  
数据可以换、因子可以换、模型可以换、LLM 也可以换，但整体工作流保持稳定。

### 1.2 从技术视角看目录结构

根目录下比较核心的模块是：

- `get_data_tushare/`：  
  - 与 Tushare 对接的数据抓取模块，包含：
    - `cli.py`：命令行入口，支持历史回补、每日更新、行业/概念数据更新等；
    - `client.py`：面向其他 Python 代码的 Tushare 客户端；
    - `config.py`：统一配置数据根目录、Token 加载逻辑（从 `.env` 读取 `TUSHARE_TOKEN`）；
    - `fetcher_daily.py`：按交易日日粒度批量抓取并缓存数据。
  - 所有原始与加工后的 Tushare 数据会落到 `data/` 目录（例如 `data/raw/daily/`）。

- `core/`：  
  - 一些与数据/因子相关的公共工具与脚本，例如：
    - `tushare_utils.py`：交易日历、代码处理等工具；
    - `indicators.py` / `technical_indicators.md`：技术指标集合与说明；
    - `dataset_builder.py`、`generate_api_field_dict.py` 等数据准备脚本。

- `cal_factors/`：  
  - 使用 TA-Lib 等库计算技术类因子的封装（如 `talib_indicator.py`），  
  - 和后续更丰富的因子计算脚本预留位置。

- `backtest/`：  
  - 一整套回测框架（详见 `backtest/README.md`），包括：
    - `data/`：把评分和行情合成「宽表」；
    - `strategy/`：从评分生成买卖信号；
    - `engine/`、`analysis/`、`visualization/`：回测引擎、统计指标和可视化报告；
    - `run_backtest.py`：回测入口脚本。

- `LLMClient_v2/`：  
  - 通用 LLM 客户端及配置模块，方便在项目中统一调用大模型：
    - `llm_client.py`、`structured_llm_client.py`：同步/结构化调用接口；
    - `llm_config.py`：API 路由与密钥配置（从根目录 `.env` 读取 Yunwu 的 Key）；
    - `models.py`、`token_usage_tracker.py` 等；
    - 子目录 `examples/` 给出使用示例。

- `production/`：  
  - 「每天收盘后的生产流水线」所在的位置，核心文件包括：
    - `daily_runner.py`：Step 1 —— 调用 `get_data_tushare` + 本地模型，对全市场打分并生成 Top 列表；
    - `daily_llm_report.py`：Step 2/3 —— 调用 `LLMClient_v2` 生成每日 LLM 投研报告；
    - `config.py`：生产流程配置（输出目录、Top N、模板路径等）；
    - `history/`：存放历史 Top 列表的 JSON 快照；
    - `templates/`：LLM 报告的模板（如 HTML 模板）；
    - `utils/`：`data_fetcher.py`、`scorer.py`、`llm_analyst.py`、`reporter.py` 等子模块。

- `production_output/`：  
  - 生产流水线的输出目录，例如：
    - `scores_full_YYYYMMDD.csv`：全市场评分结果；
    - `merged_scores_with_excel_YYYYMMDD.csv`：与 Excel 真值合并后的对账表；
    - `llm_reports/`：每日 LLM 分析报告（如 `daily_report_20251218_gpt.md`）。

- `demo/`：  
  - 若干完整的「从数据到结果」的示例项目：
    - `demo1-逆向总分/`：以 Excel/Tushare 为输入，训练和监控一个「逆向总分」模型；
    - `demo2-抓取行业数据/`：围绕行业/概念数据抓取与优化的示例。

- `docs/`：  
  - 更详细的架构与策略设计文档，例如：
    - `architecture/architecture_design.md`：整体架构设计；
    - `architecture/daily_production_pipeline.md`：每日收盘流水线的详细说明；
    - `data/data_strategy.md`、`strategy/factor_calculation_strategy.md` 等。

---

## 二、安装与环境准备

### 2.1 Python 环境

- 推荐 Python 3.11+（当前开发环境为 3.12）。  
- 建议在项目根目录下创建虚拟环境并安装依赖：

```bash
cd AI_Trading_Scout
python -m venv .venv
.venv\Scripts\activate  # Windows
# 或 source .venv/bin/activate  # macOS / Linux

pip install -r requirements.txt
```

（如果你习惯用 `uv`，也可以按自己的习惯用 `uv venv` + `uv pip`，本项目的代码结构与之兼容。）

### 2.2 配置 `.env`

在项目根目录复制 `.env.example` 为 `.env`，并填写实际的 Token / Key：

```env
TUSHARE_TOKEN=your_tushare_token_here

# Yunwu LLM API Keys
YUNWU_ROBUST_GEMINI_API_KEY=your_yunwu_gemini_api_key_here
YUNWU_ROBUST_GPT_API_KEY=your_yunwu_gpt_api_key_here
```

注意：`.env` 已经在 `.gitignore` 中，请不要把真实 Key 提交到 GitHub。

---

## 三、模块使用指南

这一节重点说明「如果别人拿到这个仓库，应该如何使用各个模块」，尤其是：
- 数据获取模块 `get_data_tushare`
- 每日生产流水线模块 `production`
- 示例模块 `demo/`

### 3.1 数据获取模块：`get_data_tushare/`

**核心用途：**  
统一用 Tushare 把日线、基础信息、行业/概念等数据抓取到本地 `data/` 目录，为因子计算、回测和生产流水线提供稳定的数据源。

#### 3.1.1 基本配置

1. 确保 `.env` 中配置了 `TUSHARE_TOKEN`。  
2. 所有数据默认写入：
   - `data/raw/daily/`：按年份拆分的日线/行业等原始数据 Parquet；
   - 其他子目录用于缓存行业、概念、指数等数据（见 `get_data_tushare/config.py`）。

#### 3.1.2 命令行使用

在项目根目录激活虚拟环境后，可直接调用 CLI：

```bash
# 历史回补：从 2020-01-01 起回补 daily 日线
python -m get_data_tushare.cli backfill --start 20200101

# 指定时间段回补
python -m get_data_tushare.cli backfill --start 20230101 --end 20231130

# 回补指定接口（可重复多次使用 --api）
python -m get_data_tushare.cli backfill --start 20240101 --api daily_basic --api adj_factor

# 每日更新（默认更新「昨天」）
python -m get_data_tushare.cli update

# 更新指定交易日
python -m get_data_tushare.cli update --date 20251217

# 更新所有支持的日频接口
python -m get_data_tushare.cli update --all
```

行业/概念数据相关的 CLI 示例：

```bash
# 更新中信行业指数维度表
python -m get_data_tushare.cli update --ci-dim

# 更新原始行业/概念接口快照（推荐先执行一次）
python -m get_data_tushare.cli update --industry-raw

# 基于快照构建「股票-行业-概念」聚合面板
python -m get_data_tushare.cli update --industry-panel

# 一次性更新所有行业/概念相关数据
python -m get_data_tushare.cli update --extras-all
```

配置与下载统计可以通过：

```bash
python -m get_data_tushare.cli info
```

#### 3.1.3 在 Python 代码中使用

如果你希望在自己的脚本里直接重用 Tushare 客户端：

```python
from get_data_tushare.client import TushareClient

client = TushareClient()
df = client.query("stock_basic", exchange="", list_status="L")
```

更多查询示例可以参考：`demo/demo2-抓取行业数据/run_daily_industry_concept_demo.py:1`。

---

### 3.2 每日生产流水线：`production/`

**目标：**  
从「更新完的本地数据」出发，完成：
1. 全市场打分与 Top 列表固化（Step 1）；  
2. 基于 Top 列表 + 历史记录 + 行业/概念信息，生成 LLM 投研报告（Step 2/3）；  
3. 将结果输出到 `production_output/`（CSV/JSON/Markdown/HTML 等）。

#### 3.2.1 前置条件

1. `get_data_tushare` 已经完成历史回补，并且每天通过 `update` 持续更新数据；
2. `.env` 中配置了：
   - `TUSHARE_TOKEN`（用于数据获取）；
   - `YUNWU_ROBUST_GEMINI_API_KEY` / `YUNWU_ROBUST_GPT_API_KEY`（用于 LLM 分析）。
3. 本地已经训练或准备好了评分逻辑（当前版本的打分逻辑主要放在 `production/utils/scorer.py`，也会复用 `demo/demo1-逆向总分` 中的相关能力）。

#### 3.2.2 Step 1：日度打分与 Top 列表

入口脚本：`production/daily_runner.py:1`  

示例用法：

```bash
# 在项目根目录
python production/daily_runner.py --date 20251218 --top-n 50
```

该脚本会：

- 从本地 `data/` 与 Excel 真值（如果存在）加载当日所需数据；
- 计算全市场得分，输出：
  - `production_output/scores_full_YYYYMMDD.csv`：全量评分结果；
  - `production_output/merged_scores_with_excel_YYYYMMDD.csv`：评分 + Excel 真值的对账表（如有真值）；
  - `production/history/top_YYYYMMDD.json`：Top N 股票列表（供后续 LLM 使用）。

#### 3.2.3 Step 2/3：生成每日 LLM 投研报告

入口脚本：`production/daily_llm_report.py:1`

示例用法（推荐使用 `uv run` 或直接 Python）：

```bash
# 基于指定交易日生成 LLM 报告
python -m production.daily_llm_report --date 20251218 --history-window 3
```

要求在此之前已经运行过对应日期的 `daily_runner.py`，并生成：

- `production_output/scores_full_20251218.csv`
- `production/history/top_20251218.json`

脚本会：

- 读取当前和过去若干日（`--history-window`）的 Top 列表；
- 结合行业/概念快照数据，构建 LLM 的上下文；
- 调用 `LLMClient_v2` 中配置的 Yunwu GPT / Gemini 模型生成分析文本；
- 输出到 `production_output/llm_reports/`（例如 `daily_report_20251218_gpt.md`）。

#### 3.2.4 自定义或扩展打分逻辑

- 如果你有自己的因子和评分模型，可以：
  - 在 `production/utils/scorer.py` 中替换或扩展 `calculate_scores` 的实现；
  - 在 `core/`、`cal_factors/` 或 `demo/demo1-逆向总分` 中重用已有特征工程、模型训练代码；
- 扩展后，保持输出的评分表结构不变（至少包含 `ts_code`、`score`），即可无缝接入回测与 LLM 分析。

---

### 3.3 示例模块：`demo/`

`demo/` 目录主要面向「直觉理解」和「快速演示」，帮助你在不深入所有模块的情况下先跑通一个端到端流程。

#### 3.3.1 `demo1-逆向总分/`：逆向总分模型 Demo

**目标：** 用 Excel/Tushare 的历史打分与真值，训练一个「逆向总分」模型，并提供：
- 特征工程与模型接口；
- 每日模型监控与漂移检测；
- 输出日度预测结果。

子目录结构（简要）：

- `src/`：核心 Python 模块：
  - `data_loader.py`：加载各种来源的评分/真值数据；
  - `feature_eng.py`：特征工程（数值标准化、特征挑选等）；
  - `model_engine.py`：模型训练与推理接口；
  - `monitor.py`：日度漂移监控。
- `scripts/`：围绕这些模块构建的可执行脚本：
  - `train_excel_model.py` / `train_tushare_model.py`：训练模型；
  - `daily_monitor.py`：在每日数据上跑模型 + 漂移监控；
  - `aggregate_feature_importance.py`、`eval_rank_and_overlap.py` 等辅助分析脚本。
- `output/`、`output_full/`、`output_excel_only/`：模型文件与结果输出目录。

典型用法示例（在 `demo/demo1-逆向总分/` 下）：

```bash
# 1. 训练模型（示例，具体参数参考脚本内部）
python scripts/train_excel_model.py

# 2. 在指定交易日上跑每日监控 + 预测
python scripts/daily_monitor.py --date 20251218 --model excel_model.pkl
```

训练好的模型与每日预测会写入 `demo/demo1-逆向总分/output/`，  
这些能力在生产流水线中会以更自动化的方式被重用。

#### 3.3.2 `demo2-抓取行业数据/`：行业与概念数据 Demo

**目标：** 演示如何利用 `get_data_tushare` 包装好的客户端，拉取：
- 股票基础信息；
- 行业分类（申万、中信等）；
- 行业/概念成份等。

核心脚本：

- `run_daily_industry_concept_demo.py:1`：
  - 通过 `TushareClient` 顺序调用多个和行业/概念相关的接口；
  - 打印每个接口的形状和前几行，帮助你快速理解字段结构。
- `build_ci_index_dim.py`、`build_daily_merge_ready.py` 等脚本：
  - 基于原始拉取的数据构建更适合分析的维度表或日度合并结果。

典型用法（在项目根目录）：

```bash
python demo/demo2-抓取行业数据/run_daily_industry_concept_demo.py
```

你可以把这里的代码看作是对 `get_data_tushare.client.TushareClient` 的「官方示例」。

---

## 四、如何按自己的需求扩展这个项目？

如果你想在这个项目基础上做自己的东西，可以按下面的顺序来思考：

1. **先把数据跑通**  
   - 用 `get_data_tushare` 把你关心的时间段和品种的数据补全；
   - 确认 `data/` 下面的 Parquet/CSV 结构是你需要的。

2. **选一个 Demo 当模板**  
   - 如果你主要做「个股打分 + Excel 对账」，可以从 `demo/demo1-逆向总分` 入手；
   - 如果你更关心行业/概念轮动，可以从 `demo/demo2-抓取行业数据` 入手。

3. **接入回测**  
   - 把你的评分或信号整理成「宽表」格式，接入 `backtest/`；
   - 用 `run_backtest.py` 检查策略在历史上的表现。

4. **接入每日生产流水线**  
   - 根据自己模型的输出，改造 `production/utils/scorer.py`；
   - 让 `production/daily_runner.py` 的输出结构与你的策略对齐；
   - 复用或调整 `production/daily_llm_report.py` 中的 Prompt 与模板，让 LLM 报告更贴近你的偏好。

5. **随时迭代 LLM 层**  
   - `LLMClient_v2` 支持通过 `llm_config.py` 配置多个 API 与模型；
   - 你可以在 `.env` 中新增 Key，并在 `LLM_STAGE_ROUTING` 中为不同场景选择不同模型（例如「回测总结用小模型、每日投资建议用大模型」）。

---

如果你在阅读或使用过程中遇到任何不清晰的地方，可以优先查看：
- `docs/architecture/architecture_design.md:1` —— 项目整体架构设计  
- `docs/architecture/daily_production_pipeline.md:1` —— 每日生产流水线的详细说明  
- `backtest/README.md:1` —— 回测模块说明  
- `LLMClient_v2/README.md:1` —— LLM 客户端与配置说明  

也欢迎在这些基础上扩展你自己的模块与文档。 
