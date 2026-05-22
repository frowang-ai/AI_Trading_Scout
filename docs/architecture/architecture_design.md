# AI Trading Scout 平台架构设计文档

## 1. 项目概述
本项目旨在构建一个基于 Python 的现代化量化交易平台，集数据获取、因子计算、策略整合、交易执行与可视化分析于一体。平台采用模块化设计，强调高内聚低耦合，以支持灵活的策略扩展与数据分析。

## 2. 核心模块架构 (Core Modules)

### 2.1 数据获取模块 (`get_data_tushare`)
**职责**：负责与 Tushare 数据源交互，提供标准化的数据获取接口。
**设计要点**：
- **基础数据**：股票列表、交易日历。
- **量价数据**：日/周/月线行情（开盘、收盘、最高、最低、成交量）、复权因子。
- **基本面数据**：财务报表（资产负债表、利润表、现金流量表）、财务指标。
- **接口设计**：封装 Tushare API，提供统一的 `Fetcher` 类或函数，处理网络异常与限流。

### 2.2 因子计算模块 (`cal_factors`)
**职责**：基于原始数据计算各类量化因子。
**子模块划分**：
- **技术指标 (Technical Indicators)**：
  - 趋势类：均线 (MA, EMA), MACD, 布林带 (Bollinger Bands)。
  - 震荡类：KDJ, RSI, CCI。
- **基本面指标 (Fundamental Indicators)**：
  - 偿债能力：流动比率 (Current Ratio), 速动比率 (Quick Ratio)。
  - 盈利能力：ROE, ROA, 净利率。
  - 估值指标：PE, PB, PS。
- **学术/Alpha 指标 (Academic/Alpha Factors)**：
  - 动量 (Momentum), 反转 (Reversal)。
  - 波动率 (Volatility), 换手率因子。
**设计模式**：采用策略模式或工厂模式管理不同类型的因子计算逻辑，确保新增因子不影响现有代码。

### 2.3 数据存储模块 (`data`)
**职责**：数据的持久化存储与管理。
**策略**：
- **本地文件**：CSV/Parquet 格式，用于离线分析与回测（推荐 Parquet 以提高读写性能）。
- **数据库**：未来可扩展支持 SQLite/MySQL/ClickHouse。
- **目录结构**：按数据类型（如 `raw`, `processed`, `factors`）分层存储。

## 3. 扩展模块规划 (Future Modules)

### 3.1 因子整合模块 (`factor_integration`)
**职责**：对计算出的单因子进行合成与优化。
**功能**：
- **多因子合成**：使用等权、IC 加权或机器学习模型（如 XGBoost, LightGBM, 神经网络）组合因子。
- **因子分析**：IC/IR 分析、因子相关性检验。

### 3.2 交易执行模块 (`trade_execution`)
**职责**：策略信号生成与模拟/实盘交易。
**功能**：
- **信号生成**：基于整合后的因子生成买入/卖出信号。
- **回测引擎**：模拟历史交易，评估策略表现（夏普比率、最大回撤）。
- **实盘接口**：对接券商 API 进行下单（需考虑风控与滑点）。

### 3.3 可视化模块 (`visualization`)
**职责**：数据与策略表现的前端展示。
**技术栈**：Streamlit / Dash / Vue + ECharts。
**功能**：
- K 线图叠加技术指标。
- 因子分布与相关性热力图。
- 策略回测净值曲线与风险指标仪表盘。

## 4. 文档与规范 (`docs` & `spec`)

- **`docs/`**：存放项目总体策略、架构图、算法说明笔记、Tushare 数据字典笔记。
- **`spec/`**：存放编码规范、开发指南、依赖版本说明（详见 `spec/coding_standards.md`）。

## 5. 目录结构示意

```text
AI_Trading_Scout/
├── get_data_tushare/     # 数据获取
├── cal_factors/          # 因子计算
├── data/                 # 数据存储 (本地持久化)
├── factor_integration/   # 因子整合 (ML/合成)
├── trade_execution/      # 交易执行与回测
├── visualization/        # 可视化前端
├── docs/                 # 项目文档
└── spec/                 # 开发规范
```
