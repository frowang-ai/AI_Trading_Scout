#!/usr/bin/env python3
"""Benchmark normalized intraday JSONL encoding and buffered disk writes.

This is a local capacity diagnostic, not a network benchmark.  It estimates the
CPU and disk portion shared by a multi-symbol SSE collector without contacting
Eastmoney.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any


CURRENT_DIR = Path(__file__).parent.resolve()
DEFAULT_REPORT_PATH = CURRENT_DIR / "_test_sse_capacity.json"


def make_record(sequence: int) -> dict[str, Any]:
    """Return one representative normalized SSE trade record."""

    return {
        "schema_version": 1,
        "trade_date": "2026-08-13",
        "symbol": f"{sequence % 500:06d}.SZ",
        "source_time": "13:12:36",
        "price": 15.78,
        "volume_lots": 444,
        "trade_count": 42,
        "side_code": 2,
        "received_at": "2026-08-13T13:12:36.187+08:00",
        "connection_id": f"300058-20260813-{sequence // 4800:04d}",
        "frame_sequence": sequence // 2,
        "detail_sequence": sequence,
        "full": 0,
        "recovered": False,
        "disconnect_started": None,
        "reconnect_attempt": 0,
        "dedupe_key": (
            f"2026-08-13|{sequence % 500:06d}.SZ|13:12:36|"
            f"15.78|444|42|2"
        ),
    }


def serialize_records(record_count: int) -> tuple[list[bytes], float]:
    started = time.perf_counter()
    lines = [
        (json.dumps(make_record(index), ensure_ascii=False, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        for index in range(record_count)
    ]
    return lines, time.perf_counter() - started


def write_lines(lines: list[bytes], flush_every: int) -> tuple[int, float]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="realtime-alert-capacity-") as temp_dir:
        output_path = Path(temp_dir) / "trades.jsonl"
        with output_path.open("wb", buffering=1024 * 1024) as output_file:
            for index, line in enumerate(lines, start=1):
                output_file.write(line)
                if index % flush_every == 0:
                    output_file.flush()
            output_file.flush()
        byte_count = output_path.stat().st_size
    return byte_count, time.perf_counter() - started


def build_capacity_estimates(bytes_per_record: float) -> list[dict[str, Any]]:
    trading_seconds = 4 * 60 * 60
    records_per_symbol = trading_seconds / 3
    estimates: list[dict[str, Any]] = []
    for symbols in (10, 50, 100, 500):
        records_per_second = symbols / 3
        bytes_per_day = bytes_per_record * records_per_symbol * symbols
        estimates.append(
            {
                "symbols": symbols,
                "sse_connections": symbols,
                "trade_records_per_second": round(records_per_second, 2),
                "trade_records_per_day": int(records_per_symbol * symbols),
                "normalized_trade_mib_per_day": round(bytes_per_day / 1024 / 1024, 2),
                "three_second_quote_requests_per_second_if_unbatched": round(
                    symbols / 3, 2
                ),
            }
        )
    return estimates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=100_000)
    parser.add_argument("--flush-every", type=int, default=100)
    args = parser.parse_args()
    if args.records <= 0 or args.flush_every <= 0:
        parser.error("records 和 flush-every 必须大于 0")

    lines, serialize_seconds = serialize_records(args.records)
    byte_count, write_seconds = write_lines(lines, args.flush_every)
    bytes_per_record = byte_count / args.records
    report = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "scope": "local JSON serialization and buffered JSONL write only",
        "record_count": args.records,
        "flush_every": args.flush_every,
        "bytes_total": byte_count,
        "bytes_per_record": round(bytes_per_record, 2),
        "serialize_seconds": round(serialize_seconds, 6),
        "serialize_records_per_second": round(args.records / serialize_seconds, 2),
        "write_seconds": round(write_seconds, 6),
        "write_mib_per_second": round(byte_count / write_seconds / 1024 / 1024, 2),
        "capacity_estimates": build_capacity_estimates(bytes_per_record),
        "assumptions": {
            "trading_hours_per_day": 4,
            "one_trade_aggregate_every_seconds": 3,
            "quote_poll_interval_seconds": 3,
            "excludes": [
                "network/TLS cost",
                "raw SSE frame archive",
                "quote snapshot storage",
                "error and reconnect logs",
                "filesystem sync on every record",
            ],
        },
    }
    DEFAULT_REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"report={DEFAULT_REPORT_PATH}")


if __name__ == "__main__":
    main()
