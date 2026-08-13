"""Production-oriented multi-symbol Eastmoney SSE collector.

The upstream endpoints are undocumented web contracts.  Every recovery and
failure is therefore written to an audit stream; the collector never claims
that a reconnect makes the source lossless.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import signal
import time
import uuid
from collections import Counter, OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, time as datetime_time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx
import psutil

from realtime_alert.eastmoney import (
    ASK_FIELDS,
    BASE_URL,
    BID_FIELDS,
    QUOTE_FIELDS,
    UT,
    to_secid,
)


CURRENT_DIR = Path(__file__).parent.resolve()
CHINA_TZ = ZoneInfo("Asia/Shanghai")
SSE_URL = "https://81.push2.eastmoney.com/api/qt/stock/details/sse"
SSE_UT = "bd1d9ddb04089700cf9c27f6f7426281"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"
)


def now_iso() -> str:
    return datetime.now(CHINA_TZ).isoformat()


def current_trade_date(compact: bool = False) -> str:
    return datetime.now(CHINA_TZ).strftime("%Y%m%d" if compact else "%Y-%m-%d")


MARKET_WINDOWS = (
    (datetime_time(9, 20), datetime_time(11, 35), "morning"),
    (datetime_time(12, 55), datetime_time(15, 10), "afternoon"),
)


def next_market_window(now: datetime | None = None) -> tuple[datetime, datetime, str]:
    """Return the current or next weekday collection window in China time."""

    moment = (now or datetime.now(CHINA_TZ)).astimezone(CHINA_TZ)
    for day_offset in range(8):
        candidate_date = (moment + timedelta(days=day_offset)).date()
        if candidate_date.weekday() >= 5:
            continue
        for start_time, end_time, label in MARKET_WINDOWS:
            start = datetime.combine(candidate_date, start_time, CHINA_TZ)
            end = datetime.combine(candidate_date, end_time, CHINA_TZ)
            if end > moment:
                return max(start, moment), end, label
    raise RuntimeError("无法计算下一交易时段")


def canonical_symbol(symbol: str) -> str:
    secid = to_secid(symbol)
    market, code = secid.split(".", 1)
    if market == "1":
        suffix = "SH"
    else:
        suffix = "BJ" if code.startswith(("4", "8", "9")) else "SZ"
    return f"{code}.{suffix}"


def load_symbols(path: Path, max_symbols: int = 100) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"股票池文件不存在: {path}")
    symbols: list[str] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        value = raw_line.split("#", 1)[0].strip()
        if not value:
            continue
        try:
            symbol = canonical_symbol(value)
        except ValueError as exc:
            raise ValueError(f"股票池第 {line_number} 行无效: {raw_line!r}") from exc
        if symbol not in seen:
            symbols.append(symbol)
            seen.add(symbol)
        if len(symbols) > max_symbols:
            raise ValueError(f"股票池最多允许 {max_symbols} 只，当前至少 {len(symbols)} 只")
    if not symbols:
        raise ValueError("股票池为空")
    return symbols


def restore_recent_trade_state(
    path: Path,
    *,
    symbols: set[str],
    deduper: "RecentTradeDeduper",
    max_tail_bytes: int = 32 * 1024 * 1024,
) -> dict[str, Any]:
    """Restore bounded same-day dedupe watermarks from the JSONL tail."""

    report: dict[str, Any] = {
        "path": str(path),
        "file_exists": path.is_file(),
        "bytes_scanned": 0,
        "records_restored": 0,
        "trailing_partial_lines": 0,
        "counts_by_symbol": {},
        "last_source_time": {},
        "last_dedupe_key": {},
    }
    if not path.is_file():
        return report
    file_size = path.stat().st_size
    start = max(0, file_size - max_tail_bytes)
    with path.open("rb") as handle:
        handle.seek(start)
        data = handle.read()
    report["bytes_scanned"] = len(data)
    lines = data.splitlines()
    if start > 0 and lines:
        lines = lines[1:]
    counts: Counter[str] = Counter()
    last_source_time: dict[str, str] = {}
    last_dedupe_key: dict[str, str] = {}
    for index, raw_line in enumerate(lines):
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            if index == len(lines) - 1:
                report["trailing_partial_lines"] += 1
                continue
            raise ValueError(f"历史成交 JSONL 尾部存在非末行损坏: {path}") from exc
        symbol = str(record.get("symbol") or "")
        key = str(record.get("dedupe_key") or "")
        source_time = str(record.get("source_time") or "")
        if symbol not in symbols or not key or not source_time:
            continue
        deduper.seen_or_add(symbol, key)
        counts[symbol] += 1
        if source_time >= last_source_time.get(symbol, ""):
            last_source_time[symbol] = source_time
            last_dedupe_key[symbol] = key
    report["records_restored"] = sum(counts.values())
    report["counts_by_symbol"] = dict(sorted(counts.items()))
    report["last_source_time"] = last_source_time
    report["last_dedupe_key"] = last_dedupe_key
    return report


class SSEDecoder:
    """Incrementally decode SSE data fields into complete payload strings."""

    def __init__(self) -> None:
        self._data_lines: list[str] = []

    def feed(self, line: str) -> list[str]:
        if line.startswith(":"):
            return []
        if line.startswith("data:"):
            self._data_lines.append(line[5:].lstrip())
            return []
        if line == "" and self._data_lines:
            payload = "\n".join(self._data_lines)
            self._data_lines.clear()
            return [payload]
        return []


def normalize_trade(
    *,
    symbol: str,
    raw: str,
    trade_date: str,
    received_at: str,
    source_kind: str,
    connection_id: str | None,
    frame_sequence: int,
    detail_sequence: int,
    full: int | None,
    recovered: bool,
    reconnect_attempt: int,
) -> dict[str, Any]:
    values = raw.split(",")
    if len(values) < 4:
        raise ValueError(f"分笔字段数量异常: {raw!r}")
    trade_time = values[0]
    price = float(values[1])
    volume_lots = int(values[2])
    trade_count = int(values[3])
    side_code = int(values[4]) if len(values) >= 5 and values[4] != "" else None
    dedupe_key = "|".join(
        str(value)
        for value in (
            trade_date,
            symbol,
            trade_time,
            price,
            volume_lots,
            trade_count,
            side_code,
        )
    )
    return {
        "stream": "trades",
        "schema_version": 1,
        "trade_date": trade_date.replace("-", ""),
        "symbol": symbol,
        "source_time": trade_time,
        "price": price,
        "volume_lots": volume_lots,
        "trade_count": trade_count,
        "side_code": side_code,
        "estimated_amount_cny": price * volume_lots * 100,
        "received_at": received_at,
        "source_kind": source_kind,
        "connection_id": connection_id,
        "frame_sequence": frame_sequence,
        "detail_sequence": detail_sequence,
        "full": full,
        "recovered": recovered,
        "reconnect_attempt": reconnect_attempt,
        "dedupe_key": dedupe_key,
    }


class RecentTradeDeduper:
    """Bounded per-symbol key index for SSE first frames and HTTP recovery."""

    def __init__(self, max_keys_per_symbol: int = 200):
        if max_keys_per_symbol <= 0:
            raise ValueError("max_keys_per_symbol 必须大于 0")
        self.max_keys_per_symbol = max_keys_per_symbol
        self._keys: dict[str, OrderedDict[str, None]] = defaultdict(OrderedDict)

    def seen_or_add(self, symbol: str, key: str) -> bool:
        keys = self._keys[symbol]
        if key in keys:
            keys.move_to_end(key)
            return True
        keys[key] = None
        while len(keys) > self.max_keys_per_symbol:
            keys.popitem(last=False)
        return False

    def contains(self, symbol: str, key: str) -> bool:
        return key in self._keys[symbol]


@dataclass(slots=True)
class CollectorConfig:
    symbols: list[str]
    output_dir: Path = CURRENT_DIR / "data"
    max_symbols: int = 100
    quote_interval: float = 3.0
    recovery_limit: int = 20
    queue_maxsize: int = 10_000
    writer_batch_size: int = 100
    writer_flush_interval: float = 0.2
    writer_fsync_interval: float = 2.0
    connect_concurrency: int = 10
    recovery_concurrency: int = 5
    recovery_http_attempts: int = 3
    quote_concurrency: int = 10
    metrics_interval: float = 60.0
    startup_spread_seconds: float = 30.0
    backoff_seconds: tuple[float, ...] = (1, 2, 4, 8, 15, 30)
    jitter_ratio: float = 0.2

    def __post_init__(self) -> None:
        self.symbols = list(dict.fromkeys(canonical_symbol(value) for value in self.symbols))
        self.output_dir = self.output_dir.resolve()
        if not self.symbols:
            raise ValueError("至少需要一只股票")
        if len(self.symbols) > self.max_symbols:
            raise ValueError(f"股票数 {len(self.symbols)} 超过上限 {self.max_symbols}")
        positive_values = {
            "quote_interval": self.quote_interval,
            "recovery_limit": self.recovery_limit,
            "queue_maxsize": self.queue_maxsize,
            "writer_batch_size": self.writer_batch_size,
            "writer_flush_interval": self.writer_flush_interval,
            "writer_fsync_interval": self.writer_fsync_interval,
            "connect_concurrency": self.connect_concurrency,
            "recovery_concurrency": self.recovery_concurrency,
            "recovery_http_attempts": self.recovery_http_attempts,
            "quote_concurrency": self.quote_concurrency,
            "metrics_interval": self.metrics_interval,
            "startup_spread_seconds": self.startup_spread_seconds,
        }
        for name, value in positive_values.items():
            if value <= 0:
                raise ValueError(f"{name} 必须大于 0")


class AsyncJsonlWriter:
    """Route normalized records to daily JSONL files with batched syncs."""

    STREAMS = {"trades", "quotes", "connections", "metrics", "collisions"}

    def __init__(
        self,
        *,
        output_dir: Path,
        queue: asyncio.Queue[dict[str, Any] | None],
        batch_size: int,
        flush_interval: float,
        fsync_interval: float,
    ) -> None:
        self.output_dir = output_dir.resolve()
        self.queue = queue
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.fsync_interval = fsync_interval
        self.records_written = 0

    async def run(self) -> None:
        handles: dict[Path, Any] = {}
        pending: list[dict[str, Any]] = []
        last_flush = time.monotonic()
        last_fsync = time.monotonic()
        stopping = False
        try:
            while not stopping:
                try:
                    item = await asyncio.wait_for(
                        self.queue.get(), timeout=self.flush_interval
                    )
                    if item is None:
                        stopping = True
                    else:
                        pending.append(item)
                    self.queue.task_done()
                except asyncio.TimeoutError:
                    pass

                if pending and (
                    stopping
                    or len(pending) >= self.batch_size
                    or time.monotonic() - last_flush >= self.flush_interval
                ):
                    for record in pending:
                        stream = str(record.get("stream", ""))
                        if stream not in self.STREAMS:
                            raise ValueError(f"未知写入流: {stream!r}")
                        trade_date = str(record.get("trade_date") or current_trade_date(True))
                        path = self.output_dir / trade_date / f"{stream}.jsonl"
                        if path not in handles:
                            path.parent.mkdir(parents=True, exist_ok=True)
                            handles[path] = path.open("a", encoding="utf-8", buffering=1024 * 1024)
                        handles[path].write(
                            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
                        )
                        self.records_written += 1
                    pending.clear()
                    for handle in handles.values():
                        handle.flush()
                    last_flush = time.monotonic()

                now = time.monotonic()
                if handles and (stopping or now - last_fsync >= self.fsync_interval):
                    for handle in handles.values():
                        handle.flush()
                        os.fsync(handle.fileno())
                    last_fsync = now
        finally:
            for handle in handles.values():
                try:
                    handle.flush()
                    os.fsync(handle.fileno())
                finally:
                    handle.close()


@dataclass(slots=True)
class RuntimeStats:
    started_at: str = field(default_factory=now_iso)
    sse_active: int = 0
    sse_connects: int = 0
    sse_disconnects: int = 0
    sse_frames: int = 0
    trades_written: int = 0
    trades_deduped: int = 0
    stale_trades_ignored: int = 0
    recovered_trades: int = 0
    recovery_successes: int = 0
    recovery_failures: int = 0
    quote_successes: int = 0
    quote_failures: int = 0
    parse_failures: int = 0


class EastmoneySSECollector:
    def __init__(self, config: CollectorConfig):
        self.config = config
        self.queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(
            maxsize=config.queue_maxsize
        )
        self.stop_event = asyncio.Event()
        self.deduper = RecentTradeDeduper(max_keys_per_symbol=200)
        self.stats = RuntimeStats()
        self.last_source_time: dict[str, str] = {}
        self.last_dedupe_key: dict[str, str] = {}
        self.stream_connected_at: dict[str, float] = {}
        self.stream_frames: dict[str, int] = defaultdict(int)
        self.stream_generation: dict[str, int] = defaultdict(int)
        self.connect_semaphore = asyncio.Semaphore(config.connect_concurrency)
        self.recovery_semaphore = asyncio.Semaphore(config.recovery_concurrency)
        self.quote_semaphore = asyncio.Semaphore(config.quote_concurrency)
        self.writer = AsyncJsonlWriter(
            output_dir=config.output_dir,
            queue=self.queue,
            batch_size=config.writer_batch_size,
            flush_interval=config.writer_flush_interval,
            fsync_interval=config.writer_fsync_interval,
        )
        limits = httpx.Limits(
            max_connections=config.max_symbols + config.quote_concurrency + config.recovery_concurrency + 10,
            max_keepalive_connections=max(20, config.quote_concurrency + config.recovery_concurrency),
            keepalive_expiry=30,
        )
        self.client = httpx.AsyncClient(
            headers={
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": USER_AGENT,
            },
            limits=limits,
            follow_redirects=True,
        )

    async def emit(self, record: dict[str, Any]) -> None:
        await self.queue.put(record)

    async def audit(self, symbol: str | None, status: str, **details: Any) -> None:
        await self.emit(
            {
                "stream": "connections",
                "schema_version": 1,
                "trade_date": current_trade_date(True),
                "received_at": now_iso(),
                "symbol": symbol,
                "status": status,
                **details,
            }
        )

    async def accept_trade(self, record: dict[str, Any]) -> bool:
        symbol = str(record["symbol"])
        key = str(record["dedupe_key"])
        received_at = datetime.fromisoformat(str(record["received_at"]))
        source_clock = datetime_time.fromisoformat(str(record["source_time"]))
        received_seconds = (
            received_at.hour * 3600 + received_at.minute * 60 + received_at.second
        )
        source_seconds = source_clock.hour * 3600 + source_clock.minute * 60 + source_clock.second
        if source_seconds - received_seconds > 10 * 60:
            self.stats.stale_trades_ignored += 1
            await self.emit(
                {
                    **record,
                    "stream": "collisions",
                    "status": "stale_source_date_suppressed",
                    "reason": "上游仅给出时分秒，源时间比接收时间晚超过10分钟，疑似上一交易时段记录",
                }
            )
            return False
        if self.deduper.seen_or_add(symbol, key):
            self.stats.trades_deduped += 1
            await self.emit(
                {
                    **record,
                    "stream": "collisions",
                    "status": "dedupe_key_suppressed",
                    "reason": "复合键已出现；可能是SSE首帧/HTTP回补重放，也可能是无法区分的合法键碰撞",
                }
            )
            return False
        source_time = str(record["source_time"])
        if source_time >= self.last_source_time.get(symbol, ""):
            self.last_source_time[symbol] = source_time
            self.last_dedupe_key[symbol] = key
        self.stats.trades_written += 1
        if record["recovered"]:
            self.stats.recovered_trades += 1
        await self.emit(record)
        return True

    async def fetch_recent_trades(
        self, symbol: str, reconnect_attempt: int
    ) -> tuple[list[dict[str, Any]], bool]:
        previous_key = self.last_dedupe_key.get(symbol)
        params = {
            "ut": UT,
            "secid": to_secid(symbol),
            "pos": -self.config.recovery_limit,
            "iscca": 1,
            "invt": 2,
            "fltt": 2,
            "fields1": "f1,f2,f3,f4,f5",
            "fields2": "f51,f52,f53,f54,f55",
            "_": int(time.time() * 1000),
        }
        async with self.recovery_semaphore:
            response = await self.client.get(
                f"{BASE_URL}/details/get", params=params, timeout=10.0
            )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data")
        if payload.get("rc") != 0 or not isinstance(data, dict):
            raise RuntimeError(
                f"details/get 无有效 data: rc={payload.get('rc')}, message={payload.get('message')}"
            )
        received_at = now_iso()
        trade_date = current_trade_date(False)
        rows = [
            normalize_trade(
                symbol=symbol,
                raw=raw,
                trade_date=trade_date,
                received_at=received_at,
                source_kind="recovery_http",
                connection_id=None,
                frame_sequence=0,
                detail_sequence=index,
                full=1,
                recovered=True,
                reconnect_attempt=reconnect_attempt,
            )
            for index, raw in enumerate(data.get("details") or [], 1)
        ]
        overlap_found = previous_key is None or any(
            row["dedupe_key"] == previous_key for row in rows
        )
        return rows, overlap_found

    async def recover(self, symbol: str, reconnect_attempt: int) -> bool:
        recovery_started = time.monotonic()
        for http_attempt in range(1, self.config.recovery_http_attempts + 1):
            try:
                rows, overlap_found = await self.fetch_recent_trades(symbol, reconnect_attempt)
                inserted = 0
                for row in rows:
                    if await self.accept_trade(row):
                        inserted += 1
                self.stats.recovery_successes += 1
                await self.audit(
                    symbol,
                    "recovery_complete",
                    reconnect_attempt=reconnect_attempt,
                    http_attempt=http_attempt,
                    rows_received=len(rows),
                    rows_inserted=inserted,
                    overlap_found=overlap_found,
                    elapsed_ms=round((time.monotonic() - recovery_started) * 1000, 1),
                )
                if reconnect_attempt > 0 and rows and not overlap_found:
                    await self.audit(
                        symbol,
                        "unrecoverable_gap_possible",
                        reconnect_attempt=reconnect_attempt,
                        recovery_first_source_time=rows[0]["source_time"],
                        reason="最近回补窗口中找不到断线前最后一条记录",
                    )
                return True
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.stats.recovery_failures += 1
                await self.audit(
                    symbol,
                    "recovery_error",
                    reconnect_attempt=reconnect_attempt,
                    http_attempt=http_attempt,
                    attempts_total=self.config.recovery_http_attempts,
                    error_type=type(exc).__name__,
                    error=str(exc),
                    elapsed_ms=round((time.monotonic() - recovery_started) * 1000, 1),
                )
                if http_attempt < self.config.recovery_http_attempts:
                    try:
                        await asyncio.wait_for(
                            self.stop_event.wait(), timeout=float(http_attempt)
                        )
                        return False
                    except asyncio.TimeoutError:
                        pass
        await self.audit(
            symbol,
            "recovery_exhausted",
            reconnect_attempt=reconnect_attempt,
            attempts_total=self.config.recovery_http_attempts,
            last_source_time=self.last_source_time.get(symbol),
            elapsed_ms=round((time.monotonic() - recovery_started) * 1000, 1),
        )
        return False

    async def stream_once(self, symbol: str, reconnect_attempt: int) -> None:
        connection_id = f"{symbol}-{uuid.uuid4().hex}"
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
        decoder = SSEDecoder()
        frame_sequence = 0
        detail_sequence = 0
        connected = False
        timeout = httpx.Timeout(connect=10, read=None, write=10, pool=10)
        async with self.connect_semaphore:
            stream_context = self.client.stream(
                "GET",
                SSE_URL,
                params=params,
                headers={"Accept": "text/event-stream", "Cache-Control": "no-cache"},
                timeout=timeout,
            )
            response = await stream_context.__aenter__()
        try:
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "text/event-stream" not in content_type.lower():
                raise RuntimeError(f"SSE Content-Type 异常: {content_type!r}")
            self.stats.sse_active += 1
            connected = True
            self.stream_connected_at[symbol] = time.monotonic()
            self.stream_frames[symbol] = 0
            self.stream_generation[symbol] += 1
            self.stats.sse_connects += 1
            await self.audit(
                symbol,
                "connected",
                connection_id=connection_id,
                reconnect_attempt=reconnect_attempt,
                http_status=response.status_code,
                content_type=content_type,
            )
            async for line in response.aiter_lines():
                if self.stop_event.is_set():
                    return
                for payload_text in decoder.feed(line):
                    frame_sequence += 1
                    self.stats.sse_frames += 1
                    self.stream_frames[symbol] += 1
                    try:
                        payload = json.loads(payload_text)
                        full = payload.get("full")
                        details = (payload.get("data") or {}).get("details") or []
                        received_at = now_iso()
                        for raw in details:
                            detail_sequence += 1
                            record = normalize_trade(
                                symbol=symbol,
                                raw=raw,
                                trade_date=current_trade_date(False),
                                received_at=received_at,
                                source_kind="sse",
                                connection_id=connection_id,
                                frame_sequence=frame_sequence,
                                detail_sequence=detail_sequence,
                                full=full,
                                recovered=False,
                                reconnect_attempt=reconnect_attempt,
                            )
                            await self.accept_trade(record)
                    except Exception as exc:
                        self.stats.parse_failures += 1
                        await self.audit(
                            symbol,
                            "sse_parse_error",
                            connection_id=connection_id,
                            frame_sequence=frame_sequence,
                            error_type=type(exc).__name__,
                            error=str(exc),
                            payload_preview=payload_text[:500],
                        )
            if not self.stop_event.is_set():
                raise EOFError("SSE 连接读取到 EOF")
        finally:
            if connected:
                self.stats.sse_active -= 1
            await stream_context.__aexit__(None, None, None)

    async def recover_after(
        self,
        previous: asyncio.Task[bool] | None,
        symbol: str,
        reconnect_attempt: int,
    ) -> bool:
        """Serialize a symbol's recovery jobs without blocking SSE reconnects."""

        if previous is not None:
            try:
                await previous
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                await self.audit(
                    symbol,
                    "recovery_chain_error",
                    reconnect_attempt=reconnect_attempt,
                    error_type=type(exc).__name__,
                    error=str(exc),
                )
        if self.stop_event.is_set():
            return False
        return await self.recover(symbol, reconnect_attempt)

    async def supervise_symbol(self, symbol: str, initial_delay: float = 0.0) -> None:
        if initial_delay > 0:
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=initial_delay)
                return
            except asyncio.TimeoutError:
                pass
        reconnect_attempt = 0
        recovery_task: asyncio.Task[bool] | None = asyncio.create_task(
            self.recover(symbol, reconnect_attempt=0), name=f"recovery-{symbol}-0"
        )
        try:
            while not self.stop_event.is_set():
                generation_before = self.stream_generation[symbol]
                try:
                    await self.stream_once(symbol, reconnect_attempt)
                    if self.stop_event.is_set():
                        return
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self.stats.sse_disconnects += 1
                    connected_this_attempt = (
                        self.stream_generation[symbol] > generation_before
                    )
                    connected_seconds = (
                        max(
                            0.0,
                            time.monotonic()
                            - self.stream_connected_at.get(symbol, time.monotonic()),
                        )
                        if connected_this_attempt
                        else 0.0
                    )
                    stable_connection = (
                        connected_this_attempt
                        and connected_seconds >= 30
                        and self.stream_frames.get(symbol, 0) > 0
                    )
                    reconnect_attempt = 1 if stable_connection else reconnect_attempt + 1
                    await self.audit(
                        symbol,
                        "disconnected",
                        reconnect_attempt=reconnect_attempt,
                        error_type=type(exc).__name__,
                        error=str(exc),
                        last_source_time=self.last_source_time.get(symbol),
                        connected_seconds=round(connected_seconds, 1),
                        frames_before_disconnect=self.stream_frames.get(symbol, 0),
                        connected_this_attempt=connected_this_attempt,
                        backoff_reset=stable_connection,
                    )
                    if connected_this_attempt or recovery_task is None or recovery_task.done():
                        recovery_task = asyncio.create_task(
                            self.recover_after(recovery_task, symbol, reconnect_attempt),
                            name=f"recovery-{symbol}-{reconnect_attempt}",
                        )

                base = self.config.backoff_seconds[
                    min(reconnect_attempt - 1, len(self.config.backoff_seconds) - 1)
                ]
                delay = max(
                    0.1,
                    base
                    * random.uniform(
                        1 - self.config.jitter_ratio, 1 + self.config.jitter_ratio
                    ),
                )
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass
        finally:
            if recovery_task is not None and not recovery_task.done():
                recovery_task.cancel()
            if recovery_task is not None:
                await asyncio.gather(recovery_task, return_exceptions=True)

    async def fetch_quote(self, symbol: str) -> dict[str, Any]:
        params = {
            "ut": UT,
            "_": int(time.time() * 1000),
            "secid": to_secid(symbol),
            "invt": 2,
            "fltt": 2,
            "wbp2u": "|0|0|0|web",
            "dect": 1,
            "fields": QUOTE_FIELDS,
        }
        async with self.quote_semaphore:
            response = await self.client.get(f"{BASE_URL}/get", params=params, timeout=10.0)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data")
        if payload.get("rc") != 0 or not isinstance(data, dict):
            raise RuntimeError(f"stock/get 无有效 data: rc={payload.get('rc')}")

        def number(key: str) -> float | None:
            value = data.get(key)
            return None if value in (None, "", "-") else float(value)

        def levels(fields: tuple[tuple[str, str], ...]) -> list[dict[str, Any]]:
            result = []
            for level, (price_key, volume_key) in enumerate(fields, 1):
                price = number(price_key)
                volume = number(volume_key)
                if price is None or volume is None:
                    return []
                result.append({"level": level, "price": price, "volume_lots": int(volume)})
            return result

        bids = levels(BID_FIELDS)
        asks = levels(ASK_FIELDS)
        return {
            "stream": "quotes",
            "schema_version": 1,
            "trade_date": current_trade_date(True),
            "symbol": symbol,
            "received_at": now_iso(),
            "source_time_epoch": int(number("f86")) if number("f86") is not None else None,
            "price": number("f43"),
            "open": number("f46"),
            "high": number("f44"),
            "low": number("f45"),
            "pre_close": number("f60"),
            "volume_lots": int(number("f47")) if number("f47") is not None else None,
            "amount_cny": number("f48"),
            "order_book_available": len(bids) == 5 and len(asks) == 5,
            "bids": bids,
            "asks": asks,
        }

    async def poll_symbol_quotes(self, symbol: str, initial_delay: float) -> None:
        try:
            await asyncio.wait_for(self.stop_event.wait(), timeout=initial_delay)
            return
        except asyncio.TimeoutError:
            pass
        next_run = time.monotonic()
        while not self.stop_event.is_set():
            started = time.monotonic()
            try:
                quote = await self.fetch_quote(symbol)
                quote["elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
                self.stats.quote_successes += 1
                await self.emit(quote)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.stats.quote_failures += 1
                await self.audit(
                    symbol,
                    "quote_error",
                    error_type=type(exc).__name__,
                    error=str(exc),
                    elapsed_ms=round((time.monotonic() - started) * 1000, 1),
                )
            next_run += self.config.quote_interval
            if next_run < time.monotonic():
                next_run = time.monotonic()
            delay = max(0.0, next_run - time.monotonic())
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass

    async def report_metrics(self) -> None:
        process = psutil.Process()
        process.cpu_percent(interval=None)
        while not self.stop_event.is_set():
            try:
                await asyncio.wait_for(
                    self.stop_event.wait(), timeout=self.config.metrics_interval
                )
                return
            except asyncio.TimeoutError:
                pass
            try:
                memory = process.memory_info()
                await self.emit(
                    {
                        "stream": "metrics",
                        "schema_version": 1,
                        "trade_date": current_trade_date(True),
                        "received_at": now_iso(),
                        "symbol_count": len(self.config.symbols),
                        "queue_size": self.queue.qsize(),
                        "queue_capacity": self.queue.maxsize,
                        "writer_records": self.writer.records_written,
                        "process_cpu_percent": process.cpu_percent(interval=None),
                        "process_rss_mib": round(memory.rss / 1024 / 1024, 2),
                        "open_files": len(process.open_files()),
                        "connections": len(process.net_connections(kind="inet")),
                        **{
                            name: getattr(self.stats, name)
                            for name in self.stats.__dataclass_fields__
                        },
                    }
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                await self.audit(
                    None,
                    "metrics_error",
                    error_type=type(exc).__name__,
                    error=str(exc),
                )

    def create_market_tasks(self) -> list[asyncio.Task[Any]]:
        tasks: list[asyncio.Task[Any]] = []
        symbol_count = len(self.config.symbols)
        for index, symbol in enumerate(self.config.symbols):
            sse_offset = self.config.startup_spread_seconds * index / symbol_count
            tasks.append(
                asyncio.create_task(
                    self.supervise_symbol(symbol, sse_offset), name=f"sse-{symbol}"
                )
            )
            quote_offset = self.config.quote_interval * index / symbol_count
            tasks.append(
                asyncio.create_task(
                    self.poll_symbol_quotes(symbol, quote_offset), name=f"quote-{symbol}"
                )
            )
        return tasks

    async def run_market_hours(self) -> None:
        """Run network tasks only in weekday A-share collection windows."""

        while not self.stop_event.is_set():
            window_start, window_end, label = next_market_window()
            delay = (window_start - datetime.now(CHINA_TZ)).total_seconds()
            if delay > 0:
                await self.audit(
                    None,
                    "waiting_for_market_window",
                    window=label,
                    window_start=window_start.isoformat(),
                    seconds_until_start=round(delay, 1),
                    note="仅按工作日判断，法定休市日仍会尝试连接",
                )
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=delay)
                    return
                except asyncio.TimeoutError:
                    pass
            await self.audit(
                None,
                "market_window_starting",
                window=label,
                window_end=window_end.isoformat(),
                symbol_count=len(self.config.symbols),
                symbols=self.config.symbols,
            )
            tasks = self.create_market_tasks()
            remaining = max(0.0, (window_end - datetime.now(CHINA_TZ)).total_seconds())
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                pass
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                await self.audit(None, "market_window_stopped", window=label)

    async def run(self, duration: float | None = None, market_hours: bool = False) -> None:
        trade_path = (
            self.config.output_dir / current_trade_date(True) / "trades.jsonl"
        )
        restored = restore_recent_trade_state(
            trade_path,
            symbols=set(self.config.symbols),
            deduper=self.deduper,
        )
        self.last_source_time.update(restored["last_source_time"])
        self.last_dedupe_key.update(restored["last_dedupe_key"])
        await self.audit(
            None,
            "collector_starting",
            symbol_count=len(self.config.symbols),
            symbols=self.config.symbols,
            output_dir=str(self.config.output_dir),
            quote_interval=self.config.quote_interval,
            recovery_limit=self.config.recovery_limit,
            startup_spread_seconds=self.config.startup_spread_seconds,
            market_hours=market_hours,
            restored_records=restored["records_restored"],
            restore_bytes_scanned=restored["bytes_scanned"],
            restore_trailing_partial_lines=restored["trailing_partial_lines"],
        )
        writer_task = asyncio.create_task(self.writer.run(), name="jsonl-writer")
        writer_task.add_done_callback(lambda _: self.stop_event.set())
        tasks: list[asyncio.Task[Any]] = [
            asyncio.create_task(self.report_metrics(), name="metrics")
        ]
        if market_hours:
            tasks.append(asyncio.create_task(self.run_market_hours(), name="market-scheduler"))
        else:
            tasks.extend(self.create_market_tasks())
        try:
            if duration is None:
                await self.stop_event.wait()
            else:
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=duration)
                except asyncio.TimeoutError:
                    self.stop_event.set()
        finally:
            self.stop_event.set()
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            writer_error = writer_task.exception() if writer_task.done() else None
            if writer_error is None:
                await self.audit(
                    None,
                    "collector_stopped",
                    writer_records=self.writer.records_written,
                    queue_size=self.queue.qsize(),
                )
                await self.queue.put(None)
            await self.client.aclose()
            await writer_task


def resolve_module_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (CURRENT_DIR / path).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="东方财富100股票 SSE 正式采集器")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--symbols-file", help="股票池文件；相对路径按 realtime_alert/ 解析")
    source.add_argument("--symbol", action="append", help="可重复指定，最多100只")
    parser.add_argument("--output-dir", default="data", help="输出目录；相对路径按 realtime_alert/ 解析")
    parser.add_argument("--duration", type=float, help="诊断运行秒数；正式运行时省略")
    parser.add_argument("--quote-interval", type=float, default=3.0)
    parser.add_argument("--recovery-limit", type=int, default=20)
    parser.add_argument("--metrics-interval", type=float, default=60.0)
    parser.add_argument(
        "--market-hours",
        action="store_true",
        help="仅在工作日 09:20–11:35、12:55–15:10 连接；不含法定节假日日历",
    )
    return parser


async def async_main(args: argparse.Namespace) -> None:
    if args.symbols_file:
        symbols = load_symbols(resolve_module_path(args.symbols_file), max_symbols=100)
    else:
        symbols = list(dict.fromkeys(canonical_symbol(value) for value in args.symbol))
    config = CollectorConfig(
        symbols=symbols,
        output_dir=resolve_module_path(args.output_dir),
        quote_interval=args.quote_interval,
        recovery_limit=args.recovery_limit,
        metrics_interval=args.metrics_interval,
    )
    collector = EastmoneySSECollector(config)
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signal_name, collector.stop_event.set)
        except (NotImplementedError, RuntimeError):
            pass
    print(
        json.dumps(
            {
                "status": "starting",
                "symbols": len(symbols),
                "output_dir": str(config.output_dir),
                "duration": args.duration,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    await collector.run(duration=args.duration, market_hours=args.market_hours)
    print(json.dumps({"status": "stopped", "at": now_iso()}, ensure_ascii=False), flush=True)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.duration is not None and args.duration <= 0:
        parser.error("--duration 必须大于 0")
    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
