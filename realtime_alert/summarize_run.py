"""Stream a collector trading-day partition and write a compact health report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator


CURRENT_DIR = Path(__file__).parent.resolve()


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.is_file():
        return
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSONL 解析失败: {path}:{line_number}") from exc


def summarize_partition(partition_dir: Path) -> dict[str, Any]:
    trade_counts: Counter[str] = Counter()
    recovered_counts: Counter[str] = Counter()
    quote_counts: Counter[str] = Counter()
    connection_statuses: Counter[str] = Counter()
    max_cpu = 0.0
    max_rss = 0.0
    max_queue = 0
    max_connections = 0
    latest_metrics: dict[str, Any] | None = None
    expected_symbols: list[str] = []

    for record in iter_jsonl(partition_dir / "trades.jsonl"):
        symbol = str(record.get("symbol"))
        trade_counts[symbol] += 1
        if record.get("recovered"):
            recovered_counts[symbol] += 1
    for record in iter_jsonl(partition_dir / "quotes.jsonl"):
        quote_counts[str(record.get("symbol"))] += 1
    for record in iter_jsonl(partition_dir / "connections.jsonl"):
        connection_statuses[str(record.get("status"))] += 1
        if record.get("status") in {"collector_starting", "market_window_starting"} and isinstance(
            record.get("symbols"), list
        ):
            expected_symbols = [str(value) for value in record["symbols"]]
    for record in iter_jsonl(partition_dir / "metrics.jsonl"):
        latest_metrics = record
        max_cpu = max(max_cpu, float(record.get("process_cpu_percent") or 0))
        max_rss = max(max_rss, float(record.get("process_rss_mib") or 0))
        max_queue = max(max_queue, int(record.get("queue_size") or 0))
        max_connections = max(max_connections, int(record.get("connections") or 0))

    observed_symbols = sorted(set(trade_counts) | set(quote_counts))
    report_symbols = sorted(set(expected_symbols) | set(observed_symbols))
    file_sizes = {
        name: (partition_dir / f"{name}.jsonl").stat().st_size
        if (partition_dir / f"{name}.jsonl").is_file()
        else 0
        for name in ("trades", "quotes", "connections", "metrics", "collisions")
    }
    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "partition_dir": str(partition_dir),
        "observed_symbol_count": len(observed_symbols),
        "expected_symbol_count": len(set(expected_symbols)),
        "trade_records": sum(trade_counts.values()),
        "quote_records": sum(quote_counts.values()),
        "recovered_trade_records": sum(recovered_counts.values()),
        "symbols_without_any_data": [
            symbol for symbol in report_symbols if symbol not in observed_symbols
        ],
        "symbols_without_trades": [symbol for symbol in report_symbols if trade_counts[symbol] == 0],
        "symbols_without_quotes": [symbol for symbol in report_symbols if quote_counts[symbol] == 0],
        "trade_counts_by_symbol": dict(sorted(trade_counts.items())),
        "quote_counts_by_symbol": dict(sorted(quote_counts.items())),
        "connection_statuses": dict(sorted(connection_statuses.items())),
        "possible_gap_events": connection_statuses["unrecoverable_gap_possible"],
        "recovery_exhausted_events": connection_statuses["recovery_exhausted"],
        "quote_error_events": connection_statuses["quote_error"],
        "peak_process_cpu_percent": max_cpu,
        "peak_process_rss_mib": max_rss,
        "peak_queue_size": max_queue,
        "peak_network_connections": max_connections,
        "latest_metrics": latest_metrics,
        "file_sizes_bytes": file_sizes,
        "total_bytes": sum(file_sizes.values()),
    }


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (CURRENT_DIR / path).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="汇总 SSE 采集器单日运行质量")
    parser.add_argument("partition_dir", help="例如 data/20260814；相对路径按 realtime_alert/ 解析")
    parser.add_argument("--output", help="默认写入分区内 run_summary.json")
    args = parser.parse_args()
    partition_dir = resolve_path(args.partition_dir)
    if not partition_dir.is_dir():
        parser.error(f"目录不存在: {partition_dir}")
    output_path = resolve_path(args.output) if args.output else partition_dir / "run_summary.json"
    report = summarize_partition(partition_dir)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"report={output_path}")


if __name__ == "__main__":
    main()
