# 100 股票 SSE 采集器部署与首日验收

## 一、部署前准备

要求：

- Linux 服务器时间和时区正确，建议设置为 `Asia/Shanghai`；
- Python 3.11 或 3.12；
- 服务器能够直接访问 `push2.eastmoney.com` 和 `81.push2.eastmoney.com`；
- 进程打开文件数上限大于 1024；
- 为首日数据至少预留 2 GiB 空间。

安装：

```bash
cd /opt/AI_Trading_Scout
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp realtime_alert/watchlists/symbols_market_cap_top99_plus_blue_cursor_20260813.txt \
  realtime_alert/symbols.txt
```

编辑 `realtime_alert/symbols.txt`，每行一只股票。程序会规范化代码、去重，并严格拒绝超过 100 只的清单。

## 二、上线前短测

先跑离线测试：

```bash
.venv/bin/python -m realtime_alert._test_eastmoney
.venv/bin/python -m realtime_alert._test_sse_collector
.venv/bin/python -m realtime_alert._test_summarize_run
```

交易时段内用 1～3 只股票实连 60 秒：

```bash
.venv/bin/python -m realtime_alert.collector \
  --symbol 300058.SZ \
  --duration 60 \
  --output-dir diagnostics/server_smoke \
  --metrics-interval 10
```

检查：

```bash
find realtime_alert/diagnostics/server_smoke -type f -maxdepth 2 -ls
tail -n 20 realtime_alert/diagnostics/server_smoke/YYYYMMDD/connections.jsonl
tail -n 5 realtime_alert/diagnostics/server_smoke/YYYYMMDD/metrics.jsonl
```

预期至少出现：

- `collector_starting`；
- 每只股票的 `connected`；
- `trades.jsonl` 首帧成交记录；
- `quotes.jsonl` 快照；
- `metrics.jsonl` CPU、RSS、连接数和队列指标。

若处于午休或盘后，SSE 首帧仍可能有最近记录，但不能据此完成盘中增量验收。

## 三、systemd 服务

复制并编辑模板：

```bash
sudo cp realtime_alert/deploy/realtime-alert.service.example \
  /etc/systemd/system/realtime-alert.service
sudo systemctl edit --full realtime-alert.service
```

必须把模板里的 `/opt/AI_Trading_Scout` 替换为服务器真实绝对路径。然后：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now realtime-alert.service
sudo systemctl status realtime-alert.service
journalctl -u realtime-alert.service -f
```

服务使用 `--market-hours`：

```text
工作日 09:20–11:35
工作日 12:55–15:10
```

时间窗口故意在连续竞价前后留出余量。当前调度器只判断周一至周五，不内置中国法定节假日交易日历；节假日会尝试连接并留下错误审计，但不会伪造数据。

## 四、输出文件

默认输出：

```text
realtime_alert/data/YYYYMMDD/trades.jsonl
realtime_alert/data/YYYYMMDD/quotes.jsonl
realtime_alert/data/YYYYMMDD/connections.jsonl
realtime_alert/data/YYYYMMDD/metrics.jsonl
realtime_alert/data/YYYYMMDD/collisions.jsonl
```

JSONL 都是只追加事实记录。不要在运行中移动或改写当日文件；备份或压缩安排在收盘并停止网络任务之后。

## 五、收盘汇总

```bash
.venv/bin/python -m realtime_alert.summarize_run data/YYYYMMDD
```

输出：

```text
realtime_alert/data/YYYYMMDD/run_summary.json
```

首日重点查看：

```text
observed_symbol_count             是否为100
possible_gap_events              应为0
recovery_exhausted_events         应尽量为0
quote_error_events                快照错误次数
peak_process_cpu_percent          CPU峰值
peak_process_rss_mib              内存峰值
peak_queue_size                   应远低于10000
peak_network_connections          实际连接规模
trade_counts_by_symbol            每股成交记录数
quote_counts_by_symbol            每股快照数
```

不要只看服务是否还在运行。只要存在 `unrecoverable_gap_possible`，当日数据就不能宣称完整；若队列持续增长，则说明 writer 或磁盘异常。

## 六、首日扩容建议

虽然程序硬上限已按100只设计，第一次部署仍建议：

1. 交易时段先用 3 只运行 1 分钟；
2. 用 10 只运行 10 分钟；
3. 再换正式100只股票池，并观察前30分钟日志；
4. 若大量出现 `RemoteProtocolError`、429、502 或 `recovery_exhausted`，立即降低股票数，不要通过无限提高并发掩盖上游限制。

程序启动时会把100只 SSE 建连与启动回补均匀展开到30秒，快照请求均匀错开到每个3秒周期中。全局并发默认：建连10、回补5、快照10。

## 七、停止与重启

```bash
sudo systemctl stop realtime-alert.service
sudo systemctl restart realtime-alert.service
```

正常 `SIGTERM` 会停止网络任务、排空写入队列、刷新并 `fsync` 后退出。若进程被 `SIGKILL` 或服务器突然掉电，最多可能丢失最近一个 `fsync` 周期（默认约2秒）的尚未持久化记录。

同日重启会从当日 `trades.jsonl` 最多读取尾部32 MiB，恢复近期复合去重键与每股时间水位；不会全量加载全天文件。若突然掉电留下末尾半行，程序会计入 `restore_trailing_partial_lines` 后继续；若发现非末行损坏，则拒绝启动，避免静默跳过历史数据。
