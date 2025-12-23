# 每日收盘自动化管线 (Daily Closing Pipeline) 架构设计

## 1. 概述

本设计旨在构建一个自动化的每日工作流，用于在收盘后执行以下任务：
1.  **全量数据更新**：获取当天的日线行情与因子数据。
2.  **策略评分**：基于最新数据运行选股模型，生成全市场评分与排名。
3.  **AI 投顾分析**：利用大模型（LLM）对比今日与昨日的优选股列表，生成自然语言的行情解读与操作建议。
4.  **报告交付**：生成面向交易团队的 Excel 执行表和面向决策层的 HTML 分析报告。

## 2. 核心流程 (Pipeline Stages)

```mermaid
graph TD
    subgraph "Stage 1: 数据准备"
        A[CLI Trigger] --> B(调用 get_data_tushare)
        B --> C{数据完整性校验}
    end

    subgraph "Stage 2: 策略计算"
        C -->|Raw Data| D[Scoring Engine]
        D -->|计算因子 & 模型打分| E[全市场评分表]
        E --> F[提取 Top N 股票]
        F -->|JSON/CSV| G[(今日 Top List 持久化)]
    end

    subgraph "Stage 3: AI 投顾分析"
        G --> H[Context Builder]
        I[(昨日 Top List)] --> H
        H -->|Prompt: 变动分析 + 因子解读| J[LLM Client]
        J -->|调用 LLMClient_v2| K[自然语言分析报告]
    end

    subgraph "Stage 4: 交付物生成"
        E --> L[Excel Generator]
        K --> L
        K --> M[HTML Report Generator]
        F --> M
        L -->|Output| N[Actionable Excel (For Traders)]
        M -->|Output| O[Daily Briefing HTML (For Review)]
    end
```

## 3. 详细模块设计

### Stage 1: 数据更新 (Data Ingestion)
*   **功能**：触发每日数据下载。
*   **实现**：直接调用现有的 `get_data_tushare` 模块。
*   **关键点**：
    *   需确保下载完成后进行简单的完整性检查（如：是否包含今日日期的记录）。
    *   支持重试机制。

### Stage 2: 策略计算与评分 (Scoring Engine)
*   **功能**：加载最新数据，计算技术指标，运行打分模型。
*   **输入**：Stage 1 下载的 CSV/Database 数据。
*   **逻辑复用**：
    *   复用 `demo/demo1-逆向总分` 或 `backtest` 中的因子计算与打分逻辑。
*   **输出**：
    *   **Full Score Table**：包含 `ts_code`, `score`, `rank`, 及核心因子列。
    *   **Daily Top List**：筛选出 Top N（如 20 只）股票，保存为轻量级文件（如 `production/history/top_20251218.json`）。

### Stage 3: AI 投顾分析 (LLM Analyst)
*   **功能**：生成“类人”的交易分析报告。
*   **核心依赖**：**`LLMClient_v2`** (位于项目根目录)。
*   **Context 组装策略**：
    1.  **持仓变动分析**：读取 `production/history/` 下的“昨日 Top List”，与“今日 Top List”对比。
        *   *New Entry*：新入榜股票（重点关注买入机会）。
        *   *Drop Out*：落榜股票（重点关注卖出/止盈风险）。
        *   *Stay*：持续霸榜股票（趋势延续）。
    2.  **因子自然语言化**：将 `RSI > 80` 翻译为“超买”，`MA5 > MA20` 翻译为“多头排列”等。
*   **Prompt 设计思路**：
    *   角色：专业交易员/量化分析师。
    *   任务：基于提供的 Top 股票及其因子数据，分析市场风格，并对新入榜股票进行点评。

### Stage 4: 报告生成 (Delivery)
*   **Excel 报告 (面向交易执行)**：
    *   **Sheet 1 (Action Items)**：仅展示 Top 20。包含代码、名称、现价、预测分、**LLM 简评**（如有）、核心因子状态。
    *   **Sheet 2 (Full Market)**：全量数据备份。
*   **HTML 报告 (面向复盘/决策)**：
    *   展示 LLM 生成的完整市场分析文本。
    *   可视化展示 Top 股票的近期走势缩略图（Sparklines）。
    *   高亮显示“新入榜”与“落榜”名单。

## 4. 目录结构规划

建议在项目根目录下新建 `production` 文件夹，保持与研发代码隔离：

```text
production/
├── daily_runner.py          # [入口] 每日执行的主脚本，串联 Stage 1-4
├── config.py                # 生产环境配置 (路径, Top N 设置, 邮件接收人等)
├── history/                 # [状态] 存放每日 Top List 的历史快照
│   ├── top_20251217.json
│   └── top_20251218.json
├── templates/               # [资源] HTML 报告模板 (Jinja2)
│   └── daily_report.html
└── utils/                   # [工具库]
    ├── data_fetcher.py      # 封装 Stage 1 (调用 get_data_tushare)
    ├── scorer.py            # 封装 Stage 2 (调用 core/demo 算法)
    ├── llm_analyst.py       # 封装 Stage 3 (调用 LLMClient_v2)
    └── reporter.py          # 封装 Stage 4 (Excel/HTML 生成)
```

## 5. 实施路线图 (Implementation Plan)

1.  **基础建设 (Infrastructure)**
    *   创建 `production` 目录结构。
    *   编写 `production/config.py`。

2.  **评分引擎封装 (Scorer)**
    *   实现 `production/utils/scorer.py`。
    *   目标：能够读取最新数据，输出带有分数的 DataFrame，并能保存/读取 `history/` 下的 JSON 快照。

3.  **LLM 集成 (Intelligence)**
    *   实现 `production/utils/llm_analyst.py`。
    *   引入 `LLMClient_v2`。
    *   开发 `generate_daily_analysis(current_top, previous_top)` 函数，调试 Prompt 效果。

4.  **报告与串联 (Delivery & Pipeline)**
    *   实现 `production/utils/reporter.py` 生成 Excel/HTML。
    *   编写 `production/daily_runner.py` 将全流程串联。

5.  **测试与部署**
    *   使用历史数据模拟“昨天”和“今天”，验证变动分析逻辑。
    *   设置定时任务（如 Windows Task Scheduler 或 Crontab）每日收盘后执行。
