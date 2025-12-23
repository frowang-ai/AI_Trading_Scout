from pathlib import Path

import numpy as np
import pandas as pd

from production.utils import scorer


def _make_dummy_features() -> pd.DataFrame:
    """构造一份极小的 Tushare 特征表，用于验证打分与排序接口."""
    data = {
        "ts_code": ["000001.SZ", "000002.SZ", "600000.SH"],
        "trade_date": ["20251218", "20251218", "20251218"],
        "open": [10.0, 20.0, 30.0],
        "close": [11.0, 19.0, 29.0],
        "vol": [1000.0, 2000.0, 1500.0],
    }
    return pd.DataFrame(data)


class _DummyModel:
    """用于单元测试的极简回归模型，避免依赖真实 XGBoost 模型文件."""

    def __init__(self) -> None:
        self.n_features_in_ = 3

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        # 简单地对每行做特征求和，便于断言排序结果
        if isinstance(X, pd.DataFrame):
            arr = X.to_numpy(dtype=float)
        else:
            arr = np.asarray(X, dtype=float)
        return arr.sum(axis=1)


def test_calculate_scores_basic_rank_order() -> None:
    """验证 calculate_scores 返回的分数与排序逻辑基本正确."""
    df_features = _make_dummy_features()
    model = _DummyModel()

    df_scores = scorer.calculate_scores(df_features, model=model)

    assert set(["ts_code", "trade_date", "predicted_score", "rank"]).issubset(
        df_scores.columns
    )
    # 按分数降序排列后，rank 应当从 1 开始递增
    top = df_scores.sort_values("predicted_score", ascending=False).reset_index(
        drop=True
    )
    assert list(top["rank"]) == [1, 2, 3]


def test_get_top_n_uses_rank_order() -> None:
    """验证 get_top_n 根据 rank/分数获取前 N 只股票."""
    df_features = _make_dummy_features()
    model = _DummyModel()
    df_scores = scorer.calculate_scores(df_features, model=model)

    top2 = scorer.get_top_n(df_scores, n=2)
    assert len(top2) == 2
    # Top2 的 rank 应该是 1 和 2
    assert set(top2["rank"].tolist()) == {1, 2}

