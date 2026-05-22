# 回测系统架构设计 (Backtest System Architecture)

## 1. 设计理念 (Design Philosophy)

本回测系统旨在为基于“总分模型”的选股策略提供高效、严谨、可视化的验证工具。核心设计原则如下：

*   **关注点分离 (Separation of Concerns)**：数据准备、策略逻辑、回测引擎、指标计算、可视化展示必须严格解耦。
*   **向量化优先 (Vectorization First)**：利用 Pandas/Numpy 的矩阵运算能力，避免 Python 循环，确保全样本期回测的秒级响应。
*   **信号分析为主 (Cohort Analysis First)**：优先实现基于“每日独立观察”的信号分析模式（Cohort Analysis），以纯粹地衡量选股能力，随后再支持资金账户模拟。
*   **可交互报告 (Interactive Reporting)**：输出独立的 HTML 报告，支持团队协作与深度归因。

---

## 2. 系统模块架构 (Module Architecture)

建议在项目根目录下新建 `backtest/` 模块，内部结构如下：

```text
backtest/
├── data/                 # 数据层：负责数据的加载、清洗、对齐与预计算
│   ├── __init__.py
│   ├── loader.py         # 原始数据加载器 (CSV/DB)
│   ├── builder.py        # 宽表构建器 (WideTableBuilder)
│   └── preprocessor.py   # 预计算逻辑 (未来收益率、移动平均等)
│
├── strategy/             # 策略层：定义“买什么”、“卖什么”
│   ├── __init__.py
│   ├── base.py           # 策略基类 (Abstract Strategy)
│   ├── selector.py       # 选股逻辑 (TopN, Percentile, Threshold)
│   └── generator.py      # 信号生成器 (SignalGenerator)
│
├── engine/               # 引擎层：负责模拟推演
│   ├── __init__.py
│   ├── cohort.py         # 信号分析引擎 (CohortAnalyzer) - 矩阵/表格操作核心
│   └── portfolio.py      # (未来) 账户回测引擎 (PortfolioBacktester)
│
├── analysis/             # 分析层：核心指标计算 (纯数学/统计逻辑)
│   ├── __init__.py
│   ├── metrics.py        # 基础指标 (胜率, 盈亏比, 累计收益)
│   ├── factor_test.py    # 因子检验 (IC, Rank IC, 分组收益)
│   └── attribution.py    # 归因分析
│
├── visualization/        # 可视化层：图表与报告生成
│   ├── __init__.py
│   ├── charts.py         # 绘图组件 (Plotly/Matplotlib 封装)
│   └── report.py         # HTML 报告生成器 (Jinja2/Streamlit)
│
└── run_backtest.py       # 入口脚本
```

---

## 3. 详细模块设计 (Detailed Design)

### 3.1 数据层 (Data Layer)

**核心目标**：构建“回测宽表 (The Wide Table)”。
回测不应在运行时去查原始数据，而应基于一张预先计算好的宽表。

*   **`WideTableBuilder`**:
    *   **输入**：打分结果 CSV（含 `trade_date`, `ts_code`, `total_score`）、日线行情 CSV。
    *   **处理**：
        *   **对齐**：Inner Join 打分表与行情表。
        *   **预计算 (Vectorized Pre-computation)**：利用 `shift(-k)` 批量计算所有样本的 `Future_Return_1d`, `Future_Return_3d`, `Future_Return_5d`, `Future_Return_10d`。
    *   **输出**：一张包含所有回测所需信息的 DataFrame，存为 Parquet 或 Feather 格式（极速读取）。

### 3.2 策略层 (Strategy Layer)

**核心目标**：将业务逻辑抽象为可配置的参数。

*   **`SignalGenerator`**:
    *   接收宽表。
    *   根据配置生成每日的**目标持仓列表 (Target Positions)**。
*   **`Selector` (选股器)**:
    *   **TopNSelector**: 每天选 `total_score` 最高的 N 只。
    *   **PercentileSelector**: 每天选 `total_score` 排名前 X% 的股票。
    *   **ThresholdSelector**: 选 `total_score > X` 的股票。
*   **配置对象 (StrategyConfig)**:
    *   `method`: "top_n"
    *   `n`: 5
    *   `ascending`: False (分数越高越好)

### 3.3 引擎层 (Engine Layer)

**核心目标**：执行回测逻辑，产出原始结果数据。

*   **`CohortAnalyzer` (信号分析模式)**:
    *   **逻辑**：这是“矩阵操作”的核心。它不维护资金账户，而是将每一天视为一个独立的“观察组 (Cohort)”。
    *   **输入**：宽表、策略生成的信号列表、持有天数列表 `[1, 3, 5, 10]`。
    *   **操作**：
        1.  遍历每一个 `trade_date`。
        2.  获取当天的 Target Positions。
        3.  直接从宽表中索引这些股票在 `T+1`...`T+k` 的预计算收益率。
        4.  聚合计算当天的平均收益、中位数收益。
    *   **输出**：`CohortResults` 对象，包含一个多级索引 DataFrame（Date, Hold_Period -> Return, Win_Rate）。

### 3.4 分析层 (Analysis Layer)

**核心目标**：纯粹的数学计算，不涉及绘图。

*   **`MetricsCalculator`**:
    *   `calculate_win_rate(returns_series)`: 计算 > 0 的比例。
    *   `calculate_pl_ratio(returns_series)`: 平均盈利 / 平均亏损。
    *   `calculate_sharpe(returns_series)`: 夏普比率。
*   **`FactorTester`**:
    *   `calculate_ic(ranks, returns)`: 计算每日的 Rank IC (Spearman Correlation)。
    *   `calculate_group_returns(df, groups=5)`: 将股票按分数组分为 5 档，计算每档的平均收益，验证单调性。

### 3.5 可视化层 (Visualization Layer)

**核心目标**：将数据转换为直观的图表和最终报告。

*   **`ChartGenerator`**:
    *   封装 Plotly 代码，生成 `Figure` 对象。
    *   `plot_heatmap(df)`: 绘制“持有天数 vs 日期”的热力图。
    *   `plot_cumulative_returns(df)`: 绘制策略 vs 基准的累计收益曲线。
    *   `plot_ic_decay(df)`: 绘制 IC 随持有天数衰减的柱状图。
*   **`HTMLRenderer`**:
    *   使用 Jinja2 模板或简单的字符串拼接。
    *   将多个 Plotly `Figure` 转换为 HTML `div` 字符串。
    *   组装成完整的 HTML 文件，包含 CSS 样式和交互脚本。

---

## 4. 工作流 (Workflow)

1.  **Data Prep**: 运行 `builder.py` -> 生成 `backtest_wide_table.parquet`。
2.  **Strategy Config**: 用户定义 `config = {top_n: 5, hold_days: [1,3,5]}`。
3.  **Engine Run**: `CohortAnalyzer.run(data, config)` -> 得到 `raw_results`。
4.  **Analysis**: `MetricsCalculator.compute(raw_results)` -> 得到 `metrics_summary`。
5.  **Visualization**: `ReportBuilder.build(raw_results, metrics_summary)` -> 生成 `report.html`。

---

## 5. 扩展性思考 (Scalability)

*   **多策略对比**：架构允许同时运行多个 `StrategyConfig`，并在同一张图中对比它们的表现（例如 Top 5 vs Top 10）。
*   **参数网格搜索**：可以在 `run_backtest.py` 中通过循环遍历参数组合，自动寻找最优参数。
*   **实盘对接**：`Strategy` 层的输出接口应设计为标准的 `List[StockCode]`，未来可直接对接交易执行模块。
