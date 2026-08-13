#!/usr/bin/env python3
"""Offline contract tests for the production multi-symbol SSE collector."""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

from realtime_alert.collector import (
    AsyncJsonlWriter,
    RecentTradeDeduper,
    SSEDecoder,
    load_symbols,
    normalize_trade,
    CollectorConfig,
    next_market_window,
    restore_recent_trade_state,
)
from datetime import datetime
from zoneinfo import ZoneInfo


CURRENT_DIR = Path(__file__).parent.resolve()


def test_sse_decoder_handles_multiline_and_partial_events() -> None:
    decoder = SSEDecoder()
    assert decoder.feed("data: {\"full\":0,") == []
    assert decoder.feed('data: "data":{"details":[]}}') == []
    assert decoder.feed("") == ['{\"full\":0,\n"data":{"details":[]}}']
    assert decoder.feed(": heartbeat") == []


def test_normalize_and_dedupe_recovery_overlap() -> None:
    record = normalize_trade(
        symbol="300058.SZ",
        raw="13:12:36,15.78,444,42,2",
        trade_date="2026-08-13",
        received_at="2026-08-13T13:12:36.187+08:00",
        source_kind="sse",
        connection_id="connection-1",
        frame_sequence=3,
        detail_sequence=7,
        full=0,
        recovered=False,
        reconnect_attempt=0,
    )
    assert record["volume_lots"] == 444
    assert record["trade_count"] == 42
    assert record["dedupe_key"].endswith("|15.78|444|42|2")

    deduper = RecentTradeDeduper(max_keys_per_symbol=20)
    assert deduper.seen_or_add("300058.SZ", record["dedupe_key"]) is False
    assert deduper.seen_or_add("300058.SZ", record["dedupe_key"]) is True


def test_symbol_file_normalizes_and_enforces_limit() -> None:
    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        path = Path(temp_dir) / "symbols.txt"
        path.write_text("# watchlist\n300058.SZ\nsz000001\n300058.SZ\n", encoding="utf-8")
        assert load_symbols(path, max_symbols=100) == ["300058.SZ", "000001.SZ"]
        path.write_text("\n".join(f"{index:06d}.SZ" for index in range(101)), encoding="utf-8")
        try:
            load_symbols(path, max_symbols=100)
        except ValueError as exc:
            assert "100" in str(exc)
        else:
            raise AssertionError("超过100只股票时必须拒绝启动")


def test_writer_batches_and_routes_jsonl() -> None:
    async def scenario(output_dir: Path) -> None:
        queue: asyncio.Queue[dict[str, object] | None] = asyncio.Queue(maxsize=10)
        writer = AsyncJsonlWriter(
            output_dir=output_dir,
            queue=queue,
            batch_size=100,
            flush_interval=0.01,
            fsync_interval=0.01,
        )
        task = asyncio.create_task(writer.run())
        await queue.put(
            {
                "stream": "trades",
                "trade_date": "20260813",
                "symbol": "300058.SZ",
                "price": 15.78,
            }
        )
        await queue.put(
            {
                "stream": "connections",
                "trade_date": "20260813",
                "symbol": "300058.SZ",
                "status": "connected",
            }
        )
        await queue.put(None)
        await task

        trade_path = output_dir / "20260813" / "trades.jsonl"
        connection_path = output_dir / "20260813" / "connections.jsonl"
        assert json.loads(trade_path.read_text(encoding="utf-8"))["price"] == 15.78
        assert json.loads(connection_path.read_text(encoding="utf-8"))["status"] == "connected"

    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        asyncio.run(scenario(Path(temp_dir)))


def test_collector_suppresses_stale_and_audits_duplicate() -> None:
    from realtime_alert.collector import EastmoneySSECollector

    async def scenario(output_dir: Path) -> None:
        collector = EastmoneySSECollector(
            CollectorConfig(symbols=["300058.SZ"], output_dir=output_dir)
        )
        stale = normalize_trade(
            symbol="300058.SZ",
            raw="15:30:00,15.25,5,4,1",
            trade_date="2026-08-14",
            received_at="2026-08-14T09:20:00+08:00",
            source_kind="sse",
            connection_id="c1",
            frame_sequence=1,
            detail_sequence=1,
            full=1,
            recovered=False,
            reconnect_attempt=0,
        )
        assert await collector.accept_trade(stale) is False

        live = normalize_trade(
            symbol="300058.SZ",
            raw="09:31:00,15.25,5,4,1",
            trade_date="2026-08-14",
            received_at="2026-08-14T09:31:01+08:00",
            source_kind="sse",
            connection_id="c1",
            frame_sequence=2,
            detail_sequence=2,
            full=0,
            recovered=False,
            reconnect_attempt=0,
        )
        assert await collector.accept_trade(live) is True
        assert await collector.accept_trade(live) is False
        streams = [collector.queue.get_nowait()["stream"] for _ in range(3)]
        assert streams == ["collisions", "trades", "collisions"]

        older_recovery = normalize_trade(
            symbol="300058.SZ",
            raw="09:30:00,15.24,6,5,2",
            trade_date="2026-08-14",
            received_at="2026-08-14T09:31:02+08:00",
            source_kind="recovery_http",
            connection_id=None,
            frame_sequence=0,
            detail_sequence=1,
            full=1,
            recovered=True,
            reconnect_attempt=1,
        )
        assert await collector.accept_trade(older_recovery) is True
        assert collector.last_source_time["300058.SZ"] == "09:31:00"
        assert collector.last_dedupe_key["300058.SZ"] == live["dedupe_key"]
        await collector.client.aclose()

    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        asyncio.run(scenario(Path(temp_dir)))


def test_disconnects_chain_recovery_without_blocking_reconnect() -> None:
    from realtime_alert.collector import EastmoneySSECollector

    class ControlledCollector(EastmoneySSECollector):
        def __init__(self, config: CollectorConfig):
            super().__init__(config)
            self.stream_attempts: list[int] = []
            self.recovery_attempts: list[int] = []

        async def recover(self, symbol: str, reconnect_attempt: int) -> bool:
            self.recovery_attempts.append(reconnect_attempt)
            await asyncio.sleep(0.02)
            return True

        async def stream_once(self, symbol: str, reconnect_attempt: int) -> None:
            self.stream_attempts.append(reconnect_attempt)
            if len(self.stream_attempts) == 1:
                self.stream_connected_at[symbol] = asyncio.get_running_loop().time()
                self.stream_generation[symbol] += 1
                raise EOFError("controlled disconnect")
            self.stop_event.set()

    async def scenario(output_dir: Path) -> None:
        collector = ControlledCollector(
            CollectorConfig(
                symbols=["300058.SZ"],
                output_dir=output_dir,
                backoff_seconds=(0.01,),
                jitter_ratio=0,
            )
        )
        await collector.supervise_symbol("300058.SZ")
        assert collector.stream_attempts == [0, 1]
        assert collector.recovery_attempts == [0, 1]
        await collector.client.aclose()

    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        asyncio.run(scenario(Path(temp_dir)))


def test_config_accepts_exactly_one_hundred_symbols() -> None:
    symbols = [f"{index:06d}.SZ" for index in range(100)]
    config = CollectorConfig(symbols=symbols)
    assert len(config.symbols) == 100


def test_market_window_scheduler_skips_lunch_and_weekend() -> None:
    china_tz = ZoneInfo("Asia/Shanghai")
    lunch = datetime(2026, 8, 14, 12, 0, tzinfo=china_tz)
    start, end, label = next_market_window(lunch)
    assert label == "afternoon"
    assert start.strftime("%H:%M") == "12:55"
    assert end.strftime("%H:%M") == "15:10"

    saturday = datetime(2026, 8, 15, 10, 0, tzinfo=china_tz)
    start, _, label = next_market_window(saturday)
    assert start.strftime("%Y-%m-%d %H:%M") == "2026-08-17 09:20"
    assert label == "morning"


def test_restart_restores_recent_dedupe_state_from_bounded_tail() -> None:
    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        path = Path(temp_dir) / "trades.jsonl"
        records = [
            normalize_trade(
                symbol="300058.SZ",
                raw=f"09:31:0{index},15.2{index},{index + 1},{index + 2},1",
                trade_date="2026-08-14",
                received_at=f"2026-08-14T09:31:0{index}+08:00",
                source_kind="sse",
                connection_id="c1",
                frame_sequence=1,
                detail_sequence=index,
                full=0,
                recovered=False,
                reconnect_attempt=0,
            )
            for index in range(3)
        ]
        path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
            + '{"partial":',
            encoding="utf-8",
        )
        deduper = RecentTradeDeduper(max_keys_per_symbol=20)
        report = restore_recent_trade_state(
            path, symbols={"300058.SZ"}, deduper=deduper
        )
        assert report["records_restored"] == 3
        assert report["trailing_partial_lines"] == 1
        assert report["last_source_time"]["300058.SZ"] == "09:31:02"
        assert deduper.contains("300058.SZ", records[-1]["dedupe_key"])


def main() -> None:
    tests = [
        test_sse_decoder_handles_multiline_and_partial_events,
        test_normalize_and_dedupe_recovery_overlap,
        test_symbol_file_normalizes_and_enforces_limit,
        test_writer_batches_and_routes_jsonl,
        test_collector_suppresses_stale_and_audits_duplicate,
        test_disconnects_chain_recovery_without_blocking_reconnect,
        test_config_accepts_exactly_one_hundred_symbols,
        test_market_window_scheduler_skips_lunch_and_weekend,
        test_restart_restores_recent_dedupe_state_from_bounded_tail,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    main()
