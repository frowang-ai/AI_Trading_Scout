
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import shap
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# Windows 推荐
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False  # 避免坐标轴负号显示成方块

class ScorePredictor:
    """
    Demo1 统一版回归模型封装：
    - 负责 XGBoost 训练 / 评估 / 预测
    - 记录特征名与元数据
    - 支持模型与元数据的持久化
    - 支持导出全量特征的 SHAP 报告
    """

    def __init__(
        self,
        params: Optional[Dict[str, Any]] = None,
        model_path: Optional[Path] = None,
    ) -> None:
        self.params: Dict[str, Any] = params or {
            "n_estimators": 1000,
            "learning_rate": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "n_jobs": -1,
            "random_state": 42,
            "early_stopping_rounds": 50,
            "eval_metric": "rmse",
        }
        self.model: Optional[xgb.XGBRegressor] = None
        self.evals_result: Dict[str, Dict[str, List[float]]] = {}
        self.feature_names: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.model_path: Optional[Path] = model_path

    # -------- 元数据 --------
    def set_metadata(self, **kwargs: Any) -> None:
        self.metadata.update(kwargs)

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self.metadata)

    # -------- 训练与评估 --------
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_valid: Optional[pd.DataFrame] = None,
        y_valid: Optional[pd.Series] = None,
        eval_name: str = "validation",
    ) -> "ScorePredictor":
        """
        训练模型，记录训练过程与特征名。
        """
        X_train = self._clean_data(X_train)
        self.feature_names = list(X_train.columns)

        eval_set = [(X_train, y_train)]
        eval_names = ["train"]

        if X_valid is not None and y_valid is not None:
            X_valid = self._clean_data(X_valid)
            eval_set.append((X_valid, y_valid))
            eval_names.append(eval_name)

        self.model = xgb.XGBRegressor(**self.params)
        # 兼容旧版本 xgboost：不在 fit 中显式传 eval_metric，
        # 仅通过构造参数中的 eval_metric 控制评估指标。
        self.model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            verbose=False,
        )
        self.evals_result = self.model.evals_result()
        return self

    def get_learning_curves(self) -> Dict[str, List[float]]:
        """
        返回训练/验证集上 RMSE 曲线用于画图。
        """
        if not self.evals_result:
            return {}

        results: Dict[str, List[float]] = {}
        for name, metrics in self.evals_result.items():
            if "rmse" in metrics:
                results[f"{name}_rmse"] = metrics["rmse"]
        return results

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("模型尚未加载或训练。")

        X = self._clean_data(X)

        if self.feature_names:
            # 对齐特征：缺失列补 0，多余列丢弃
            X = X.reindex(columns=self.feature_names, fill_value=0.0)

        return self.model.predict(X)

    def evaluate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        dataset_name: str = "Test Set",
        verbose: bool = True,
    ) -> Dict[str, float]:
        """
        在给定数据集上评估性能。
        """
        y_pred = self.predict(X)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y, y_pred)))

        if verbose:
            print(f"\n{dataset_name} Performance:")
            print(f"  R² Score:  {r2:.4f}")
            print(f"  MAE:       {mae:.4f}")
            print(f"  RMSE:      {rmse:.4f}")

        return {"r2": r2, "mae": mae, "rmse": rmse}

    # -------- 模型持久化 --------
    def save(
        self,
        model_path: Optional[Path] = None,
        meta_path: Optional[Path] = None,
    ) -> None:
        """
        保存模型和元数据（特征名、训练配置等）。
        """
        if self.model is None:
            raise RuntimeError("当前没有可保存的模型，请先训练。")

        final_model_path = model_path or self.model_path
        if final_model_path is None:
            raise ValueError("未指定模型保存路径。")

        final_model_path.parent.mkdir(parents=True, exist_ok=True)
        with final_model_path.open("wb") as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {final_model_path}")

        if meta_path is None:
            meta_path = final_model_path.with_suffix(".meta.pkl")

        meta = {
            "feature_names": self.feature_names,
            "params": self.params,
            "metadata": self.metadata,
        }

        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with meta_path.open("wb") as f:
            pickle.dump(meta, f)
        print(f"Model metadata saved to {meta_path}")

    def load(
        self,
        model_path: Optional[Path] = None,
        meta_path: Optional[Path] = None,
    ) -> bool:
        """
        加载模型与元数据，返回是否成功。
        """
        final_model_path = model_path or self.model_path
        if final_model_path is None or not final_model_path.exists():
            return False

        with final_model_path.open("rb") as f:
            self.model = pickle.load(f)
        print(f"Model loaded from {final_model_path}")

        if meta_path is None:
            meta_path = final_model_path.with_suffix(".meta.pkl")

        if meta_path.exists():
            with meta_path.open("rb") as f:
                meta = pickle.load(f)
            self.feature_names = meta.get("feature_names", [])
            self.params = meta.get("params", self.params)
            self.metadata = meta.get("metadata", {})
            print(f"Model metadata loaded from {meta_path}")

        self.model_path = final_model_path
        return True

    # -------- SHAP 报告 --------
    def compute_shap_values(
        self,
        X_sample: pd.DataFrame,
        max_samples: int = 5000,
    ) -> shap._explanation.Explanation:
        """
        基于当前模型与给定样本，计算 SHAP 值。
        返回 shap.Explanation 对象，供上层绘图或导出 CSV 使用。
        """
        if self.model is None:
            raise RuntimeError("模型尚未加载或训练，无法计算 SHAP。")

        if self.feature_names:
            X_sample = X_sample.reindex(columns=self.feature_names, fill_value=0.0)

        X_sample = self._clean_data(X_sample)

        if len(X_sample) > max_samples:
            X_sample = X_sample.sample(n=max_samples, random_state=42)

        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer(X_sample)
        return shap_values

    def export_shap_report(
        self,
        X_sample: pd.DataFrame,
        output_dir: Path,
        prefix: str = "shap_full",
        max_samples: int = 5000,
    ) -> None:
        """
        生成一份“全部特征”的 SHAP 报告：
        - 保存 shap summary bar 图（全局重要性）
        - 保存 per-feature 平均 |SHAP| 到 CSV，便于后续做 feature_importance_grouped
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        shap_values = self.compute_shap_values(X_sample=X_sample, max_samples=max_samples)

        # 全局 summary bar 图
        plt.figure(figsize=(10, 6))
        shap.plots.bar(shap_values, show=False, max_display=50)
        plt.tight_layout()
        png_path = output_dir / f"{prefix}_summary.png"
        plt.savefig(png_path, dpi=150)
        plt.close()
        print(f"SHAP summary plot saved to {png_path}")

        # 平均 |SHAP| CSV
        abs_values = np.abs(shap_values.values)
        mean_abs = abs_values.mean(axis=0)
        feature_importance = pd.DataFrame(
            {
                "feature": shap_values.feature_names,
                "mean_abs_shap": mean_abs,
            }
        ).sort_values("mean_abs_shap", ascending=False)

        csv_path = output_dir / f"{prefix}_importance.csv"
        feature_importance.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"SHAP feature importance saved to {csv_path}")

        # 同时打印一次“我们最终用了哪些特征”
        features_txt_path = output_dir / f"{prefix}_features.txt"
        with features_txt_path.open("w", encoding="utf-8") as f:
            for name in shap_values.feature_names:
                f.write(f"{name}\n")
        print(f"Feature list saved to {features_txt_path}")

    # -------- 内部工具 --------
    def _clean_data(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.replace([np.inf, -np.inf], np.nan)
        return X
