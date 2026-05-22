from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from get_data_cls.fetcher_telegraph import fetch_cls_telegraph


CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.resolve()
INCREMENTAL_DIR = PROJECT_ROOT / "data" / "raw" / "cls_telegraph" / "incremental_20250210_20260521"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "cls_telegraph"
REPORT_DIR = PROJECT_ROOT / "data" / "reports" / "cls_telegraph"

START_TIME = "2025-02-10 23:37:25"
END_TIME = "2026-05-21 20:22:00"


def iter_month_windows(start_time: str, end_time: str) -> list[tuple[str, str]]:
    start = pd.Timestamp(start_time)
    end = pd.Timestamp(end_time)
    windows: list[tuple[str, str]] = []
    cursor = start
    while cursor < end:
        next_month = (cursor + pd.offsets.MonthBegin(1)).replace(hour=0, minute=0, second=0)
        chunk_end = min(next_month, end)
        windows.append((cursor.strftime("%Y-%m-%d %H:%M:%S"), chunk_end.strftime("%Y-%m-%d %H:%M:%S")))
        cursor = chunk_end
    return windows


def safe_name(start_time: str, end_time: str) -> str:
    start_part = start_time.replace("-", "").replace(":", "").replace(" ", "_")
    end_part = end_time.replace("-", "").replace(":", "").replace(" ", "_")
    return f"cls_telegraph_{start_part}_{end_part}.csv"


def backfill_incremental() -> None:
    INCREMENTAL_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for start_time, end_time in iter_month_windows(START_TIME, END_TIME):
        output_path = INCREMENTAL_DIR / safe_name(start_time, end_time)
        if output_path.exists():
            existing = pd.read_csv(output_path, nrows=5, encoding="utf-8-sig")
            print(f"跳过已存在分块：{output_path.name}；预览行数={len(existing)}")
            continue

        print(f"\n抓取分块：{start_time} -> {end_time}")
        df = fetch_cls_telegraph(start_time, end_time)
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        rows.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "rows": len(df),
                "output_path": str(output_path),
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        print(f"写入：{output_path}；rows={len(df)}")

    summary_path = REPORT_DIR / "_test_cls_incremental_backfill_chunks.csv"
    if rows:
        pd.DataFrame(rows).to_csv(summary_path, index=False, encoding="utf-8-sig")
        print(f"写入分块摘要：{summary_path}")


if __name__ == "__main__":
    backfill_incremental()
