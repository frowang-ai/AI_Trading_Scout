from __future__ import annotations

import csv
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

from get_data_cls.fetcher_telegraph import (
    DEFAULT_APP,
    DEFAULT_RN,
    DEFAULT_SV,
    REQUEST_TIMEOUT_SECONDS,
    ROLL_LIST_URL,
    get_sign,
)


CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.resolve()
RAW_BASE_DIR = PROJECT_ROOT / "data" / "raw" / "cls_telegraph" / "full_fields_reverse"
CHUNK_DIR = RAW_BASE_DIR / "chunks"
CHECKPOINT_DIR = RAW_BASE_DIR / "checkpoint"
LOG_DIR = RAW_BASE_DIR / "logs"
CHECKPOINT_PATH = CHECKPOINT_DIR / "cls_raw_reverse_checkpoint.json"
RUN_LOG_PATH = LOG_DIR / "cls_raw_reverse_run_log.csv"

START_LAST_TIME = "2026-05-21 20:22:00"
STOP_TIME = "2014-03-29 19:17:57"
PAGES_PER_RUN = 240
SLEEP_MIN_SECONDS = 8
SLEEP_MAX_SECONDS = 12
MAX_RETRIES = 3
TIMEZONE = ZoneInfo("Asia/Shanghai")


@dataclass(frozen=True)
class BackfillConfig:
    start_last_time: str = START_LAST_TIME
    stop_time: str = STOP_TIME
    pages_per_run: int = PAGES_PER_RUN
    sleep_min_seconds: float = SLEEP_MIN_SECONDS
    sleep_max_seconds: float = SLEEP_MAX_SECONDS
    max_retries: int = MAX_RETRIES


def parse_local_timestamp(value: str) -> int:
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=TIMEZONE)
    except ValueError as exc:
        raise ValueError(f"时间格式必须是 YYYY-MM-DD HH:MM:SS：{value}") from exc
    return int(dt.timestamp())


def format_local_timestamp(value: int | float | str | None) -> str:
    if value is None or value == "":
        return ""
    try:
        timestamp = int(float(value))
    except (TypeError, ValueError):
        return str(value)
    return datetime.fromtimestamp(timestamp, tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def utc_now_text() -> str:
    return datetime.now(tz=ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S%z")


def ensure_dirs() -> None:
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_checkpoint(path: Path = CHECKPOINT_PATH) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_checkpoint(checkpoint: dict[str, Any], path: Path = CHECKPOINT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(checkpoint, file, ensure_ascii=False, indent=2)
    temp_path.replace(path)


def next_chunk_path() -> Path:
    existing = sorted(CHUNK_DIR.glob("cls_raw_part_*.jsonl"))
    if not existing:
        return CHUNK_DIR / "cls_raw_part_000001.jsonl"
    last_stem = existing[-1].stem
    last_index = int(last_stem.rsplit("_", maxsplit=1)[-1])
    return CHUNK_DIR / f"cls_raw_part_{last_index + 1:06d}.jsonl"


def append_run_log(row: dict[str, Any], path: Path = RUN_LOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_id",
        "started_at",
        "finished_at",
        "start_last_time",
        "end_last_time",
        "pages_requested",
        "pages_succeeded",
        "rows_written",
        "chunk_path",
        "status",
        "error_message",
    ]
    write_header = not path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in fieldnames})


def request_roll_page(session: requests.Session, last_time: int) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "refresh_type": "1",
        "rn": str(DEFAULT_RN),
        "last_time": last_time,
        "app": DEFAULT_APP,
        "sv": DEFAULT_SV,
    }
    params["sign"] = get_sign(params)

    try:
        response = session.get(ROLL_LIST_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data_json = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"请求财联社电报接口失败：{exc}") from exc
    except ValueError as exc:
        raise RuntimeError("财联社电报接口返回内容不是合法 JSON") from exc

    roll_data = data_json.get("data", {}).get("roll_data", [])
    if not isinstance(roll_data, list):
        raise RuntimeError("财联社电报接口 roll_data 不是 list")
    return roll_data


def request_roll_page_with_retries(
    session: requests.Session,
    last_time: int,
    max_retries: int,
) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            roll_data = request_roll_page(session, last_time)
            if not roll_data:
                raise RuntimeError(f"财联社电报接口返回空 roll_data，last_time={last_time}")
            return roll_data
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(min(2 * attempt, 10))
    raise RuntimeError(f"重试 {max_retries} 次后仍失败：{last_error}") from last_error


def initial_checkpoint(config: BackfillConfig) -> dict[str, Any]:
    start_last_time = parse_local_timestamp(config.start_last_time)
    return {
        "last_time": start_last_time,
        "last_ctime": format_local_timestamp(start_last_time),
        "total_pages": 0,
        "total_rows": 0,
        "last_chunk": "",
        "completed": False,
        "updated_at": utc_now_text(),
    }


def attach_metadata(
    record: dict[str, Any],
    fetched_at: str,
    request_last_time: int,
    page_index: int,
    run_id: str,
) -> dict[str, Any]:
    enriched = dict(record)
    enriched["fetched_at"] = fetched_at
    enriched["request_last_time"] = request_last_time
    enriched["page_index"] = page_index
    enriched["run_id"] = run_id
    return enriched


def newest_next_time(roll_data: list[dict[str, Any]]) -> int:
    last_record = roll_data[-1]
    sort_score = last_record.get("sort_score")
    if sort_score is None:
        raise RuntimeError("页面最后一条记录缺少 sort_score，无法继续翻页")
    return int(float(sort_score))


def run_backfill(config: BackfillConfig = BackfillConfig()) -> dict[str, Any]:
    if config.pages_per_run <= 0:
        raise ValueError("pages_per_run 必须大于 0")
    if config.sleep_min_seconds < 0 or config.sleep_max_seconds < config.sleep_min_seconds:
        raise ValueError("sleep 秒数范围不合法")

    ensure_dirs()
    checkpoint = load_checkpoint() or initial_checkpoint(config)
    stop_timestamp = parse_local_timestamp(config.stop_time)
    start_last_time = int(checkpoint["last_time"])
    run_id = datetime.now(tz=TIMEZONE).strftime("%Y%m%d_%H%M%S")
    chunk_path = next_chunk_path()
    started_at = utc_now_text()
    pages_succeeded = 0
    rows_written = 0
    status = "running"
    error_message = ""
    current_last_time = start_last_time

    if bool(checkpoint.get("completed")) or current_last_time <= stop_timestamp:
        status = "completed"
        checkpoint["completed"] = True
        checkpoint["updated_at"] = utc_now_text()
        write_checkpoint(checkpoint)
        finished_at = utc_now_text()
        append_run_log(
            {
                "run_id": run_id,
                "started_at": started_at,
                "finished_at": finished_at,
                "start_last_time": start_last_time,
                "end_last_time": current_last_time,
                "pages_requested": config.pages_per_run,
                "pages_succeeded": 0,
                "rows_written": 0,
                "chunk_path": "",
                "status": status,
                "error_message": "checkpoint 已完成或已到达 STOP_TIME",
            }
        )
        return checkpoint

    session = requests.Session()
    try:
        with chunk_path.open("a", encoding="utf-8") as file:
            for page_index in range(1, config.pages_per_run + 1):
                if current_last_time <= stop_timestamp:
                    status = "completed"
                    checkpoint["completed"] = True
                    break

                roll_data = request_roll_page_with_retries(
                    session=session,
                    last_time=current_last_time,
                    max_retries=config.max_retries,
                )
                fetched_at = utc_now_text()
                for record in roll_data:
                    enriched = attach_metadata(
                        record=record,
                        fetched_at=fetched_at,
                        request_last_time=current_last_time,
                        page_index=page_index,
                        run_id=run_id,
                    )
                    file.write(json.dumps(enriched, ensure_ascii=False, separators=(",", ":")) + "\n")

                pages_succeeded += 1
                rows_written += len(roll_data)
                current_last_time = newest_next_time(roll_data)
                checkpoint.update(
                    {
                        "last_time": current_last_time,
                        "last_ctime": format_local_timestamp(
                            roll_data[-1].get("ctime") or current_last_time
                        ),
                        "total_pages": int(checkpoint.get("total_pages", 0)) + 1,
                        "total_rows": int(checkpoint.get("total_rows", 0)) + len(roll_data),
                        "last_chunk": str(chunk_path),
                        "completed": current_last_time <= stop_timestamp,
                        "updated_at": utc_now_text(),
                    }
                )
                write_checkpoint(checkpoint)

                print(
                    f"page={page_index} rows={len(roll_data)} "
                    f"next_last_time={current_last_time} "
                    f"next_ctime={checkpoint['last_ctime']}"
                )

                if current_last_time <= stop_timestamp:
                    status = "completed"
                    break

                if page_index < config.pages_per_run:
                    time.sleep(random.uniform(config.sleep_min_seconds, config.sleep_max_seconds))
        if status == "running":
            status = "partial"
    except Exception as exc:
        status = "failed"
        error_message = str(exc)
        print(f"本轮停止：{error_message}")
    finally:
        finished_at = utc_now_text()
        append_run_log(
            {
                "run_id": run_id,
                "started_at": started_at,
                "finished_at": finished_at,
                "start_last_time": start_last_time,
                "end_last_time": current_last_time,
                "pages_requested": config.pages_per_run,
                "pages_succeeded": pages_succeeded,
                "rows_written": rows_written,
                "chunk_path": str(chunk_path) if rows_written else "",
                "status": status,
                "error_message": error_message,
            }
        )

    if status == "failed":
        raise RuntimeError(error_message)
    return checkpoint


def main() -> None:
    checkpoint = run_backfill()
    print(json.dumps(checkpoint, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
