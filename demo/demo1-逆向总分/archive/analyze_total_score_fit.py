from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
from scipy.stats import spearmanr, kendalltau
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle


CURRENT_DIR = Path(__file__).parent.resolve()
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

import train_full_november as train_mod


OUTPUT_DIR = train_mod.OUTPUT_DIR
EXTERNAL_DIR_NOV = train_mod.EXTERNAL_DIR_NOV


def load_prediction_file(file_name: str):
    path = OUTPUT_DIR / file_name
    if not path.exists():
        print(f"\nPrediction file not found: {path}")
        return None
    df = pd.read_csv(path)
    print(f"\nLoaded {len(df)} rows from {path.name}")
    return df


def prepare_eval_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df_eval = df.copy()
    if "total_score" in df_eval.columns and "true_score" not in df_eval.columns:
        df_eval = df_eval.rename(columns={"total_score": "true_score"})
    if "predicted_score" not in df_eval.columns:
        raise ValueError("Column predicted_score is required in prediction file")
    return df_eval


def evaluate_regression_from_predictions(df: pd.DataFrame, name: str):
    df_eval = prepare_eval_dataframe(df)
    y_true = df_eval["true_score"].values
    y_pred = df_eval["predicted_score"].values
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    errors = y_true - y_pred
    print(f"\n{name} Regression Metrics")
    print(f"R2:   {r2:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print("Error Distribution")
    print(f"Mean: {errors.mean():.4f}")
    print(f"Std:  {errors.std():.4f}")
    print(f"Min:  {errors.min():.4f}")
    print(f"Max:  {errors.max():.4f}")
    return {
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "mean_error": float(errors.mean()),
        "std_error": float(errors.std()),
    }


def calculate_rank_correlation(df: pd.DataFrame, name: str):
    df_eval = prepare_eval_dataframe(df)
    spearman_all, p_spearman_all = spearmanr(df_eval["true_score"], df_eval["predicted_score"])
    kendall_all, p_kendall_all = kendalltau(df_eval["true_score"], df_eval["predicted_score"])
    print(f"\n{name} Rank Correlation (All Samples)")
    print(f"Spearman: {spearman_all:.6f} (p={p_spearman_all:.2e})")
    print(f"Kendall:  {kendall_all:.6f} (p={p_kendall_all:.2e})")
    daily_results = []
    if "trade_date" in df_eval.columns:
        for date in sorted(df_eval["trade_date"].unique()):
            df_day = df_eval[df_eval["trade_date"] == date]
            if len(df_day) <= 1:
                continue
            sp_corr, sp_p = spearmanr(df_day["true_score"], df_day["predicted_score"])
            kd_corr, kd_p = kendalltau(df_day["true_score"], df_day["predicted_score"])
            daily_results.append(
                {
                    "date": date,
                    "n_stocks": len(df_day),
                    "spearman": sp_corr,
                    "kendall": kd_corr,
                    "spearman_p": sp_p,
                    "kendall_p": kd_p,
                }
            )
    if not daily_results:
        return None
    df_daily = pd.DataFrame(daily_results)
    print("\nDaily Rank Correlation Summary")
    print(df_daily[["date", "n_stocks", "spearman", "kendall"]].to_string(index=False))
    path = OUTPUT_DIR / f"daily_rank_correlation_{name.replace(' ', '_').lower()}.csv"
    df_daily.to_csv(path, index=False, encoding="utf-8")
    print(f"\nDaily rank correlation saved to: {path}")
    return df_daily


def analyze_top_overlap(df: pd.DataFrame, name: str, top_n_list=None):
    if top_n_list is None:
        top_n_list = [50, 100, 200]
    df_eval = prepare_eval_dataframe(df)
    results = []
    for top_n in top_n_list:
        if "trade_date" in df_eval.columns:
            overlaps = []
            for date in sorted(df_eval["trade_date"].unique()):
                df_day = df_eval[df_eval["trade_date"] == date]
                if len(df_day) < top_n:
                    continue
                true_top = set(df_day.nlargest(top_n, "true_score")["ts_code"])
                pred_top = set(df_day.nlargest(top_n, "predicted_score")["ts_code"])
                overlap = len(true_top & pred_top)
                overlaps.append(overlap / top_n)
            if overlaps:
                mean_overlap = float(np.mean(overlaps))
                std_overlap = float(np.std(overlaps))
            else:
                mean_overlap = float("nan")
                std_overlap = float("nan")
        else:
            df_sorted_true = df_eval.nlargest(top_n, "true_score")
            df_sorted_pred = df_eval.nlargest(top_n, "predicted_score")
            true_top = set(df_sorted_true["ts_code"])
            pred_top = set(df_sorted_pred["ts_code"])
            overlap = len(true_top & pred_top)
            mean_overlap = overlap / top_n
            std_overlap = 0.0
        print(f"\n{name} Top-{top_n} Overlap")
        print(f"Mean overlap: {mean_overlap * 100:.2f}%")
        results.append(
            {
                "top_n": top_n,
                "mean_overlap": mean_overlap,
                "std_overlap": std_overlap,
            }
        )
    df_results = pd.DataFrame(results)
    path = OUTPUT_DIR / f"top_overlap_{name.replace(' ', '_').lower()}.csv"
    df_results.to_csv(path, index=False, encoding="utf-8")
    print(f"\nTop-N overlap statistics saved to: {path}")
    return df_results


def plot_true_vs_pred(df: pd.DataFrame, name: str):
    df_eval = prepare_eval_dataframe(df)
    sample = df_eval
    if len(sample) > 5000:
        sample = sample.sample(n=5000, random_state=42)
    plt.figure(figsize=(6, 6))
    plt.scatter(sample["true_score"], sample["predicted_score"], s=5, alpha=0.4)
    min_val = min(sample["true_score"].min(), sample["predicted_score"].min())
    max_val = max(sample["true_score"].max(), sample["predicted_score"].max())
    plt.plot([min_val, max_val], [min_val, max_val], color="red", linewidth=1)
    plt.xlabel("True total_score")
    plt.ylabel("Predicted total_score")
    plt.title(f"{name} True vs Predicted")
    plt.tight_layout()
    path = OUTPUT_DIR / f"scatter_true_vs_pred_{name.replace(' ', '_').lower()}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nScatter plot saved to: {path}")


def load_or_compute_feature_importance(model, X, feature_cols):
    path = OUTPUT_DIR / "feature_importance.csv"
    if path.exists():
        df_imp = pd.read_csv(path)
        if {"feature", "importance"}.issubset(set(df_imp.columns)):
            print(f"\nLoaded feature importance from: {path}")
            return df_imp
    print("\nComputing SHAP feature importance on November data")
    importance_df = train_mod.shap_analysis(model, X, feature_cols)
    path = OUTPUT_DIR / "feature_importance.csv"
    importance_df.to_csv(path, index=False, encoding="utf-8")
    print(f"Feature importance saved to: {path}")
    return importance_df


def group_feature_importance(importance_df: pd.DataFrame):
    df_imp = importance_df.copy()
    df_imp["feature"] = df_imp["feature"].astype(str)
    def group_func(name: str):
        if "_" in name:
            return name.split("_", 1)[0]
        return "other"
    df_imp["group"] = df_imp["feature"].map(group_func)
    df_group = (
        df_imp.groupby("group", as_index=False)["importance"]
        .sum()
        .sort_values("importance", ascending=False)
    )
    path = OUTPUT_DIR / "feature_importance_grouped.csv"
    df_group.to_csv(path, index=False, encoding="utf-8")
    print("\nGrouped feature importance (top 20 groups)")
    print(df_group.head(20).to_string(index=False))
    print(f"\nGrouped feature importance saved to: {path}")
    return df_group


def select_representative_sample_from_test():
    path = OUTPUT_DIR / "prediction_nov_test.csv"
    if not path.exists():
        return None, None
    df = pd.read_csv(path)
    if "error" not in df.columns:
        return None, None
    idx = df["error"].abs().idxmax()
    row = df.iloc[idx]
    ts_code = str(row["ts_code"])
    trade_date = str(row["trade_date"])
    print(f"\nSelected sample for local explanation from test set: {ts_code} {trade_date}")
    return ts_code, trade_date


def local_explanation(model, df_full: pd.DataFrame, X_full: pd.DataFrame, feature_cols, ts_code=None, trade_date=None, top_k: int = 20):
    if ts_code is None or trade_date is None:
        ts_code, trade_date = select_representative_sample_from_test()
    if ts_code is None or trade_date is None:
        print("\nNo sample available for local explanation")
        return
    mask = (df_full["ts_code"].astype(str) == str(ts_code)) & (
        df_full["trade_date"].astype(str) == str(trade_date)
    )
    if not mask.any():
        print(f"\nSample not found in November data: {ts_code} {trade_date}")
        return
    idx = df_full.index[mask][0]
    x_row = X_full.loc[[idx]]
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x_row)
    if isinstance(shap_values, list):
        shap_row = np.array(shap_values[0][0])
        base_value = float(np.array(explainer.expected_value[0]))
    else:
        shap_row = np.array(shap_values[0])
        base_value = float(np.array(explainer.expected_value))
    contrib_df = pd.DataFrame(
        {
            "feature": list(feature_cols),
            "feature_value": x_row.iloc[0].values,
            "shap_value": shap_row,
        }
    )
    contrib_df["abs_shap"] = contrib_df["shap_value"].abs()
    contrib_df = contrib_df.sort_values("abs_shap", ascending=False)
    true_score = float(df_full.loc[idx, "total_score"])
    pred_score = float(model.predict(x_row)[0])
    print(f"\nLocal explanation for {ts_code} {trade_date}")
    print(f"True total_score: {true_score:.4f}")
    print(f"Predicted score:  {pred_score:.4f}")
    print(f"SHAP base value:  {base_value:.4f}")
    print(f"SHAP sum:         {shap_row.sum():.4f}")
    print("\nTop features by |SHAP|")
    print(contrib_df.head(top_k)[["feature", "feature_value", "shap_value", "abs_shap"]].to_string(index=False))
    top_df = contrib_df.head(top_k).sort_values("shap_value")
    plt.figure(figsize=(10, 8))
    plt.barh(top_df["feature"], top_df["shap_value"])
    plt.axvline(0, color="black", linewidth=0.8)
    plt.xlabel("SHAP value contribution")
    plt.title(f"Local SHAP for {ts_code} {trade_date}")
    plt.tight_layout()
    safe_ts = ts_code.replace(".", "_")
    file_name = f"local_shap_{safe_ts}_{trade_date}.png"
    path = OUTPUT_DIR / file_name
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nLocal SHAP plot saved to: {path}")


def main():
    print("\n############################################################")
    print("Two-step analysis for reverse-engineered total score model")
    print("Step 2: Fit quality, ranking metrics, and interpretability")
    print("############################################################")
    model_path = OUTPUT_DIR / "xgboost_model_nov.pkl"
    if not model_path.exists():
        print(f"\nModel file not found: {model_path}")
        print("Please run train_full_november.py first")
        return
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print(f"\nLoaded model from: {model_path}")
    df_train_pred = load_prediction_file("prediction_nov_train.csv")
    if df_train_pred is not None:
        evaluate_regression_from_predictions(df_train_pred, "November Train")
        calculate_rank_correlation(df_train_pred, "November Train")
        analyze_top_overlap(df_train_pred, "November Train")
        plot_true_vs_pred(df_train_pred, "November Train")
    df_test_pred = load_prediction_file("prediction_nov_test.csv")
    if df_test_pred is not None:
        evaluate_regression_from_predictions(df_test_pred, "November Test")
        calculate_rank_correlation(df_test_pred, "November Test")
        analyze_top_overlap(df_test_pred, "November Test")
        plot_true_vs_pred(df_test_pred, "November Test")
    df_dec_pred = load_prediction_file("december_predictions.csv")
    if df_dec_pred is not None:
        evaluate_regression_from_predictions(df_dec_pred, "December Holdout")
        calculate_rank_correlation(df_dec_pred, "December Holdout")
        analyze_top_overlap(df_dec_pred, "December Holdout")
        plot_true_vs_pred(df_dec_pred, "December Holdout")
    print("\nLoading November data for SHAP analysis")
    df_nov = train_mod.load_all_data(EXTERNAL_DIR_NOV, "November")
    X_nov, y_nov, feature_cols = train_mod.prepare_features(df_nov)
    importance_df = load_or_compute_feature_importance(model, X_nov, feature_cols)
    group_feature_importance(importance_df)
    local_explanation(model, df_nov, X_nov, feature_cols)
    print("\nAll analysis outputs saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()

