# 日频数据概览与字段对照索引

- 数据来源：`get_data_tushare/fetcher_daily.py` 拉取并落盘至 `data/raw/daily/YYYY/{api_name}_YYYYMMDD.parquet`
- 统计产物位置：
  - 概览 JSON：`docs/fetch_data_from_api/generated/apis_overview.json`
  - 接口字段对照：`docs/fetch_data_from_api/generated/{api}_fields_vs_official.md`
  - 质量报告（daily）：`data/reports/daily/*`

## 接口列表（已覆盖）

- `daily`：基础行情（字段字典见 `docs/fetch_data_from_api/daily_data_dictionary.md`）
- `daily_basic`：每日指标
- `adj_factor`：复权因子
- `stk_limit`：涨跌停价格
- `moneyflow`：个股资金流向
- `stk_factor`：技术因子
- `stk_factor_pro`：技术因子（扩展）
- `stk_nineturn`：神奇九转
- `stk_auction`：集合竞价

## 重建方法

- 生成质量报告：`python -m core.analyze_daily_quality`
- 生成字段对照与概览：`python -m core.generate_api_field_dict`

