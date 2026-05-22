from __future__ import annotations

import argparse
import csv
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator
from zoneinfo import ZoneInfo

from get_data_cls.backfill_cls_telegraph_raw_reverse import (
    CHECKPOINT_PATH,
    LOG_DIR,
    BackfillConfig,
    format_local_timestamp,
    load_checkpoint,
    run_backfill,
)


CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.resolve()
TIMEZONE = ZoneInfo("Asia/Shanghai")
DEFAULT_SLEEP_SECONDS = 30 * 60
LOOP_LOG_PATH = LOG_DIR / "cls_raw_reverse_loop_log.csv"
LOCK_PATH = LOG_DIR / "cls_raw_reverse_loop.lock"


def local_now_text() -> str:
    return datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def append_loop_log(row: dict[str, Any], path: Path = LOOP_LOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "loop_id",
        "started_at",
        "finished_at",
        "status",
        "completed",
        "last_time",
        "last_ctime",
        "total_pages",
        "total_rows",
        "sleep_seconds",
        "error_message",
    ]
    write_header = not path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in fieldnames})


@contextmanager
def loop_lock(path: Path = LOCK_PATH) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"循环任务疑似已在运行，锁文件已存在：{path}") from exc

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "pid": os.getpid(),
                    "started_at": local_now_text(),
                    "command": "python -m get_data_cls.run_cls_raw_reverse_loop",
                },
                file,
                ensure_ascii=False,
                indent=2,
            )
        yield
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def checkpoint_completed() -> bool:
    checkpoint = load_checkpoint()
    return bool(checkpoint and checkpoint.get("completed"))


def checkpoint_summary(checkpoint: dict[str, Any] | None) -> dict[str, Any]:
    if not checkpoint:
        return {
            "completed": "",
            "last_time": "",
            "last_ctime": "",
            "total_pages": "",
            "total_rows": "",
        }
    last_time = checkpoint.get("last_time", "")
    return {
        "completed": bool(checkpoint.get("completed")),
        "last_time": last_time,
        "last_ctime": checkpoint.get("last_ctime") or format_local_timestamp(last_time),
        "total_pages": checkpoint.get("total_pages", ""),
        "total_rows": checkpoint.get("total_rows", ""),
    }


def run_loop(
    sleep_seconds: int = DEFAULT_SLEEP_SECONDS,
    max_runs: int | None = None,
    stop_on_error: bool = False,
) -> None:
    if sleep_seconds < 0:
        raise ValueError("sleep_seconds 不能为负数")
    if max_runs is not None and max_runs < 0:
        raise ValueError("max_runs 不能为负数")

    print(f"loop log: {LOOP_LOG_PATH}")
    print(f"checkpoint: {CHECKPOINT_PATH}")
    print(f"sleep_seconds: {sleep_seconds}")

    if max_runs == 0:
        return

    runs_finished = 0
    with loop_lock():
        while True:
            if checkpoint_completed():
                print("checkpoint 已完成，循环退出。")
                break
            if max_runs is not None and runs_finished >= max_runs:
                print(f"已达到 max_runs={max_runs}，循环退出。")
                break

            loop_id = datetime.now(tz=TIMEZONE).strftime("%Y%m%d_%H%M%S")
            started_at = local_now_text()
            status = "running"
            error_message = ""
            checkpoint: dict[str, Any] | None = None

            print(f"[{started_at}] 开始第 {runs_finished + 1} 轮 full-fields 倒序抓取。")
            try:
                checkpoint = run_backfill(BackfillConfig())
                status = "completed" if bool(checkpoint.get("completed")) else "partial"
            except Exception as exc:
                status = "failed"
                error_message = str(exc)
                checkpoint = load_checkpoint()
                print(f"[{local_now_text()}] 本轮失败：{error_message}")
                if stop_on_error:
                    append_loop_log(
                        {
                            "loop_id": loop_id,
                            "started_at": started_at,
                            "finished_at": local_now_text(),
                            "status": status,
                            "sleep_seconds": "",
                            "error_message": error_message,
                            **checkpoint_summary(checkpoint),
                        }
                    )
                    raise
            finally:
                if status != "running":
                    finished_at = local_now_text()
                    append_loop_log(
                        {
                            "loop_id": loop_id,
                            "started_at": started_at,
                            "finished_at": finished_at,
                            "status": status,
                            "sleep_seconds": sleep_seconds if status != "completed" else 0,
                            "error_message": error_message,
                            **checkpoint_summary(checkpoint),
                        }
                    )
                    print(f"[{finished_at}] 本轮结束，status={status}。")

            runs_finished += 1
            if checkpoint and checkpoint.get("completed"):
                print("已抓到历史终点，循环退出。")
                break
            if max_runs is not None and runs_finished >= max_runs:
                print(f"已达到 max_runs={max_runs}，循环退出。")
                break

            print(f"[{local_now_text()}] 休息 {sleep_seconds} 秒后继续。Ctrl+C 可停止循环。")
            time.sleep(sleep_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="循环运行财联社 full-fields raw 倒序抓取。")
    parser.add_argument(
        "--sleep-seconds",
        type=int,
        default=DEFAULT_SLEEP_SECONDS,
        help="每轮结束后的休息秒数，默认 1800 秒。",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="最多运行多少轮；不指定则持续运行到 checkpoint completed=true。",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="单轮失败后立即退出；默认记录失败并休息后继续。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_loop(
        sleep_seconds=args.sleep_seconds,
        max_runs=args.max_runs,
        stop_on_error=args.stop_on_error,
    )


if __name__ == "__main__":
    main()
