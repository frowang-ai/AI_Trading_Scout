from __future__ import annotations

import json
from pathlib import Path

from get_data_cls.backfill_cls_telegraph_raw_reverse import (
    CHECKPOINT_PATH,
    CHUNK_DIR,
    BackfillConfig,
    load_checkpoint,
    run_backfill,
)


REQUIRED_FIELDS = ["category", "tags", "subjects", "plate_list", "stock_list"]


def latest_chunk() -> Path:
    chunk_paths = sorted(CHUNK_DIR.glob("*.jsonl"))
    if not chunk_paths:
        raise FileNotFoundError(f"探针未生成 JSONL 分块：{CHUNK_DIR}")
    return chunk_paths[-1]


def read_jsonl_head(path: Path, limit: int = 100) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line_number > limit:
                break
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"JSONL 非法：{path} line={line_number}；{exc}") from exc
            if not isinstance(row, dict):
                raise AssertionError(f"JSONL 行不是 object：{path} line={line_number}")
            rows.append(row)
    return rows


def main() -> None:
    checkpoint_before = load_checkpoint()
    if checkpoint_before:
        print(
            "checkpoint before: "
            f"last_time={checkpoint_before.get('last_time')} "
            f"total_pages={checkpoint_before.get('total_pages')} "
            f"total_rows={checkpoint_before.get('total_rows')}"
        )
    else:
        print("checkpoint before: none")

    checkpoint_after = run_backfill(
        BackfillConfig(
            pages_per_run=5,
            sleep_min_seconds=1,
            sleep_max_seconds=2,
            max_retries=3,
        )
    )

    chunk_path = latest_chunk()
    rows = read_jsonl_head(chunk_path)
    if not rows:
        raise AssertionError(f"JSONL 分块为空：{chunk_path}")

    missing_meta = [
        field
        for field in ["fetched_at", "request_last_time", "page_index", "run_id"]
        if field not in rows[0]
    ]
    if missing_meta:
        raise AssertionError(f"采集元数据字段缺失：{missing_meta}")

    field_presence = {
        field: sum(1 for row in rows if field in row and row.get(field) not in (None, "", []))
        for field in REQUIRED_FIELDS
    }

    if not CHECKPOINT_PATH.exists():
        raise AssertionError(f"checkpoint 未生成：{CHECKPOINT_PATH}")
    if int(checkpoint_after.get("total_pages", 0)) <= int((checkpoint_before or {}).get("total_pages", 0)):
        raise AssertionError("checkpoint total_pages 未推进，续跑断点可能异常")

    print(f"latest chunk: {chunk_path}")
    print(f"sample rows checked: {len(rows)}")
    print(f"required field non-empty counts in sample: {field_presence}")
    print(
        "checkpoint after: "
        f"last_time={checkpoint_after.get('last_time')} "
        f"last_ctime={checkpoint_after.get('last_ctime')} "
        f"total_pages={checkpoint_after.get('total_pages')} "
        f"total_rows={checkpoint_after.get('total_rows')}"
    )


if __name__ == "__main__":
    main()
