# AI Trading Scout 文档入口

这个目录用于沉淀项目的长期知识：架构、数据、生产流程、回测、开发约定和阶段状态。后续新增功能或数据时，优先更新这里的索引和对应专题文档，避免知识只散落在代码、聊天记录或临时脚本里。

## 推荐阅读顺序

1. [project/PROJECT_MAP.md](project/PROJECT_MAP.md)：先看项目目录职责和模块边界。
2. [project/STATUS.md](project/STATUS.md)：了解当前已经有什么、哪些还在建设中、工作区有哪些注意点。
3. [data/DATA_GOVERNANCE.md](data/DATA_GOVERNANCE.md)：新增数据、数据报告、临时分析产物时先看这里。
4. [project/DEVELOPMENT_WORKFLOW.md](project/DEVELOPMENT_WORKFLOW.md)：写代码、跑测试、配置环境、提交前检查的统一流程。
5. [architecture/architecture_design.md](architecture/architecture_design.md)：整体平台架构设计。
6. [data/data_strategy.md](data/data_strategy.md)：Tushare 数据抓取与本地存储策略。
7. [strategy/factor_calculation_strategy.md](strategy/factor_calculation_strategy.md)：因子计算策略。
8. [architecture/backtest_architecture.md](architecture/backtest_architecture.md)：回测框架设计。
9. [architecture/daily_production_pipeline.md](architecture/daily_production_pipeline.md)：每日收盘生产流水线。

## 专题文档分区

- `project/`：项目地图、状态、开发流程和维护规则。
- `architecture/`：系统架构、回测架构、生产流水线等设计文档。
- `data/`：数据治理、数据策略、API 抓取方案、字段字典和质量报告。
- `strategy/`：交易直觉、因子设计、策略逻辑和假设说明。
- `reference/`：外部资料和自动抓取的大体量参考文档。
- `SHORT_MEMORY/`：历史长上下文或阶段性笔记，适合迁移成更稳定的专题文档后再长期依赖。

## 文档维护规则

- 入口索引放在 `docs/README.md`，不要让新文档变成孤岛。
- 架构级决策写入 `architecture/`；阶段状态写入 `project/STATUS.md`。
- 数据落点、命名、版本化规则写入 `data/DATA_GOVERNANCE.md`。
- 代码规范、测试策略、运行命令写入 `project/DEVELOPMENT_WORKFLOW.md` 或 `spec/coding_standards.md`。
- 自动生成的大体量 API 文档和数据报告应标明来源和生成方式，不要混入人工结论。

## 当前重点数据文档

- [data/cls_telegraph_data.md](data/cls_telegraph_data.md)：财联社电报数据、Parquet 标准表和事件分析入口说明。
- [data/cls_telegraph_full_fields_schema.md](data/cls_telegraph_full_fields_schema.md)：财联社 full-fields JSONL 原始字段结构、`subjects` 关系和解析建议。
