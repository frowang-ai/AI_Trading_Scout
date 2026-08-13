"""Command-line entry point for probing and recording Eastmoney quotes."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from realtime_alert.eastmoney import EastmoneyClient


CURRENT_DIR = Path(__file__).parent.resolve()
CHINA_TZ = ZoneInfo("Asia/Shanghai")


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _watch(client: EastmoneyClient, symbol: str, interval: float, count: int | None) -> None:
    trade_date = datetime.now(CHINA_TZ).strftime("%Y%m%d")
    output_path = CURRENT_DIR / "data" / trade_date / f"{symbol.replace('.', '_')}_quotes.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    completed = 0
    try:
        while count is None or completed < count:
            started = time.monotonic()
            quote = client.quote(symbol)
            with output_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(quote, ensure_ascii=False) + "\n")
            print(json.dumps(quote, ensure_ascii=False), flush=True)
            completed += 1
            remaining = interval - (time.monotonic() - started)
            if remaining > 0 and (count is None or completed < count):
                time.sleep(remaining)
    except KeyboardInterrupt:
        pass
    print(f"output={output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="东方财富网页行情抓取器")
    parser.add_argument("command", choices=("quote", "minutes", "trades", "watch"))
    parser.add_argument("symbol", help="例如 300058.SZ、sz300058 或 0.300058")
    parser.add_argument("--limit", type=int, default=20, help="trades 返回的最近记录数")
    parser.add_argument("--interval", type=float, default=3.0, help="watch 轮询秒数")
    parser.add_argument("--count", type=int, help="watch 次数；省略则持续运行")
    args = parser.parse_args()
    client = EastmoneyClient()
    if args.command == "quote":
        _print(client.quote(args.symbol))
    elif args.command == "minutes":
        _print(client.intraday_minutes(args.symbol))
    elif args.command == "trades":
        _print(client.recent_trades(args.symbol, args.limit))
    else:
        if args.interval <= 0:
            parser.error("--interval 必须大于 0")
        _watch(client, args.symbol, args.interval, args.count)


if __name__ == "__main__":
    main()
