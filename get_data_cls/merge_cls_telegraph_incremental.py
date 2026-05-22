from __future__ import annotations

from pathlib import Path

import pandas as pd


CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.resolve()
HISTORY_PATH = PROJECT_ROOT / "data" / "processed" / "cls_telegraph" / "cls_telegraph_2014_2025.parquet"
INCREMENTAL_DIR = PROJECT_ROOT / "data" / "raw" / "cls_telegraph" / "incremental_20250210_20260521"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "cls_telegraph" / "cls_telegraph_2014_20260521.parquet"
REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "cls_telegraph" / "_test_cls_telegraph_merged_summary.csv"

RENAME_COLUMNS = {
    "标题": "title",
    "内容": "content",
    "发布时间": "publish_time",
    "引用来源": "source",
    "股票名称": "stock_name",
    "股票代码": "stock_code",
}


def read_incremental_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df.rename(columns=RENAME_COLUMNS)
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    df["source_file"] = path.name
    df["publish_date"] = df["publish_time"].dt.strftime("%Y%m%d")
    return df[["title", "content", "publish_time", "source", "stock_name", "stock_code", "md5", "source_file", "publish_date"]]


def merge_all() -> None:
    if not HISTORY_PATH.exists():
        raise FileNotFoundError(f"历史 Parquet 不存在：{HISTORY_PATH}")

    csv_paths = sorted(INCREMENTAL_DIR.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"增量 CSV 不存在：{INCREMENTAL_DIR}")

    history = pd.read_parquet(HISTORY_PATH)
    incremental = pd.concat([read_incremental_csv(path) for path in csv_paths], ignore_index=True)
    combined = pd.concat([history, incremental], ignore_index=True)

    before_dedup = len(combined)
    combined = combined.drop_duplicates(subset=["md5"], keep="first")
    after_dedup = len(combined)
    combined = combined.sort_values("publish_time").reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(OUTPUT_PATH, index=False, engine="pyarrow", compression="snappy")

    summary = pd.DataFrame(
        [
            {
                "history_rows": len(history),
                "incremental_files": len(csv_paths),
                "incremental_rows": len(incremental),
                "rows_before_dedup": before_dedup,
                "rows_after_dedup": after_dedup,
                "duplicate_md5_rows": before_dedup - after_dedup,
                "min_publish_time": combined["publish_time"].min(),
                "max_publish_time": combined["publish_time"].max(),
                "output_path": str(OUTPUT_PATH),
            }
        ]
    )
    summary.to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
    print(f"写入合并 Parquet：{OUTPUT_PATH}")
    print(f"写入摘要：{REPORT_PATH}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    merge_all()
