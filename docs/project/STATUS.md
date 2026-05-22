# 项目状态

更新时间：2026-05-21

## 当前定位

AI Trading Scout 是一个量化交易与 LLM 投研辅助项目，当前核心方向是把数据抓取、因子与评分、回测、每日生产流水线和 LLM 报告串成可复用流程。

## 已有主模块

- `get_data_tushare/`：Tushare 客户端、CLI、日频抓取和相关测试。
- `data/`：已有 `raw/daily/` 和 `reports/daily/`。
- `core/`：公共指标、Tushare 工具、字段映射、数据集构建和质量分析脚本。
- `cal_factors/`：TA-Lib 技术指标封装。
- `demo/demo1-逆向总分/`：逆向总分建模实验和训练脚本。
- `demo/demo2-抓取行业数据/`：行业/概念数据抓取实验。
- `backtest/`：回测入口、策略、引擎、分析和可视化模块。
- `production/`：每日评分与 LLM 报告生产流水线。
- `LLMClient_v2/`：统一大模型调用和结构化输出客户端。
- `stock_analysis/blue_cursor_300058/`：蓝色光标单票分析工作区。
- `get_data_cls/`：财联社电报线上抓取、数据预览和 Parquet 标准化模块。

## 已有文档

- 根目录 `README.md`：项目总览和主要使用方式。
- `docs/architecture/architecture_design.md`：整体架构。
- `docs/data/data_strategy.md`：数据抓取与存储策略。
- `docs/strategy/factor_calculation_strategy.md`：因子计算策略。
- `docs/architecture/backtest_architecture.md`：回测架构。
- `docs/architecture/daily_production_pipeline.md`：每日生产流水线。
- `docs/data/fetch_data_from_api/`：Tushare 数据抓取、字段字典和质量报告。
- `docs/reference/tushare_api_docs/`：Tushare API 文档本地化结果。
- `docs/data/cls_telegraph_data.md`：财联社电报数据说明。

## 本次文档整理新增

- `docs/README.md`：文档入口和阅读顺序。
- `docs/project/PROJECT_MAP.md`：项目目录地图和模块职责。
- `docs/data/DATA_GOVERNANCE.md`：数据目录、命名、预览、追溯和 Git 策略。
- `docs/project/DEVELOPMENT_WORKFLOW.md`：环境、测试、路径、常用命令和完成标准。
- `docs/project/STATUS.md`：当前状态与后续维护入口。

## 本次目录整理新增

- `data/external/刘丰硕给的潘哥数据/`：从根目录迁入的外部人工 Excel 数据。
- `docs/reference/tushare-data/`：从根目录迁入的 Tushare 资料和示例脚本。
- `docs/project/tracked_files.txt`：从根目录迁入的历史文件清单。
- 移除了根目录空壳 `factor_integration/`。

## 工作区注意点

当前工作区存在较多本次整理前已经出现的未提交变化：

- 大量已跟踪模板、示例输出和 Excel 数据显示为删除。
- `test.py` 已作为本地 LLM 网关临时测试脚本清理。
- 存在未跟踪目录或文件：`.claude/`、`.serena/`、`docs/SHORT_MEMORY/`、`stock_analysis/`、`data/external/`、`docs/reference/tushare-data/`、`docs/project/tracked_files.txt` 等。

后续提交前应先区分哪些是用户已有改动、哪些是本次文档整理改动，不要误回退已有变化。

## 下一步建议

1. 把 `README.md` 中的长篇说明逐步拆到 `docs/` 专题文档，根 README 保持为快速入口。
2. 为 `data/raw/daily/` 和 `data/reports/daily/` 增加自动生成的数据字典与质量检查命令。
3. 把 `docs/SHORT_MEMORY/` 中有长期价值的内容拆成稳定专题文档。
4. 梳理 `production_output/` 和 `backtest/output/` 的产物命名，形成可清理、可复现规则。
5. 对 `stock_analysis/` 建立单票分析模板，便于后续新增股票专题。
