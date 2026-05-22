from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parents[3].resolve()
OUTPUT_DIR = CURRENT_DIR / "outputs"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from get_data_tushare.client import TushareClient

START_DATE = "20250808"
END_DATE = "20251010"
ETF_KEYWORDS = ["半导体", "芯片", "集成电路", "科创芯片", "中证芯片", "国证芯片"]


def contains_any(series: pd.Series, keywords: list[str]) -> pd.Series:
    text = series.fillna("").astype(str)
    mask = pd.Series(False, index=series.index)
    for keyword in keywords:
        mask = mask | text.str.contains(keyword, regex=False, na=False)
    return mask


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = TushareClient()

    etf_basic = client.query(
        "etf_basic",
        list_status="L",
        fields="ts_code,csname,extname,cname,index_code,index_name,list_date,exchange,mgr_name,etf_type",
    )
    text = etf_basic.fillna("").astype(str).agg(" ".join, axis=1)
    candidates = etf_basic[contains_any(text, ETF_KEYWORDS)].copy()
    candidates = candidates.sort_values(["list_date", "ts_code"]).reset_index(drop=True)

    frames: list[pd.DataFrame] = []
    for ts_code in candidates["ts_code"].dropna().astype(str).tolist():
        daily = client.query(
            "fund_daily",
            ts_code=ts_code,
            start_date=START_DATE,
            end_date=END_DATE,
        )
        if daily.empty:
            continue
        daily["ts_code"] = ts_code
        frames.append(daily)

    etf_daily = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not etf_daily.empty:
        etf_daily = etf_daily.merge(
            candidates[["ts_code", "csname", "extname", "index_name"]],
            on="ts_code",
            how="left",
        )
        etf_daily = etf_daily.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)

    candidates.to_csv(OUTPUT_DIR / "_test_semiconductor_etf_candidates.csv", index=False, encoding="utf-8-sig")
    etf_daily.to_csv(OUTPUT_DIR / "_test_semiconductor_etf_daily.csv", index=False, encoding="utf-8-sig")

    if etf_daily.empty:
        summary = pd.DataFrame(
            [
                {
                    "candidate_etfs": len(candidates),
                    "daily_rows": 0,
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                }
            ]
        )
    else:
        returns = (
            etf_daily.sort_values(["ts_code", "trade_date"])
            .groupby("ts_code")
            .agg(
                csname=("csname", "first"),
                extname=("extname", "first"),
                index_name=("index_name", "first"),
                rows=("trade_date", "size"),
                first_close=("close", "first"),
                last_close=("close", "last"),
                first_date=("trade_date", "first"),
                last_date=("trade_date", "last"),
            )
            .reset_index()
        )
        returns["period_return"] = returns["last_close"] / returns["first_close"] - 1
        summary = returns.sort_values("period_return", ascending=False)

    summary.to_csv(OUTPUT_DIR / "_test_semiconductor_etf_summary.csv", index=False, encoding="utf-8-sig")
    print("ETF candidates:")
    print(candidates.to_string(index=False))
    print("\nETF summary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
