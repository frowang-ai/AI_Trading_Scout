#!/usr/bin/env python3
"""Bounded live test: Eastmoney trade SSE plus a 3-second quote poller."""

from __future__ import annotations

import argparse
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

from realtime_alert.eastmoney import EastmoneyClient, to_secid


CURRENT_DIR = Path(__file__).parent.resolve()
CHINA_TZ = ZoneInfo("Asia/Shanghai")
SSE_URL = "https://81.push2.eastmoney.com/api/qt/stock/details/sse"
SSE_UT = "bd1d9ddb04089700cf9c27f6f7426281"


def now_iso() -> str:
    return datetime.now(CHINA_TZ).isoformat()


def run_quote_poller(
    symbol: str,
    duration: float,
    interval: float,
    output: list[dict[str, Any]],
    stop: threading.Event,
) -> None:
    client = EastmoneyClient(timeout=10)
    deadline = time.monotonic() + duration
    sequence = 0
    next_run = time.monotonic()
    while not stop.is_set() and time.monotonic() < deadline:
        started = time.monotonic()
        requested_at = now_iso()
        sequence += 1
        try:
            quote = client.quote(symbol)
            output.append(
                {
                    "sequence": sequence,
                    "requested_at": requested_at,
                    "received_at": now_iso(),
                    "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
                    "status": "ok",
                    "price": quote["price"],
                    "source_time": quote["source_time"],
                    "order_book_available": quote["order_book_available"],
                    "bid1": quote["bids"][0] if quote["bids"] else None,
                    "ask1": quote["asks"][0] if quote["asks"] else None,
                }
            )
        except Exception as exc:
            output.append(
                {
                    "sequence": sequence,
                    "requested_at": requested_at,
                    "received_at": now_iso(),
                    "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
        next_run += interval
        wait_seconds = next_run - time.monotonic()
        if wait_seconds > 0:
            stop.wait(wait_seconds)


def run_sse(
    symbol: str,
    duration: float,
    output: list[dict[str, Any]],
    stop: threading.Event,
) -> None:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Referer": "https://quote.eastmoney.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"
            ),
        }
    )
    params = {
        "fields1": "f1,f2,f3,f4",
        "fields2": "f51,f52,f53,f54,f55",
        "mpi": 1000,
        "dect": 1,
        "ut": SSE_UT,
        "fltt": 2,
        "pos": -3,
        "secid": to_secid(symbol),
        "wbp2u": "|0|0|0|web",
    }
    deadline = time.monotonic() + duration
    try:
        with session.get(
            SSE_URL,
            params=params,
            stream=True,
            timeout=(10, max(15.0, duration + 5.0)),
        ) as response:
            response.raise_for_status()
            output.append(
                {
                    "received_at": now_iso(),
                    "status": "connected",
                    "http_status": response.status_code,
                    "content_type": response.headers.get("Content-Type"),
                }
            )
            data_lines: list[str] = []
            for raw_line in response.iter_lines(decode_unicode=True):
                if stop.is_set() or time.monotonic() >= deadline:
                    break
                line = raw_line or ""
                if line.startswith("data:"):
                    data_lines.append(line[5:].lstrip())
                elif line == "" and data_lines:
                    payload = json.loads("\n".join(data_lines))
                    details = (payload.get("data") or {}).get("details") or []
                    output.append(
                        {
                            "received_at": now_iso(),
                            "status": "event",
                            "full": payload.get("full"),
                            "detail_count": len(details),
                            "details": details,
                        }
                    )
                    data_lines.clear()
    except Exception as exc:
        output.append(
            {
                "received_at": now_iso(),
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
    finally:
        stop.set()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="300058.SZ")
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--quote-interval", type=float, default=3.0)
    args = parser.parse_args()
    if args.duration <= 0 or args.quote_interval <= 0:
        parser.error("duration 和 quote-interval 必须大于 0")

    sse_events: list[dict[str, Any]] = []
    quote_polls: list[dict[str, Any]] = []
    stop = threading.Event()
    threads = [
        threading.Thread(
            target=run_sse,
            args=(args.symbol, args.duration, sse_events, stop),
            name="eastmoney-sse",
        ),
        threading.Thread(
            target=run_quote_poller,
            args=(args.symbol, args.duration, args.quote_interval, quote_polls, stop),
            name="eastmoney-quote-poller",
        ),
    ]
    started_at = now_iso()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=args.duration + 20)
    stop.set()

    report = {
        "symbol": args.symbol,
        "started_at": started_at,
        "finished_at": now_iso(),
        "duration_seconds": args.duration,
        "quote_interval_seconds": args.quote_interval,
        "sse": sse_events,
        "quotes": quote_polls,
    }
    report_path = CURRENT_DIR / "_test_eastmoney_sse_monitor.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
