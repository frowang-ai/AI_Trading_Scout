# 日频数据质量报告（2024–2025）

- 覆盖范围：`data/raw/daily/2024`、`data/raw/daily/2025`
- 统计口径：按所有 `daily_*.parquet` 文件聚合
- 输出产物：
  - 缺失率汇总：`data/reports/daily/missingness_daily.csv`
  - 数值分布：`data/reports/daily/numeric_stats_daily.csv`
  - 分日记录数：`data/reports/daily/records_by_day.csv`
  - 概览：`data/reports/daily/overview.json`

## 指标说明

- 缺失率：`1 - non_null / total_rows`
- 分布统计：数值列的 `mean`、`std`、`min`、`max`
- 分日记录数：每个交易日的记录条数，观察异常交易日或数据缺口

## 生成方法

- 运行分析脚本：`python core/analyze_daily_quality.py`
- 脚本将生成上述 CSV 与 JSON 文件并写入 `data/reports/daily/`

