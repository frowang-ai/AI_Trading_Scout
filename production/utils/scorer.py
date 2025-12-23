"""
封装 Stage 2: 策略计算与评分

职责：
- 基于当日 Tushare 特征和已训练好的 XGBoost 模型计算预测总分
- 生成全市场评分表与 Top N 列表
- 将预测结果与 Excel 真值总分合并，便于离线评估
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from production.config import HISTORY_DIR, MODEL_PATH, OUTPUT_DIR, TOP_N


def _load_model(model_path: Optional[Path] = None):
    """加载已训练好的回归模型（当前为 demo1 中的 XGBoost 模型）。"""
    path = Path(model_path or MODEL_PATH)
    if not path.exists():
        raise FileNotFoundError(f"模型文件不存在：{path}")

    with path.open("rb") as f:
        # 裸模型即可，不强制要求 ScorePredictor 封装
        import pickle

        model = pickle.load(f)

    if not hasattr(model, "predict"):
        raise TypeError(f"加载的模型不支持 predict 接口：{type(model)}")
    return model


def _prepare_features(df: pd.DataFrame, model) -> pd.DataFrame:
    """
    准备模型输入特征：
    - 优先按模型训练时的特征名顺序对齐（避免 XGBoost feature_names mismatch）
    - 否则退化为：保留数值列，排除 ts_code / trade_date，处理缺失值与 inf
    """
    if "ts_code" not in df.columns or "trade_date" not in df.columns:
        raise ValueError("特征表中缺少 ts_code 或 trade_date 列，无法打分。")

    # 优先使用 XGBoost 模型自带的特征名，以避免 feature_names mismatch
    booster_feature_names = None
    try:
        if hasattr(model, "get_booster"):
            booster = model.get_booster()
            booster_feature_names = list(booster.feature_names or [])
    except Exception:
        booster_feature_names = None

    if booster_feature_names:
        # 确保所有期望特征名都在 DataFrame 中；缺失的列用 0.0 填充
        df_aligned = df.copy()
        for col in booster_feature_names:
            if col not in df_aligned.columns:
                df_aligned[col] = 0.0

        X = df_aligned[booster_feature_names].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0.0)
        return X

    # 回退策略：仅使用数值列，排除 ts_code / trade_date
    exclude_cols = {"ts_code", "trade_date"}
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    numeric_cols = []
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)

    if not numeric_cols:
        raise ValueError("特征表中未找到任何数值型特征列，无法打分。")

    X = df[numeric_cols].copy()
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    expected_features = getattr(model, "n_features_in_", None)
    if expected_features is not None and len(X.columns) != int(expected_features):
        print(
            "[警告] 特征数量与模型期望不一致："
            f"模型期望 {expected_features} 个，当前 {len(X.columns)} 个。"
        )

    return X


def calculate_scores(
    df_features: pd.DataFrame,
    model=None,
) -> pd.DataFrame:
    """
    基于当日 Tushare 特征计算预测总分并生成 rank。

    Args:
        df_features: 至少包含 ts_code / trade_date 以及若干数值型特征的 DataFrame。
        model: 可选，已加载模型实例；若为 None，则从 MODEL_PATH 自动加载。

    Returns:
        DataFrame，包含 ts_code / trade_date / predicted_score / rank 四列及其他原始列。
    """
    if df_features.empty:
        raise ValueError("输入特征表为空，无法计算分数。")

    model = model or _load_model()

    X = _prepare_features(df_features, model)

    scores = model.predict(X)

    df_scores = df_features.copy()
    df_scores["predicted_score"] = scores

    df_scores = df_scores.sort_values(
        ["predicted_score", "ts_code"], ascending=[False, True]
    ).reset_index(drop=True)
    df_scores["rank"] = np.arange(1, len(df_scores) + 1, dtype=int)

    return df_scores


def get_top_n(df: pd.DataFrame, n: int = TOP_N) -> pd.DataFrame:
    """
    从全量评分表中提取 Top N 股票。

    当 df 未按分数排序时，会先按 predicted_score 降序、ts_code 升序进行一次排序。
    """
    if df.empty:
        return df

    if "predicted_score" not in df.columns or "rank" not in df.columns:
        df = df.sort_values(
            ["predicted_score", "ts_code"], ascending=[False, True]
        ).reset_index(drop=True)
        df["rank"] = np.arange(1, len(df) + 1, dtype=int)

    return df.nsmallest(n, columns="rank")


def save_full_scores(date_str: str, df_scores: pd.DataFrame) -> Path:
    """
    将当日全市场评分表保存为 CSV。

    文件命名：scores_full_YYYYMMDD.csv
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / f"scores_full_{date_str}.csv"
    df_scores.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[Step1] 全市场评分表已保存：{csv_path}")
    return csv_path


def save_top_list_json(date_str: str, df_top: pd.DataFrame) -> Path:
    """
    将当日 Top N 列表以轻量 JSON 形式保存到 history 目录。

    文件命名：top_YYYYMMDD.json
    """
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    json_path = HISTORY_DIR / f"top_{date_str}.json"

    records = []
    for _, row in df_top.iterrows():
        records.append(
            {
                "ts_code": row["ts_code"],
                "trade_date": row["trade_date"],
                "predicted_score": float(row["predicted_score"]),
                "rank": int(row["rank"]),
            }
        )

    payload: Dict[str, object] = {
        "date": date_str,
        "top_n": len(df_top),
        "items": records,
    }

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[Step1] 当日 Top 列表已保存：{json_path}")

    return json_path


def save_merged_with_excel(
    date_str: str,
    df_scores: pd.DataFrame,
    df_excel: pd.DataFrame,
) -> Optional[Path]:
    """
    将模型预测总分与 Excel 真值总分合并并导出，便于离线评估。

    若 Excel 数据为空，则返回 None。
    """
    if df_excel.empty:
        return None

    left_cols = ["ts_code", "trade_date", "predicted_score", "rank"]
    left = df_scores[left_cols].copy()

    right = df_excel.copy()
    if "total_score" not in right.columns:
        print("[提示] Excel 表中缺失 total_score 列，跳过合并导出。")
        return None

    merged = pd.merge(
        right,
        left,
        on=["ts_code", "trade_date"],
        how="left",
        suffixes=("_excel", "_model"),
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"merged_scores_with_excel_{date_str}.csv"
    merged.to_csv(out_path, index=False, encoding="utf-8")
    print(f"[Step1] 预测分数与 Excel 真值合并文件已保存：{out_path}")

    return out_path
