# Semiconductor 2025-08-08 Case

本模块用于诊断 2025-08-08 前后半导体主题周期。

运行：

```powershell
.\.venv\Scripts\python.exe research\event_driven_vollatility\modules\semiconductor_20250808_case\_test_semiconductor_20250808_probe.py
```

输出：

```text
outputs/_test_semiconductor_news_daily.csv
outputs/_test_semiconductor_basket_daily.csv
outputs/_test_semiconductor_top_stocks.csv
outputs/_test_semiconductor_case_summary.csv
```

第一版只使用本地财联社标准 Parquet 和本地日频行情。等 full-fields raw 抓到 2025-08 后，再补 `subjects` 维度。
