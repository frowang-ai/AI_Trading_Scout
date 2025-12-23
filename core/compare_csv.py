import os
import pandas as pd
import numpy as np

from .dataset_builder import build_features_for_date


def compare(target_csv_path: str, trade_date_str: str) -> pd.DataFrame:
    try:
        src = pd.read_csv(target_csv_path, encoding="utf-8")
    except Exception:
        src = pd.read_csv(target_csv_path, encoding="gbk")
    if "日期" in src.columns:
        dt = str(src["日期"].iloc[0]).split(" ")[0]
        trade_date = dt.replace("-", "")
    else:
        trade_date = trade_date_str
    codes = src["代码"].astype(str).tolist()
    calc = build_features_for_date(trade_date, ts_codes=codes)
    cols_num = ["RSI","ADX","PLUS_DI","OBV","lower","middle","upper"]
    cols_sig = ["macd_signal","slowkdj_signal"]
    keep = [c for c in cols_num + cols_sig if c in src.columns and c in calc.columns]
    left = src[["代码"] + keep].copy()
    right = calc[["代码"] + keep].copy()
    merged = left.merge(right, on="代码", suffixes=("_src","_calc"))
    for c in cols_num:
        if f"{c}_src" in merged.columns and f"{c}_calc" in merged.columns:
            merged[f"{c}_diff"] = (pd.to_numeric(merged[f"{c}_src"], errors="coerce") - pd.to_numeric(merged[f"{c}_calc"], errors="coerce")).abs()
    for c in cols_sig:
        if f"{c}_src" in merged.columns and f"{c}_calc" in merged.columns:
            merged[f"{c}_match"] = (pd.to_numeric(merged[f"{c}_src"], errors="coerce") == pd.to_numeric(merged[f"{c}_calc"], errors="coerce")).astype(int)
    return merged


def summary(df: pd.DataFrame) -> str:
    lines = []
    num_cols = [c for c in df.columns if c.endswith("_diff")]
    sig_cols = [c for c in df.columns if c.endswith("_match")]
    for c in num_cols:
        v = df[c].dropna()
        mae = v.mean() if len(v) else np.nan
        lines.append(f"{c}: MAE={mae:.4f}")
    for c in sig_cols:
        v = df[c].dropna()
        rate = v.mean() if len(v) else np.nan
        lines.append(f"{c}: match_rate={rate:.2%}")
    return "\n".join(lines)


if __name__ == "__main__":
    path = os.getenv("TARGET_CSV_PATH", "20251126_data_sma_feature_color.csv")
    trade_date = os.getenv("TRADE_DATE", "20251126")
    try:
        out = compare(path, trade_date)
        fn = f"comparison_{trade_date}.csv"
        out.to_csv(fn, index=False, encoding="utf-8")
        print(summary(out))
    except Exception as e:
        print(f"compare_failed: {e}")

