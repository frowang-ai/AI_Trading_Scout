# 盘中实时行情抓取

当前模块直接读取东方财富网页使用的公开行情端点，不依赖 Tushare Token：

- `stock/get`：最新价、当日累计成交量/额，以及服务端可用时的买卖五档；
- `trends2/get`：当日 1 分钟分时行情；
- `details/get`：最近分笔成交聚合。

这些是未公开承诺稳定性的网页接口，不是交易所授权行情 SDK。调用失败、字段被省略或延迟时会显式报错/标记，不会静默切换数据源。

术语约定：`details/get` 与 `details/sse` 属于约 3 秒粒度的分笔成交聚合（tick-like），不是“一笔成交一条记录”的严格 Tick。`trends2/get` 和 Tushare `stk_mins` 属于一分钟 OHLCV K 线。完整分层见 [A 股日内行情粒度与术语](../docs/data/intraday_data_levels.md)。

## 已验证的数据语义

2026-08-13 午休时对蓝色光标 `300058.SZ` 实测：

- 分时接口返回 121 根，覆盖 `09:30–11:30`；
- 分笔接口可返回到 `11:30:00`，所以旧 `f1.html` 页面空白不代表接口无数据；
- 分笔字符串依次为 `时间,成交价,成交量(手),成交笔数,方向代码`；它是约 3 秒一条的成交聚合，不是逐笔委托流水；
- 基础行情能返回最新价等字段，但午休时服务端省略五档字段，客户端返回 `order_book_available=false`，不把缺失盘口伪装成零挂单。
- 下午盘双通道实测中，`details/sse` 成功保持 `text/event-stream` 长连接：首帧 `full=1` 返回最近记录，后续 `full=0` 发送增量批次。成交记录时间粒度约 3 秒，但网络帧通常约 6～7 秒发送一次、每帧含 2～3 条。
- 同时运行的 `stock/get` 轮询按绝对 3 秒节拍发起，请求间隔实测约 `3.016s / 2.994s / 2.996s`，未被 SSE 阻塞。不过下午连续竞价时响应仍省略五档字段，说明当前公开响应的五档缺失并非午休特例。
- SSE 事件没有 `id`，浏览器的 `lastEventId` 为空，不能依赖标准 SSE 的 `Last-Event-ID` 自动回补；生产化仍需要断线后用 `details/get` 拉取窗口并去重补偿。

分时字符串字段依次为：

```text
时间,开盘,收盘,最高,最低,成交量(手),成交额(元),均价
```

## 使用方式

```powershell
# 当前快照
.\.venv\Scripts\python.exe -m realtime_alert.cli quote 300058.SZ

# 当日分钟线
.\.venv\Scripts\python.exe -m realtime_alert.cli minutes 300058.SZ

# 最近 20 条分笔聚合
.\.venv\Scripts\python.exe -m realtime_alert.cli trades 300058.SZ --limit 20

# 每 3 秒记录一次快照
.\.venv\Scripts\python.exe -m realtime_alert.cli watch 300058.SZ --interval 3

# 离线契约测试
.\.venv\Scripts\python.exe -m realtime_alert._test_eastmoney

# 限时双通道实测：SSE 成交 + 每 3 秒快照
.\.venv\Scripts\python.exe -m realtime_alert._test_eastmoney_sse_monitor `
  --symbol 300058.SZ --duration 20 --quote-interval 3
```

`watch` 的 JSONL 输出基于脚本目录定位：

```text
realtime_alert/data/<YYYYMMDD>/<symbol>_quotes.jsonl
```

五档 HAR 采集步骤、SSE 断线风险和重连回补设计见 [HAR_AND_SSE_RECOVERY_PLAN.md](HAR_AND_SSE_RECOVERY_PLAN.md)。

多股票正式采集器的异步架构、容量估算、写盘策略和阶梯验收标准见 [SSE_ENGINEERING_DESIGN.md](SSE_ENGINEERING_DESIGN.md)。本机 CPU/缓冲写盘容量诊断可运行：

```powershell
.\.venv\Scripts\python.exe -m realtime_alert._test_sse_capacity `
  --records 100000 --flush-every 100
```

## 100 股票正式采集器

准备本地股票池：

```powershell
Copy-Item .\realtime_alert\symbols.example.txt .\realtime_alert\symbols.txt
```

编辑后启动；股票池严格限制为100只：

```powershell
.\.venv\Scripts\python.exe -m realtime_alert.collector `
  --symbols-file symbols.txt --market-hours
```

诊断运行可增加 `--duration 60 --metrics-interval 10`。默认写入 `realtime_alert/data/YYYYMMDD/`，包含成交、快照、连接审计与资源指标。收盘后汇总：

```powershell
.\.venv\Scripts\python.exe -m realtime_alert.summarize_run data/YYYYMMDD
```

Linux systemd 部署、服务器短测与首日验收见 [DEPLOYMENT.md](DEPLOYMENT.md)。

当前正式测试股票池采用 `2026-08-13 daily_basic.total_mv`：先剔除截至截面日上市不足3个自然月的沪深 A 股，再按总市值取前99只，最后加入蓝色光标。运行文件为被 Git 忽略的 `symbols.txt`，可部署版本保存在 `watchlists/symbols_market_cap_top99_plus_blue_cursor_20260813.txt`。重新生成：

```powershell
.\.venv\Scripts\python.exe -m realtime_alert.build_market_cap_watchlist
```

## 边界

- 五档是当前档位汇总，不包含委托编号、排队顺序、撤单事件或完整订单流。
- 分笔成交是网页展示口径的聚合记录，不能当成交易所 Level-2 逐笔成交。
- HTTP 轮询无法保证不遗漏中间快照；正式“不漏数”要求带序号与回补能力的授权行情流。
- 公开端点可能限流、断连、变更参数或省略字段，生产提醒必须记录请求失败和数据源时间。
