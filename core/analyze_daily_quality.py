from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from get_data_tushare.config import DATA_ROOT

def list_daily_files(years: list[str] | None = None) -> list[Path]:
    base = DATA_ROOT / "raw" / "daily"
    if years is None:
        years = [p.name for p in base.iterdir() if p.is_dir()]
    files: list[Path] = []
    for y in years:
        d = base / y
        if not d.exists():
            continue
        files.extend(sorted(d.glob("daily_*.parquet")))
    return files

def aggregate_missing_and_numeric(files: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    total_rows = 0
    col_non_null: dict[str, int] = {}
    numeric_stats: dict[str, dict[str, float]] = {}
    numeric_cols_seen: set[str] = set()
    for fp in files:
        df = pd.read_parquet(fp)
        total_rows += len(df)
        for c in df.columns:
            nn = df[c].notna().sum()
            col_non_null[c] = col_non_null.get(c, 0) + int(nn)
        num_df = df.select_dtypes(include=["number"])
        for c in num_df.columns:
            s = num_df[c].dropna()
            if c not in numeric_stats:
                numeric_stats[c] = {"count": 0.0, "sum": 0.0, "sumsq": 0.0, "min": float("inf"), "max": float("-inf")}
            st = numeric_stats[c]
            cnt = float(len(s))
            st["count"] += cnt
            st["sum"] += float(s.sum()) if cnt > 0 else 0.0
            st["sumsq"] += float((s.astype("float64") ** 2).sum()) if cnt > 0 else 0.0
            if cnt > 0:
                st["min"] = float(min(st["min"], s.min()))
                st["max"] = float(max(st["max"], s.max()))
            numeric_cols_seen.add(c)
    missing_rows = []
    for c, nn in col_non_null.items():
        missing_rows.append({"column": c, "non_null": nn, "total": total_rows, "missing_ratio": 1 - (nn / total_rows if total_rows > 0 else 0)})
    missing_df = pd.DataFrame(missing_rows).sort_values("missing_ratio", ascending=False).reset_index(drop=True)
    numeric_rows = []
    for c in sorted(numeric_cols_seen):
        st = numeric_stats[c]
        count = st["count"]
        mean = st["sum"] / count if count > 0 else None
        var = (st["sumsq"] / count - (mean ** 2)) if count and mean is not None else None
        std = (var ** 0.5) if var is not None and var >= 0 else None
        numeric_rows.append({"column": c, "count": int(count), "mean": mean, "std": std, "min": None if st["min"] == float("inf") else st["min"], "max": None if st["max"] == float("-inf") else st["max"]})
    numeric_df = pd.DataFrame(numeric_rows).sort_values("column").reset_index(drop=True)
    return missing_df, numeric_df

def count_records_by_day(files: list[Path]) -> pd.DataFrame:
    rows = []
    for fp in files:
        df = pd.read_parquet(fp, columns=["trade_date"])
        day = fp.stem.split("_")[-1]
        rows.append({"trade_date": day, "records": int(len(df))})
    return pd.DataFrame(rows).sort_values("trade_date").reset_index(drop=True)

def analyze_daily(years: list[str] | None = None, out_dir: Path | None = None) -> dict[str, str]:
    files = list_daily_files(years)
    if not files:
        raise FileNotFoundError("No daily parquet files found under data/raw/daily")
    missing_df, numeric_df = aggregate_missing_and_numeric(files)
    by_day_df = count_records_by_day(files)
    if out_dir is None:
        out_dir = DATA_ROOT / "reports" / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    missing_path = out_dir / "missingness_daily.csv"
    numeric_path = out_dir / "numeric_stats_daily.csv"
    byday_path = out_dir / "records_by_day.csv"
    overview_path = out_dir / "overview.json"
    missing_df.to_csv(missing_path, index=False)
    numeric_df.to_csv(numeric_path, index=False)
    by_day_df.to_csv(byday_path, index=False)
    overview = {
        "total_days": len(files),
        "first_day": files[0].stem.split("_")[-1],
        "last_day": files[-1].stem.split("_")[-1],
        "total_records": int(sum(pd.read_parquet(fp, columns=["trade_date"]).shape[0] for fp in files)),
    }
    overview_path.write_text(json.dumps(overview, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"missing_csv": str(missing_path), "numeric_csv": str(numeric_path), "byday_csv": str(byday_path), "overview_json": str(overview_path)}

if __name__ == "__main__":
    analyze_daily()
