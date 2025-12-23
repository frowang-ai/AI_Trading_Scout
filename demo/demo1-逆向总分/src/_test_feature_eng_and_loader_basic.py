from pathlib import Path
import sys

import numpy as np
import pandas as pd

CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from feature_eng import process_excel_features, process_tushare_features  # type: ignore
from data_loader import list_dates_from_dir  # type: ignore


def test_process_excel_features_basic() -> None:
    """
    验证 Excel 特征工程的基本行为：
    - 行业列被 One-Hot 化
    - 关键键值列不会出现在特征矩阵中
    """
    df = pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000002.SZ"],
            "trade_date": ["20250101", "20250101"],
            "total_score": [10.0, 20.0],
            "行业": ["金融", "科技"],
            "f1": [1.0, 2.0],
        }
    )

    X, y, feature_cols = process_excel_features(df)

    assert len(X) == len(df)
    assert list(y.values) == [10.0, 20.0]
    # 业务键不应出现在特征中
    assert "ts_code" not in feature_cols
    assert "trade_date" not in feature_cols
    assert "total_score" not in feature_cols
    # 行业 One-Hot 列应当存在
    assert any(col.startswith("industry_") for col in feature_cols)


def test_process_tushare_features_basic() -> None:
    """
    验证 Tushare 特征工程的基本行为：
    - 仅保留数值特征
    - 关键键值列不会出现在特征矩阵中
    """
    df = pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000002.SZ"],
            "trade_date": ["20250101", "20250101"],
            "total_score": [1.0, 2.0],
            "open": [10.0, 11.0],
            "close": [10.5, 11.5],
            "flag": ["a", "b"],
        }
    )

    X, y, feature_cols = process_tushare_features(df)

    assert len(X) == len(df)
    assert np.allclose(y.values, np.array([1.0, 2.0]))
    assert "ts_code" not in feature_cols
    assert "trade_date" not in feature_cols
    assert "total_score" not in feature_cols
    assert "open" in feature_cols and "close" in feature_cols
    assert "flag" not in feature_cols


def test_list_dates_from_dir_empty(tmp_path: Path) -> None:
    """
    验证 list_dates_from_dir 在空目录下返回空列表，
    不依赖真实数据目录。
    """
    from data_loader import list_dates_from_dir  # 延迟导入以使用 tmp_path

    dates = list_dates_from_dir(tmp_path)
    assert dates == []

