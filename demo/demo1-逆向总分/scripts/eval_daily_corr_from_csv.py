import argparse
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr


def compute_daily_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows: List[dict] = []
    for date in sorted(df["trade_date"].unique()):
        df_day = df[df["trade_date"] == date]
        if len(df_day) < 2:
            continue
        true = df_day["true_score"]
        pred = df_day["predicted_score"]
        sp, sp_p = spearmanr(true, pred)
        kd, kd_p = kendalltau(true, pred)
        pe, pe_p = pearsonr(true, pred)
        rows.append(
            {
                "date": date,
                "n_stocks": len(df_day),
                "spearman": sp,
                "kendall": kd,
                "pearson": pe,
                "spearman_p": sp_p,
                "kendall_p": kd_p,
                "pearson_p": pe_p,
            }
        )
    return pd.DataFrame(rows)


def compute_top_overlap(df: pd.DataFrame, top_ns: List[int]) -> pd.DataFrame:
    results: List[dict] = []
    for top_n in top_ns:
        overlaps: List[float] = []
        for date in sorted(df["trade_date"].unique()):
            df_day = df[df["trade_date"] == date]
            if len(df_day) < top_n:
                continue
            true_top = set(df_day.nlargest(top_n, "true_score")["ts_code"])
            pred_top = set(df_day.nlargest(top_n, "predicted_score")["ts_code"])
            overlap = len(true_top & pred_top) / float(top_n)
            overlaps.append(overlap)
        if overlaps:
            arr = np.array(overlaps, dtype=float)
            results.append(
                {
                    "top_n": top_n,
                    "mean_overlap": arr.mean(),
                    "std_overlap": arr.std(ddof=0),
                }
            )
    return pd.DataFrame(results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate daily rank correlations and Top-N overlap from a prediction CSV."
    )
    parser.add_argument("--csv", type=str, required=True, help="路径，包含 ts_code/trade_date/total_score/predicted_score 列")
    parser.add_argument("--output-prefix", type=str, required=True, help="输出前缀，用于生成两个 CSV 文件")
    args = parser.parse_args()

    csv_path = Path(args.csv).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 文件不存在：{csv_path}")

    df = pd.read_csv(csv_path)
    required_cols = {"ts_code", "trade_date", "total_score", "predicted_score"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV 必须包含列：{required_cols}")

    df_eval = df[["ts_code", "trade_date", "total_score", "predicted_score"]].copy()
    df_eval = df_eval.rename(columns={"total_score": "true_score"})

    daily_stats = compute_daily_stats(df_eval)
    top_overlap = compute_top_overlap(df_eval, top_ns=[50, 100, 200])

    prefix = Path(args.output_prefix)
    daily_path = prefix.with_name(prefix.name + "_daily_corr.csv")
    overlap_path = prefix.with_name(prefix.name + "_top_overlap.csv")

    daily_stats.to_csv(daily_path, index=False, encoding="utf-8")
    top_overlap.to_csv(overlap_path, index=False, encoding="utf-8")

    print(f"Daily correlations saved to: {daily_path}")
    print(f"Top-N overlap saved to: {overlap_path}")


if __name__ == "__main__":
    main()

