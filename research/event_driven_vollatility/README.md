# Event Driven Volatility Research

本目录承接“事件归因 + 主题周期识别 + 弱预测信号”研究线。当前目录名沿用已创建路径 `event_driven_vollatility`，后续如果需要修正拼写，可整体迁移到 `event_driven_volatility`。

## 目录职责

```text
ideas/        proposal、概念定义、研究计划、失败条件和案例设计
notes/        文献、数据理解、案例复盘、方法取舍和阶段性判断
modules/      可执行诊断脚本、研究管线、outputs 和 logs
data/         研究专属小型中间表或字典；大数据仍优先放项目 data/
manuscripts/  面向论文、报告或产品文档的正式写作
repos/        外部参考仓库或材料，默认只读
```

## 当前第一阶段

先不急着上复杂模型，优先做典型案例 sanity check。第一例是 2025-08-08 前后半导体主题启动，到 2025-10-10 附近的主题周期形状：

1. 用不带 `subjects` 的财联社标准表检索半导体相关新闻密度。
2. 用本地日频行情构造半导体股票篮子表现。
3. 检查 ETF、板块、个股三类价格形状是否一致。
4. 等 full-fields raw 抓到 2025 年后，再补 `subjects` 维度。

## 研究边界

- `get_data_cls/` 只负责财联社数据获取和标准化。
- 本目录负责研究设计、诊断脚本和结果沉淀。
- 稳定可复用的事件抽取、事件窗口、暴露度计算代码，成熟后迁到未来 `event_analysis/` 或 `core/`。
