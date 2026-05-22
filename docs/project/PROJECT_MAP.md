# 项目目录地图

本文档定义项目目录职责，目标是让后续新增数据、实验、因子、回测和生产流程时有稳定落点。

## 顶层主线

AI Trading Scout 的主线是：

```text
Tushare/外部数据 -> data/ -> core/cal_factors/demo -> backtest -> production -> LLM 报告
```

数据、因子、模型、回测、生产日报和 LLM 分析可以独立迭代，但应保持输入输出契约清晰。

## 顶层目录职责

| 目录 | 职责 | 维护规则 |
| --- | --- | --- |
| `get_data_tushare/` | Tushare 数据客户端、CLI、日频抓取和更新逻辑 | 新增接口抓取能力时优先放这里，并补 `_test_*.py` |
| `get_data_cls/` | 财联社电报抓取、预览、清洗和 Parquet 标准化 | 只处理数据源接入；事件提取和复盘逻辑放未来 `event_analysis/` |
| `data/` | 本地数据湖、外部人工数据和数据质量报告 | 原始数据、加工数据、外部导入数据、报告分层存放；大体量数据默认不进 Git |
| `core/` | 公共数据、指标、字段映射和因子辅助脚本 | 放跨模块复用的稳定能力，避免混入一次性实验 |
| `cal_factors/` | 可复用的因子计算封装 | 新因子应保留清晰输入列、输出列和窗口定义 |
| `demo/` | 端到端实验和验证流程 | 允许探索，但成熟能力应迁移到 `core/`、`cal_factors/` 或 `production/` |
| `research/` | 研究驱动工作区，放 proposal、plan、案例诊断、研究代码、结果和笔记 | 每条研究线一个子目录；稳定可复用代码再迁到 `core/`、`event_analysis/` 或 `production/` |
| `backtest/` | 回测框架、策略信号、指标分析和可视化 | 回测输入输出需和生产评分表兼容 |
| `production/` | 每日生产流水线、Top 列表、LLM 报告生成 | 只放可重复运行的生产逻辑，不放临时研究脚本 |
| `production_output/` | 生产流水线输出 | 默认不进 Git；需要沉淀的结论转写到 `docs/` |
| `LLMClient_v2/` | 统一 LLM 调用、结构化输出和 token 统计 | 业务侧不要直接散落调用外部 LLM SDK |
| `stock_analysis/` | 单票专题分析工作区 | 每只股票独立子目录，保留数据说明和测试脚本 |
| `docs/` | 长期文档、架构、数据治理、状态和专题说明 | 新增重要文档后更新 `docs/README.md` |
| `spec/` | 工程规范和编码标准 | 与 `AGENTS.md`、`docs/project/DEVELOPMENT_WORKFLOW.md` 保持一致 |
| `logs/` | 运行日志 | 默认不进 Git，必要结论整理进 `docs/project/STATUS.md` |

## 数据流边界

- 数据抓取：`get_data_tushare/` 负责 API 访问、限流、落盘和更新命令。
- 财联社数据：`get_data_cls/` 负责线上抓取财联社电报、增量合并、full-fields raw 倒序抓取，并生成 `data/processed/cls_telegraph/` 标准表。
- 数据落盘：`data/raw/` 存 API 原始或近原始结果；`data/reports/` 存质量检查报告。
- 外部导入：`data/external/` 存人工提供、供应商导入或一次性外部数据。
- 因子计算：`core/` 和 `cal_factors/` 提供可复用逻辑，实验验证可先放 `demo/`。
- 回测验证：`backtest/` 读取评分、行情和信号，输出回测指标与报告。
- 生产运行：`production/` 串联数据更新、评分、Top 列表、LLM 分析和报告产物。
- 事件分析：未来建议新增 `event_analysis/`，从标准化电报文本中提取事件并构造事件窗口。

## 实验迁移规则

1. 临时验证先放 `demo/` 或具体 `stock_analysis/<topic>/`。
2. 研究 proposal、概念定义、事件案例和阶段性结果先放 `research/<topic>/`。
3. 当逻辑被第二个场景复用时，迁移到 `core/`、`cal_factors/` 或未来 `event_analysis/`。
4. 当逻辑需要每日稳定运行时，迁移到 `production/`。
5. 迁移时必须补 `_test_*.py`，并在 `docs/README.md` 或相关专题文档补入口。

## 单票分析目录约定

`stock_analysis/<stock_slug>/` 用于单只股票的深度分析，建议结构：

```text
stock_analysis/<stock_slug>/
  NOTES.md                  # 人工分析笔记
  DATA_SPEC_for_GPT.md       # 给 LLM 或人工复核的数据字段说明
  land_intraday_data.py      # 数据落地脚本
  calc_indicators.py         # 指标计算脚本
  _test_*.py                 # 预览、落地、指标测试
  data/                      # 单票原始或中间数据
```

成熟后可把通用逻辑迁移回 `core/`、`cal_factors/` 或 `production/`。

## 资料与参考目录

- `docs/reference/tushare_api_docs/`：自动抓取或整理后的 Tushare API 参考文档，体量较大，按需检索。
- `docs/reference/tushare-data/`：Tushare 使用资料、示例脚本和技能参考，不替代正式抓取模块。
- `docs/project/tracked_files.txt`：历史文件清单，用于迁移或盘点时参考，不作为实时状态来源。
