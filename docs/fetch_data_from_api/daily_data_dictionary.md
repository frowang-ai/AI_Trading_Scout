# 日频数据字段字典（daily）

- 数据源目录：`data/raw/daily/YYYY/daily_YYYYMMDD.parquet`
- 主键：`ts_code` + `trade_date`
- 字段列表：
  - `ts_code`：股票代码（字符串），格式如 `000001.SZ`
  - `trade_date`：交易日期（字符串，`YYYYMMDD`）
  - `open`：开盘价（`float64`，元）
  - `high`：最高价（`float64`，元）
  - `low`：最低价（`float64`，元）
  - `close`：收盘价（`float64`，元）
  - `pre_close`：昨收价（`float64`，元）
  - `change`：涨跌额（`float64`，元）
  - `pct_chg`：涨跌幅（`float64`，百分比）
  - `vol`：成交量（`float64`，手）
  - `amount`：成交额（`float64`，千元）

## 字段含义说明

- `pct_chg` 为当日相对 `pre_close` 的百分比变化，通常与 `change` 一致，但受四舍五入影响存在微小差异。
- `vol` 单位为手（100股），如需换算为股数请乘以 100。
- `amount` 单位为千元，如需换算为元请乘以 1000。

## 数据类型与标准化

- 字段类型在落盘前已标准化：数值列使用 `float64`，`ts_code` 与 `trade_date` 使用字符串。
- 统一 Parquet 压缩：`snappy`。

## 质量度量链接

- 缺失率与分布统计见：《日频数据质量报告》：`docs/fetch_data_from_api/daily_quality_report.md`

