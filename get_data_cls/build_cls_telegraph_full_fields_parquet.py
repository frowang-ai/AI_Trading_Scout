from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.resolve()
RAW_BASE_DIR = PROJECT_ROOT / "data" / "raw" / "cls_telegraph" / "full_fields_reverse"
CHUNK_DIR = RAW_BASE_DIR / "chunks"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "cls_telegraph"
REPORT_DIR = PROJECT_ROOT / "data" / "reports" / "cls_telegraph"
OUTPUT_PATH = PROCESSED_DIR / "cls_telegraph_full_fields_2014_20260521.parquet"
SCHEMA_REPORT_PATH = REPORT_DIR / "_test_cls_full_fields_schema_report.csv"
SUMMARY_REPORT_PATH = REPORT_DIR / "_test_cls_full_fields_summary.csv"
TIMEZONE = ZoneInfo("Asia/Shanghai")

COMPLEX_COLUMNS = ["stock_list", "plate_list", "tags", "subjects"]
REPORT_COLUMNS = ["category", "tags", "subjects", "stock_list", "plate_list"]
OUTPUT_COLUMNS = [
    "id",
    "title",
    "content",
    "brief",
    "publish_time",
    "ctime",
    "sort_score",
    "category",
    "level",
    "raw_type",
    "is_ad",
    "assocArticleUrl",
    "stock_list_json",
    "plate_list_json",
    "tags_json",
    "subjects_json",
    "stock_name",
    "stock_code",
    "plate_name",
    "md5",
    "source_chunk",
    "fetched_at",
]


def is_present(value: Any) -> bool:
    return value is not None and value != "" and value != []


def md5_text(value: Any) -> str:
    text = "" if value is None else str(value)
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def json_text(value: Any) -> str:
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def iter_jsonl(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSONL 非法：{path} line={line_number}；{exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"JSONL 行不是 object：{path} line={line_number}")
            row["source_chunk"] = path.name
            yield row


class SchemaStats:
    def __init__(self) -> None:
        self.total_rows = 0
        self.non_null_rows: dict[str, int] = {}
        self.sample_values: dict[str, str] = {}

    def add(self, row: dict[str, Any]) -> None:
        self.total_rows += 1
        for column, value in row.items():
            self.non_null_rows.setdefault(column, 0)
            if is_present(value):
                self.non_null_rows[column] += 1
                self.sample_values.setdefault(column, json_text(value))

    def to_frame(self) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        for column in sorted(self.non_null_rows):
            non_null = self.non_null_rows[column]
            rows.append(
                {
                    "field": column,
                    "non_null_rows": non_null,
                    "total_rows": self.total_rows,
                    "non_null_rate": non_null / self.total_rows if self.total_rows else 0,
                    "sample_value": self.sample_values.get(column, ""),
                }
            )
        return pd.DataFrame(rows)


def first_values(items: Any, keys: list[str]) -> str:
    if not isinstance(items, list):
        return ""
    values: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in keys:
            value = item.get(key)
            if value:
                values.append(str(value))
                break
    return ",".join(values)


def normalize_stock_code(code: Any) -> str:
    if code is None or code == "":
        return ""
    normalized = str(code).replace("sz", "").replace("sh", "")
    if normalized.startswith(("0", "3")) and len(normalized) == 6:
        return f"{normalized}.SZ"
    if normalized.startswith("6") and len(normalized) == 6:
        return f"{normalized}.SH"
    return normalized


def stock_codes(stock_list: Any) -> str:
    if not isinstance(stock_list, list):
        return ""
    codes: list[str] = []
    for item in stock_list:
        if not isinstance(item, dict):
            continue
        raw_code = item.get("StockID") or item.get("stock_id") or item.get("code")
        code = normalize_stock_code(raw_code)
        if code:
            codes.append(code)
    return ",".join(codes)


def to_publish_time(ctime: Any) -> pd.Timestamp | pd.NaT:
    if ctime is None or ctime == "":
        return pd.NaT
    return pd.to_datetime(ctime, unit="s", utc=True, errors="coerce").tz_convert(TIMEZONE).tz_localize(None)


def raw_records_to_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    for column in ["id", "title", "content", "brief", "ctime", "sort_score", "category", "level", "type", "is_ad", "assocArticleUrl", "fetched_at"]:
        if column not in df.columns:
            df[column] = pd.NA
    for column in COMPLEX_COLUMNS:
        if column not in df.columns:
            df[column] = None

    out = pd.DataFrame()
    out["id"] = df["id"]
    out["title"] = df["title"]
    out["content"] = df["content"]
    out["brief"] = df["brief"]
    out["publish_time"] = df["ctime"].apply(to_publish_time)
    out["ctime"] = pd.to_numeric(df["ctime"], errors="coerce").astype("Int64")
    out["sort_score"] = pd.to_numeric(df["sort_score"], errors="coerce").astype("Int64")
    out["category"] = df["category"]
    out["level"] = df["level"]
    out["raw_type"] = df["type"]
    out["is_ad"] = df["is_ad"]
    out["assocArticleUrl"] = df["assocArticleUrl"]
    out["stock_list_json"] = df["stock_list"].apply(json_text)
    out["plate_list_json"] = df["plate_list"].apply(json_text)
    out["tags_json"] = df["tags"].apply(json_text)
    out["subjects_json"] = df["subjects"].apply(json_text)
    out["stock_name"] = df["stock_list"].apply(lambda value: first_values(value, ["name", "stock_name"]))
    out["stock_code"] = df["stock_list"].apply(stock_codes)
    out["plate_name"] = df["plate_list"].apply(lambda value: first_values(value, ["name", "plate_name"]))
    out["md5"] = df["content"].apply(md5_text)
    out["source_chunk"] = df["source_chunk"]
    out["fetched_at"] = df["fetched_at"]

    text_columns = [
        "id",
        "title",
        "content",
        "brief",
        "category",
        "level",
        "raw_type",
        "assocArticleUrl",
        "stock_list_json",
        "plate_list_json",
        "tags_json",
        "subjects_json",
        "stock_name",
        "stock_code",
        "plate_name",
        "md5",
        "source_chunk",
        "fetched_at",
    ]
    for column in text_columns:
        out[column] = out[column].astype("string")
    return out[OUTPUT_COLUMNS]


def deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    before = len(df)
    has_id = df["id"].notna() & (df["id"].astype("string").str.len() > 0)
    with_id = df[has_id].drop_duplicates(subset=["id"], keep="first")
    without_id = df[~has_id].drop_duplicates(subset=["md5"], keep="first")
    combined = pd.concat([with_id, without_id], ignore_index=True)
    combined = combined.drop_duplicates(subset=["md5"], keep="first")
    combined = combined.sort_values("publish_time", na_position="last").reset_index(drop=True)
    return combined, {
        "rows_before_dedup": before,
        "rows_after_dedup": len(combined),
        "duplicate_rows_removed": before - len(combined),
    }


def build_summary_report(
    schema_stats: SchemaStats,
    full_df: pd.DataFrame,
    dedup_stats: dict[str, int],
    chunk_count: int,
) -> pd.DataFrame:
    summary: dict[str, Any] = {
        "chunk_files": chunk_count,
        "raw_rows": schema_stats.total_rows,
        **dedup_stats,
        "min_publish_time": full_df["publish_time"].min(),
        "max_publish_time": full_df["publish_time"].max(),
        "missing_publish_time": int(full_df["publish_time"].isna().sum()),
        "output_path": str(OUTPUT_PATH),
    }
    for column in REPORT_COLUMNS:
        non_null = schema_stats.non_null_rows.get(column, 0)
        summary[f"{column}_non_null_rate"] = (
            non_null / schema_stats.total_rows if schema_stats.total_rows else 0
        )
    return pd.DataFrame([summary])


def build_parquet() -> None:
    chunk_paths = sorted(CHUNK_DIR.glob("*.jsonl"))
    if not chunk_paths:
        raise FileNotFoundError(f"未找到 raw JSONL 分块：{CHUNK_DIR}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    schema_stats = SchemaStats()
    frames: list[pd.DataFrame] = []
    for path in chunk_paths:
        records = list(iter_jsonl(path))
        for record in records:
            schema_stats.add(record)
        frames.append(raw_records_to_frame(records))

    if not frames:
        raise RuntimeError(f"未读取到 JSONL 记录：{CHUNK_DIR}")
    full_df = pd.concat(frames, ignore_index=True)
    full_df, dedup_stats = deduplicate(full_df)

    full_df.to_parquet(OUTPUT_PATH, index=False, engine="pyarrow", compression="snappy")
    schema_report = schema_stats.to_frame()
    summary_report = build_summary_report(schema_stats, full_df, dedup_stats, len(chunk_paths))
    schema_report.to_csv(SCHEMA_REPORT_PATH, index=False, encoding="utf-8-sig")
    summary_report.to_csv(SUMMARY_REPORT_PATH, index=False, encoding="utf-8-sig")

    print(f"写入 Parquet：{OUTPUT_PATH}")
    print(f"写入字段报告：{SCHEMA_REPORT_PATH}")
    print(f"写入摘要：{SUMMARY_REPORT_PATH}")
    print(summary_report.to_string(index=False))


if __name__ == "__main__":
    build_parquet()
