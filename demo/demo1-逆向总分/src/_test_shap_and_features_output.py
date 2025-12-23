from pathlib import Path

import numpy as np
import pandas as pd

from model_engine import ScorePredictor


def _make_dummy_data(n_samples: int = 40, n_features: int = 6) -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.RandomState(0)
    X = pd.DataFrame(
        rng.randn(n_samples, n_features),
        columns=[f"f{i}" for i in range(n_features)],
    )
    y = pd.Series(rng.randn(n_samples), name="target")
    return X, y


def test_export_shap_report_creates_files(tmp_path: Path) -> None:
    """
    验证 ScorePredictor.export_shap_report 能够：
    - 训练一个简单模型
    - 在给定输出目录下生成 SHAP PNG、CSV 和特征列表 TXT
    """
    X, y = _make_dummy_data()
    X_train = X.iloc[:30]
    y_train = y.iloc[:30]
    X_valid = X.iloc[30:]

    predictor = ScorePredictor()
    predictor.fit(X_train, y_train, X_valid=X_valid, y_valid=y.iloc[30:])

    out_dir = tmp_path / "shap_report"
    predictor.export_shap_report(
        X_sample=X_valid if not X_valid.empty else X_train,
        output_dir=out_dir,
        prefix="unit_test_model",
        max_samples=100,
    )

    png_path = out_dir / "unit_test_model_summary.png"
    csv_path = out_dir / "unit_test_model_importance.csv"
    txt_path = out_dir / "unit_test_model_features.txt"

    assert png_path.exists()
    assert csv_path.exists()
    assert txt_path.exists()

