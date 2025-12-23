# Tushare 股票日频全市场数据获取实施方案（多 API 扩展版）

## 1. 目标与背景

根据《数据获取与存储策略 (Data Strategy)》，我们需要构建一个稳定、高效的数据获取管道，用于维护全市场股票的**日频面板数据**。这一层不仅包括基础日线行情（`daily`），还包括一系列以 `ts_code + trade_date` 为主键、可与日线行情无缝 merge 的多种 Tushare 接口，例如：

- 基础行情：`daily`
- 每日基本面与估值：`daily_basic`
- 复权因子：`adj_factor`
- 涨跌停价格：`stk_limit`
- 个股资金流向：`moneyflow`
- 技术因子：`stk_factor`、`stk_factor_pro`
- 九转指标：`stk_nineturn`
- 竞价/撮合特征：`stk_auction`
- 筹码分布：`cyq_chips`（规划接入）

**核心策略回顾：**
- **获取方式：按日期获取 (Cross-Sectional)**。即每次调用 API 获取某一交易日的全市场所有股票数据，而非按股票代码逐个获取。
- **存储分层：Raw Layer (原始层)**。数据落地为按“年份 + API 名称 + 日期”组织的文件，作为数据湖的基础。
- **持久化格式**：推荐使用 **Parquet**（高性能、压缩比高），但在调试阶段或小规模数据可兼容 CSV。

## 2. 涉及 Tushare API（stock-daily 层）

根据 `docs/tushare_api_docs/` 中的文档，当前规划纳入“股票日频面板层”的接口主要包括：

| 接口名称       | 接口代码         | 描述                             | 典型主键/字段                            | 频率 |
| :------------- | :--------------- | :------------------------------- | :--------------------------------------- | :--- |
| 日线行情       | `daily`          | A 股日线行情（OHLCV 等）        | `ts_code`, `trade_date`, OHLCV           | 日频 |
| 每日基本面     | `daily_basic`    | 每日估值指标与基本面指标        | `ts_code`, `trade_date`, `pe` 等         | 日频 |
| 复权因子       | `adj_factor`     | 每日复权因子                     | `ts_code`, `trade_date`, `adj_factor`    | 日频 |
| 涨跌停价格     | `stk_limit`      | 每日涨跌停价格区间               | `ts_code`, `trade_date`, `up_limit` 等   | 日频 |
| 个股资金流向   | `moneyflow`      | 个股资金流                       | `ts_code`, `trade_date`, 资金流向指标    | 日频 |
| 技术因子       | `stk_factor`     | 技术指标（MACD/KDJ 等）         | `ts_code`, `trade_date`, 技术指标        | 日频 |
| 技术因子 Pro   | `stk_factor_pro` | 扩展技术/量价因子                | `ts_code`, `trade_date`, 因子字段        | 日频 |
| 九转指标       | `stk_nineturn`   | 九转序列（`freq='daily'`）      | `ts_code`, `trade_date`, `freq='daily'`  | 日频 |
| 竞价/撮合特征  | `stk_auction`    | 成交笔数、竞价特征等             | `ts_code`, `trade_date`, 量价指标        | 日频 |
| 筹码分布       | `cyq_chips`      | 每日筹码分布特征（规划接入）     | `ts_code`, `trade_date`, 分布指标        | 日频 |
| 交易日历       | `trade_cal`      | 获取交易日列表（驱动日频循环）   | `exchange`, `cal_date`, `is_open`        | 日频 |

> **关键约束：** 纳入这一层的接口必须满足：  
> 1）以 `ts_code + trade_date`（或加上 `freq='daily'`）为主键；  
> 2）支持按交易日截面拉取；  
> 3）字段可与 `daily` 通过 `merge` 组成统一的股票日频特征面板。


## 3. 模块设计 (`get_data_tushare`)：从单一 `daily` 到多 API

`get_data_tushare/` 模块整体结构保持不变，但从“只支持 `daily`”扩展为“支持任意 stock-daily 结构的 API”：

```text
get_data_tushare/
├── __init__.py
├── config.py            # Tushare Token 配置与常量
├── client.py            # TushareClient 类：封装 API 连接、限流、重试逻辑
├── fetcher_daily.py     # DailyFetcher + 多 API 日频 fetch 入口
└── utils.py             # 日期处理、文件路径生成、多 API 文件命名
```

### 3.1 核心类与工具设计

#### A. TushareClient (client.py)

**职责**：负责与 Tushare 服务器的底层交互，不包含具体业务逻辑。

- 单例模式：确保全局只有一个 API 实例。
- 限流控制：根据积分等级，通过 API_CALL_INTERVAL 控制两次调用间隔。
- 重试机制：对 query(api_name, **kwargs) 统一封装重试与异常包装。

#### B. 路径与断点续传工具 (utils.py)

- get_raw_daily_api_path(api_name, trade_date)
  - 生成通用日频文件路径：
    data/raw/daily/YYYY/{api_name}_YYYYMMDD.parquet
  - 示例：
    - daily → data/raw/daily/2025/daily_20251009.parquet
    - daily_basic → data/raw/daily/2025/daily_basic_20251009.parquet
- get_raw_daily_path(trade_date)
  - 作为基础行情 daily 的薄包装：内部调用 get_raw_daily_api_path("daily", trade_date)，保持向后兼容已有代码与测试。
- filter_existing_dates(dates, ...)
  - 仍用于 daily 的断点续传逻辑。
- filter_existing_dates_for_api(api_name, dates, ...)
  - 用于其他接口（daily_basic、adj_factor 等）的断点续传：检查 {api_name}_YYYYMMDD.parquet 是否存在且文件大小超过阈值。

#### C. DailyFetcher 与多 API 扩展 (fetcher_daily.py)

在保留现有 DailyFetcher（专注 daily 行情）的前提下，增加多 API 日频统一调度能力：

- DailyFetcher（已实现，服务 daily）：
  - fetch_trade_calendar(start, end)：获取交易日历，过滤 is_open=1。
  - fetch_cross_section(date)：调用 client.daily(trade_date=...) 获取指定日期的全市场基础行情。
  - save_to_raw(df, date)：保存至 data/raw/daily/YYYY/daily_YYYYMMDD.parquet。
  - run_initialization(start_date, end_date, skip_existing=True)：daily 历史回补。
  - run_daily_update(trade_date=None)：daily 每日更新。
- 规划中的多 API 入口（统一抽象）：
  - fetch_api_cross_section(api_name, trade_date) -> DataFrame
    - 基于 TushareClient.query(api_name, trade_date=...) 实现，按交易日拉取任意支持的接口截面数据。
  - save_api_to_raw(api_name, df, trade_date)
    - 使用 get_raw_daily_api_path(api_name, trade_date) 落地至 Raw Layer。
  - 高层调度函数（后续实现）：
    - fetch_daily_panels(trade_date: str, apis: Sequence[str] | None = None) -> dict[str, pd.DataFrame]
      - 默认 apis 为一组常用日频接口：["daily", "daily_basic", "adj_factor", ...]。
    - run_backfill_for_apis(start_date: str, end_date: str, apis: Sequence[str]) -> dict[str, dict[str, int]]
      - 对每个接口执行“按交易日循环 + 断点续传”的历史回补，返回每个接口的统计信息。

## 4. 实施步骤与逻辑细节

### 步骤一：环境与配置准备
1.  在 `config.py` 中读取环境变量或配置文件中的 `TUSHARE_TOKEN`。
2.  定义数据存储根目录：`DATA_ROOT = Path("data")`。

### 步骤二：交易日历获取
在开始拉取行情前，必须先知道哪些天是交易日。
*   调用 `pro.trade_cal(exchange='SSE', is_open='1', ...)`。
*   将交易日列表缓存或直接在内存中使用。

### 步骤三：历史数据回补 (Initialization)
这是项目启动时的“一次性”繁重任务。

**逻辑流程：**
1.  设定回补时间段（例如 2010-01-01 至 昨日）。
2.  获取该时间段内所有交易日列表。
3.  **遍历每一个交易日**：
    *   **检查存在性**：构建目标文件路径 `data/raw/daily/{YYYY}/{YYYYMMDD}.parquet`。如果文件已存在且大小正常，**跳过**（断点续传）。
    *   **API 调用**：调用 `pro.daily(trade_date='YYYYMMDD')`。
    *   **数据校验**：检查返回的 DataFrame 是否为空。
    *   **落地存储**：
        *   确保父目录 `data/raw/daily/{YYYY}/` 存在。
        *   使用 `df.to_parquet(path, compression='snappy')` 保存。
    *   **流控休眠**：`time.sleep(0.3)` (根据积分情况调整，避免触发 QPS 限制)。
    *   **日志记录**：打印进度条或日志，如 `[2023-11-01] Fetched 5100 rows. Saved.`。

### 步骤四：每日增量更新 (Daily Update)
这是部署后的常态化任务。

**逻辑流程：**
1.  获取当前日期 `today`。
2.  检查 `today` 是否为交易日，且当前时间是否已过收盘时间（如 17:00 后）。
3.  执行与“历史数据回补”相同的 `fetch -> validate -> save` 逻辑。

## 5. 数据存储规范 (Schema)

严格遵循《工程实践规范》中的路径与格式要求。

### 5.1 文件路径模板

- 通用命名规则（多 API）：

```python
    # 使用 pathlib
    year = date_str[:4]
    file_path = DATA_ROOT / "raw" / "daily" / year / f"{api_name}_{date_str}.parquet"
    # 示例:
    #   daily:       data/raw/daily/2025/daily_20251009.parquet
    #   daily_basic: data/raw/daily/2025/daily_basic_20251009.parquet
    
```
- 兼容旧接口的 daily 封装：

```python
# 内部等价于 get_raw_daily_api_path("daily", trade_date)
file_path = DATA_ROOT / "raw" / "daily" / year / f"daily_{date_str}.parquet"
```

### 5.2 数据格式 (Parquet)

- 保留 Tushare 原始字段名（ts_code, trade_date, open, high, low, close, vol, amount 等）。
- 数据类型建议在保存前做轻度标准化（按接口分别处理）：
  - ts_code, trade_date: 字符串类型。
  - OHLCV 与金额类字段：float 类型。
  - 对于 daily_basic、moneyflow、stk_factor 等，可按各接口文档对关键列做类型校准，但不强行删除或重命名字段，确保 Raw Layer 最大程度保留原始信息。

## 6. 异常处理策略

1.  **网络异常**：
    *   捕获 `requests.exceptions.RequestException`。
    *   实施指数退避重试（Exponential Backoff），如等待 1s, 2s, 4s 后重试。
    *   重试 3 次失败后，记录 ERROR 日志并跳过该日期（或抛出异常终止，视策略而定）。

2.  **数据为空**：
    *   如果 API 返回空 DataFrame，可能是该日休市（但日历显示开市）或 Tushare 数据未更新。
    *   记录 WARNING 日志：`[Date] Empty data returned.`，不生成空文件，以便下次重试。

3.  **权限/积分不足**：
    *   捕获 Tushare 特定异常信息。
    *   记录 CRITICAL 日志并停止程序。

## 7. 代码开发计划 (Todo)

- [ ] 创建 `get_data_tushare/config.py` 并配置 Token。
- [ ] 实现 `get_data_tushare/client.py` (基础 API 封装)。
- [ ] 实现 `get_data_tushare/fetcher_daily.py` (核心逻辑)。
- [ ] 编写单元测试 `_test_fetch_daily.py` (Mock API 返回，测试文件保存逻辑)。
- [ ] 运行历史回补脚本，建立基础数据库。
