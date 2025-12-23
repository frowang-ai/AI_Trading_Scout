import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_loader import load_dataset  # type: ignore
from src.feature_eng import process_excel_features  # type: ignore
from src.model_engine import ScorePredictor  # type: ignore


def _split_train_valid_indices(n_samples: int, train_ratio: float = 0.8) -> Tuple[np.ndarray, np.ndarray]:
    split_idx = int(n_samples * train_ratio)
    indices = np.arange(n_samples)
    return indices[:split_idx], indices[split_idx:]


def _compute_daily_rank_correlation(df: pd.DataFrame) -> pd.DataFrame:
    rows: List[dict] = []
    for date in sorted(df["trade_date"].unique()):
        df_day = df[df["trade_date"] == date]
        if len(df_day) < 2:
            continue
        sp, sp_p = spearmanr(df_day["true_score"], df_day["predicted_score"])
        kd, kd_p = kendalltau(df_day["true_score"], df_day["predicted_score"])
        rows.append(
            {
                "date": date,
                "n_stocks": len(df_day),
                "spearman": sp,
                "kendall": kd,
                "pearson": pearsonr(df_day["true_score"], df_day["predicted_score"])[0],
                "spearman_p": sp_p,
                "kendall_p": kd_p,
            }
        )
    return pd.DataFrame(rows)


def _compute_top_overlap_summary(df: pd.DataFrame, top_ns: List[int]) -> pd.DataFrame:
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
            overlaps_arr = np.array(overlaps, dtype=float)
            results.append(
                {
                    "top_n": top_n,
                    "mean_overlap": overlaps_arr.mean(),
                    "std_overlap": overlaps_arr.std(ddof=0),
                }
            )
    return pd.DataFrame(results)


def evaluate_rank_and_overlap(
    model_path: Path,
    start_date: str,
    end_date: str,
    output_dir: Path,
    tag: str = "november",
) -> None:
    """
    使用统一的 ScorePredictor + data_loader，对 Demo1 数据评估：
    - 训练集 / 验证集的日度排序一致性（Spearman/Kendall）
    - Top-N（50/100/200）重叠的均值和标准差
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1) 加载数据并做特征工程
    df_raw = load_dataset("excel_only", start_date=start_date, end_date=end_date)
    if df_raw.empty:
        raise RuntimeError("数据为空，无法评估排序一致性。")

    X, y, _ = process_excel_features(df_raw)

    # 确保 df_raw 中存在必要列
    base_cols = ["ts_code", "trade_date", "total_score"]
    for col in base_cols:
        if col not in df_raw.columns:
            raise ValueError(f"缺少必要列：{col}")

    df_base = df_raw[base_cols].copy()
    df_base = df_base.rename(columns={"total_score": "true_score"})

    # 2) 与训练脚本一致的 80/20 划分
    n_samples = len(X)
    train_idx, valid_idx = _split_train_valid_indices(n_samples, train_ratio=0.8)

    X_train = X.iloc[train_idx]
    y_train = y.iloc[train_idx]
    X_valid = X.iloc[valid_idx]
    y_valid = y.iloc[valid_idx]

    df_train_base = df_base.iloc[train_idx].reset_index(drop=True)
    df_valid_base = df_base.iloc[valid_idx].reset_index(drop=True)

    # 3) 加载模型并预测
    predictor = ScorePredictor(model_path=model_path)
    ok = predictor.load(model_path=model_path)
    if not ok:
        raise RuntimeError(f"无法加载模型：{model_path}")

    y_pred_train = predictor.predict(X_train)
    y_pred_valid = predictor.predict(X_valid)

    df_train = df_train_base.copy()
    df_train["predicted_score"] = y_pred_train

    df_valid = df_valid_base.copy()
    df_valid["predicted_score"] = y_pred_valid

    # 4) 计算日度排序一致性
    df_corr_train = _compute_daily_rank_correlation(df_train)
    df_corr_valid = _compute_daily_rank_correlation(df_valid)

    corr_train_path = output_dir / f"daily_rank_correlation_{tag}_train.csv"
    corr_valid_path = output_dir / f"daily_rank_correlation_{tag}_test.csv"

    df_corr_train.to_csv(corr_train_path, index=False, encoding="utf-8")
    df_corr_valid.to_csv(corr_valid_path, index=False, encoding="utf-8")
    print(f"Daily rank correlation (train) saved to: {corr_train_path}")
    print(f"Daily rank correlation (test)  saved to: {corr_valid_path}")

    # 5) 计算 Top-N 重叠统计
    top_ns = [50, 100, 200]
    df_overlap_train = _compute_top_overlap_summary(df_train, top_ns=top_ns)
    df_overlap_valid = _compute_top_overlap_summary(df_valid, top_ns=top_ns)

    overlap_train_path = output_dir / f"top_overlap_{tag}_train.csv"
    overlap_valid_path = output_dir / f"top_overlap_{tag}_test.csv"

    df_overlap_train.to_csv(overlap_train_path, index=False, encoding="utf-8")
    df_overlap_valid.to_csv(overlap_valid_path, index=False, encoding="utf-8")
    print(f"Top-N overlap (train) saved to: {overlap_train_path}")
    print(f"Top-N overlap (test)  saved to: {overlap_valid_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate rank consistency and Top-N overlap for Demo1."
    )
    parser.add_argument("--start-date", type=str, default="20251101")
    parser.add_argument("--end-date", type=str, default="20251130")
    parser.add_argument(
        "--model",
        type=str,
        default="excel_model.pkl",
        help="模型文件名（位于 output/ 下）",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "output_full"),
        help="评估结果输出目录",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default="november",
        help="输出文件名中的月份标记，例如 november / december_holdout",
    )
    args = parser.parse_args()

    model_path = PROJECT_ROOT / "output" / args.model
    output_dir = Path(args.output_dir).resolve()

    evaluate_rank_and_overlap(
        model_path=model_path,
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=output_dir,
        tag=args.tag,
    )


if __name__ == "__main__":
    main()
