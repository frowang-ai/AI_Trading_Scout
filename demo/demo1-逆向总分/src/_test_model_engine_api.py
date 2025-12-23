from pathlib import Path

import numpy as np
import pandas as pd

from model_engine import ScorePredictor


def _make_dummy_data(n_samples: int = 50, n_features: int = 4) -> tuple[pd.DataFrame, pd.Series]:
    """
    构造一份很小的虚拟训练数据，用于验证 ScorePredictor 接口是否工作正常。
    不依赖任何外部数据文件，确保在任意环境下都可以运行。
    """
    rng = np.random.RandomState(42)
    X = pd.DataFrame(
        rng.randn(n_samples, n_features),
        columns=[f"f{i}" for i in range(n_features)],
    )
    y = pd.Series(rng.randn(n_samples), name="target")
    return X, y


def test_score_predictor_basic_fit_and_save(tmp_path: Path) -> None:
    """
    验证统一后的 ScorePredictor 接口：
    - 能够完成一次简单的 fit / evaluate / predict
    - 训练后暴露 feature_names
    - 能够保存并重新加载模型
    """
    X, y = _make_dummy_data()
    X_train = X.iloc[:40]
    y_train = y.iloc[:40]
    X_valid = X.iloc[40:]
    y_valid = y.iloc[40:]

    model_path = tmp_path / "dummy_model.pkl"
    meta_path = tmp_path / "dummy_model_meta.pkl"

    predictor = ScorePredictor(model_path=model_path)
    predictor.set_metadata(source_type="unit_test")

    predictor.fit(X_train, y_train, X_valid=X_valid, y_valid=y_valid)
    metrics = predictor.evaluate(X_valid, y_valid, dataset_name="valid")
    assert "r2" in metrics and "mae" in metrics and "rmse" in metrics

    # 训练后应记录特征名
    assert predictor.feature_names
    assert set(predictor.feature_names) == set(X.columns)

    # 预测流程应可用
    y_pred = predictor.predict(X_valid)
    assert y_pred.shape[0] == X_valid.shape[0]

    # 保存与加载
    predictor.save(model_path=model_path, meta_path=meta_path)
    assert model_path.exists()
    assert meta_path.exists()

    loaded = ScorePredictor(model_path=model_path)
    ok = loaded.load(model_path=model_path, meta_path=meta_path)
    assert ok
    assert loaded.feature_names == predictor.feature_names

