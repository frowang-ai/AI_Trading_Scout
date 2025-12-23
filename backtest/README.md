# 回测模块使用指南 (Backtest Module Guide)

本模块实现了基于“信号分析模式 (Cohort Analysis)”的高效回测系统。

## 1. 快速开始

### 第一步：准备数据
构建回测所需的“宽表” (Wide Table)。这一步会将打分数据与行情数据合并，并预计算未来收益率。

```bash
python backtest/data/builder.py
```
*   输入：`刘丰硕的代码/测试数据xlsx版/*.csv` (打分数据) 和 `data/raw/daily/2025/*.parquet` (行情数据)
*   输出：`backtest/output/wide_table.parquet`

### 第二步：运行回测
运行回测脚本，指定 Top N 和持有天数。

```bash
python backtest/run_backtest.py --top_n 5 --days 1,3,5,10
```

*   **--top_n**: 每日选取得分最高的股票数量 (默认 5)
*   **--days**: 考察的持有天数列表 (默认 1,3,5,10)

### 第三步：查看报告
回测完成后，会在 `backtest/output/` 目录下生成 HTML 报告。
*   例如：`report_Top_5_Score.html`
*   直接用浏览器打开即可查看交互式图表。

## 2. 目录结构

*   `data/`: 数据处理层。`builder.py` 负责清洗和对齐数据。
*   `strategy/`: 策略定义层。`generator.py` 负责根据分数生成买入信号。
*   `engine/`: 回测引擎层。`cohort.py` 负责计算每日信号的后续表现。
*   `analysis/`: 指标计算层。`metrics.py` 计算 IC、胜率等统计指标。
*   `visualization/`: 可视化层。`report.py` 生成 Plotly 图表和 HTML 报告。

## 3. 扩展策略

如果需要实现新的选股逻辑（例如按百分比选股），请修改 `backtest/strategy/generator.py` 中的 `generate` 方法。
