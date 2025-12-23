from pathlib import Path
import sys

import numpy as np
import pandas as pd

CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.append(str(PROJECT_ROOT / "src"))

from eval_rank_and_overlap import _compute_daily_rank_correlation, _compute_top_overlap_summary  # type: ignore


def test_rank_and_overlap_helpers() -> None:
    """
    使用一份小型模拟数据，验证排序一致性和 TopN 重叠的辅助函数行为正常。
    """
    dates = ["20250101"] * 5 + ["20250102"] * 5
    ts_codes = [f"00000{i}.SZ" for i in range(10)]
    true_score = np.arange(10, dtype=float)
    pred_score = np.arange(10, dtype=float)[::-1]

    df = pd.DataFrame(
        {
            "ts_code": ts_codes,
            "trade_date": dates,
            "true_score": true_score,
            "predicted_score": pred_score,
        }
    )

    df_corr = _compute_daily_rank_correlation(df)
    assert not df_corr.empty
    assert {"date", "n_stocks", "spearman", "kendall"}.issubset(df_corr.columns)

    df_overlap = _compute_top_overlap_summary(df, top_ns=[3])
    assert not df_overlap.empty
    assert set(df_overlap.columns) == {"top_n", "mean_overlap", "std_overlap"}

