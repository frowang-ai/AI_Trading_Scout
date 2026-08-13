#!/usr/bin/env python3
"""Offline contract test for the streaming run summarizer."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from realtime_alert.summarize_run import summarize_partition


CURRENT_DIR = Path(__file__).parent.resolve()


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def test_summary_counts_quality_and_resources() -> None:
    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        partition = Path(temp_dir)
        write_jsonl(
            partition / "trades.jsonl",
            [
                {"symbol": "300058.SZ", "recovered": False},
                {"symbol": "300058.SZ", "recovered": True},
            ],
        )
        write_jsonl(partition / "quotes.jsonl", [{"symbol": "300058.SZ"}])
        write_jsonl(
            partition / "connections.jsonl",
            [
                {"status": "collector_starting", "symbols": ["300058.SZ", "000001.SZ"]},
                {"status": "connected"},
                {"status": "unrecoverable_gap_possible"},
            ],
        )
        write_jsonl(
            partition / "metrics.jsonl",
            [
                {
                    "process_cpu_percent": 2.5,
                    "process_rss_mib": 44.0,
                    "queue_size": 3,
                    "connections": 5,
                }
            ],
        )
        summary = summarize_partition(partition)
        assert summary["trade_records"] == 2
        assert summary["recovered_trade_records"] == 1
        assert summary["possible_gap_events"] == 1
        assert summary["peak_process_rss_mib"] == 44.0
        assert summary["expected_symbol_count"] == 2
        assert summary["symbols_without_any_data"] == ["000001.SZ"]


def main() -> None:
    test_summary_counts_quality_and_resources()
    print("1 test passed")


if __name__ == "__main__":
    main()
