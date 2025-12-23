"""
全量11月数据训练 + 12月Hold-out验证
目标：逆向工程外部"总分"算法
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path
import sys
import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle
from typing import List

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from get_data_tushare.config import DATA_ROOT

# 路径配置（遵循AGENTS.md规范）
CURRENT_DIR = Path(__file__).parent.resolve()
EXTERNAL_DIR_NOV = PROJECT_ROOT / "刘丰硕的代码/2025年11月潘哥数据（全）"
EXTERNAL_DIR_DEC = PROJECT_ROOT / "刘丰硕的代码/12月数据（12.8更新"
OUTPUT_DIR = CURRENT_DIR / "output_full"

# 创建输出目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def list_dates_from_dir(directory: Path) -> List[str]:
    """从目录中提取所有日期（排除BJS文件）"""
    dates = set()
    for fp in directory.glob("*.xlsx"):
        if "bjs" in fp.stem.lower():
            continue
        # 提取日期：20251103_data_sma_feature_color.xlsx -> 20251103
        parts = fp.stem.split("_")
        if parts and parts[0].startswith("2025"):
            dates.add(parts[0])
    return sorted(list(dates))

def load_external_target(date_str: str, external_dir: Path) -> pd.DataFrame:
    ext_fp = None
    for fp in external_dir.glob(f"{date_str}*.xlsx"):
        if "bjs" not in fp.stem.lower():
            ext_fp = fp
            break
    
    if not ext_fp:
        print(f"  Warning: No external file for {date_str}")
        return pd.DataFrame()
    
    # 2. 读取外部数据
    try:
        df_ext = pd.read_excel(ext_fp)
    except Exception as e:
        print(f"  Error reading {ext_fp.name}: {e}")
        return pd.DataFrame()

    cols_map = {str(c): str(c) for c in df_ext.columns}
    def get_col(*names):
        for n in names:
            if n in cols_map:
                return n
        return None
    
    c_code = get_col("code2", "ts_code", "代码", "code")
    c_score = get_col("总分", "total_score")
    
    if not c_code or not c_score:
        print(f"  Warning: Missing columns in {ext_fp.name}")
        return pd.DataFrame()
    
    # 4. 构造目标变量DataFrame
    df_target = pd.DataFrame()
    base = df_ext[c_code].astype(str).str.strip()
    if base.str.contains(r"\.").any():
        df_target["ts_code"] = base
    else:
        is_bjs = "bjs" in ext_fp.stem.lower()
        suffix = base.str[0].map(lambda x: ".SH" if x == "6" else (".SZ" if not is_bjs else ".BJ"))
        df_target["ts_code"] = base + suffix
    
    df_target["total_score"] = pd.to_numeric(df_ext[c_score], errors="coerce")
    df_target["trade_date"] = date_str
    df_target = df_target.dropna(subset=["total_score"])
    
    return df_target

def load_tushare_features(date_str: str) -> pd.DataFrame:
    def read_parquet_safe(name: str) -> pd.DataFrame:
        fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"{name}_{date_str}.parquet"
        if fp.exists():
            return pd.read_parquet(fp)
        return pd.DataFrame()
    
    df_daily = read_parquet_safe("daily")
    df_basic = read_parquet_safe("daily_basic")
    df_factor = read_parquet_safe("stk_factor")
    df_pro = read_parquet_safe("stk_factor_pro")
    
    if df_daily.empty:
        print(f"  Warning: No daily data for {date_str}")
        return pd.DataFrame()

    df_features = df_daily.copy()
    for df_other in [df_basic, df_factor, df_pro]:
        if not df_other.empty:
            df_other["ts_code"] = df_other["ts_code"].astype(str)
            df_features = pd.merge(df_features, df_other, on=["ts_code", "trade_date"], how="left", suffixes=("", "_dup"))
    
    df_features = df_features.loc[:, ~df_features.columns.str.endswith("_dup")]
    
    df_industry = read_parquet_safe("industry_concept_panel")
    if not df_industry.empty and "ts_code" in df_industry.columns:
        df_industry = df_industry.copy()
        df_industry["ts_code"] = df_industry["ts_code"].astype(str)
        df_features = pd.merge(df_features, df_industry, on="ts_code", how="left")
    
    return df_features

def load_single_day(date_str: str, external_dir: Path) -> pd.DataFrame:
    df_target = load_external_target(date_str, external_dir)
    if df_target.empty:
        return pd.DataFrame()
    df_features = load_tushare_features(date_str)
    if df_features.empty:
        return pd.DataFrame()

    df_final = pd.merge(df_target, df_features, on=["ts_code", "trade_date"], how="inner")
    
    return df_final

def load_all_data(external_dir: Path, month_name: str) -> pd.DataFrame:
    """加载指定月份的所有数据"""
    print(f"\n{'='*60}")
    print(f"Loading {month_name} Data...")
    print(f"{'='*60}")
    
    dates = list_dates_from_dir(external_dir)
    print(f"Found {len(dates)} trading days: {dates}")
    
    all_data = []
    for date_str in dates:
        print(f"  Loading {date_str}...", end=" ")
        df = load_single_day(date_str, external_dir)
        if not df.empty:
            print(f"✓ {len(df)} rows")
            all_data.append(df)
        else:
            print("✗ Failed")
    
    if not all_data:
        raise ValueError(f"No data loaded for {month_name}")
    
    df_concat = pd.concat(all_data, ignore_index=True)
    print(f"\n{month_name} Total: {len(df_concat)} rows, {len(df_concat.columns)} columns")
    
    return df_concat

def prepare_features(df: pd.DataFrame):
    """准备特征矩阵X和目标y"""
    drop_cols = ["ts_code", "trade_date", "total_score"]
    
    df_clean = df.dropna(axis=1, how="all")
    
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in drop_cols]
    
    X = df_clean[feature_cols].copy()
    y = df_clean["total_score"].copy()
    
    print(f"\nFeature Engineering:")
    print(f"  Total Features: {len(feature_cols)}")
    print(f"  Samples: {len(X)}")
    print(f"  Target (total_score) - Mean: {y.mean():.2f}, Std: {y.std():.2f}, Range: [{y.min():.1f}, {y.max():.1f}]")
    
    return X, y, feature_cols

def run_kfold_cv(X, y, n_splits: int = 5):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    rows = []
    fold = 1
    for train_index, valid_index in kf.split(X):
        X_train = X.iloc[train_index]
        X_valid = X.iloc[valid_index]
        y_train = y.iloc[train_index]
        y_valid = y.iloc[valid_index]
        model = xgb.XGBRegressor(
            n_estimators=1000,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            n_jobs=-1,
            random_state=42,
            early_stopping_rounds=50,
            eval_metric="rmse",
        )
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_train, y_train), (X_valid, y_valid)],
            verbose=False,
        )
        y_pred = model.predict(X_valid)
        r2 = r2_score(y_valid, y_pred)
        mae = mean_absolute_error(y_valid, y_pred)
        rmse = np.sqrt(mean_squared_error(y_valid, y_pred))
        rows.append(
            {
                "fold": fold,
                "r2": r2,
                "mae": mae,
                "rmse": rmse,
                "best_iteration": model.best_iteration,
            }
        )
        fold += 1
    df_cv = pd.DataFrame(rows)
    print("\nK-Fold CV Results:")
    print(df_cv.to_string(index=False))
    cv_path = OUTPUT_DIR / "cv_results.csv"
    df_cv.to_csv(cv_path, index=False, encoding="utf-8")
    print(f"\nCV results saved to: {cv_path}")
    return df_cv

def plot_training_curves(train_rmse, valid_rmse, holdout_rmse, output_path: Path):
    rounds = list(range(1, len(train_rmse) + 1))
    plt.figure(figsize=(10, 6))
    plt.plot(rounds, train_rmse, label="train_rmse")
    plt.plot(rounds, valid_rmse, label="valid_rmse")
    if holdout_rmse is not None:
        holdout_rounds = list(range(1, len(holdout_rmse) + 1))
        plt.plot(holdout_rounds, holdout_rmse, label="holdout_rmse")
    plt.xlabel("Boosting Round")
    plt.ylabel("RMSE")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"\nTraining curves saved to: {output_path}")

def train_xgboost_with_curves(X_train, y_train, X_valid, y_valid, X_holdout=None, y_holdout=None):
    print(f"\n{'='*60}")
    print("Training XGBoost Model...")
    print(f"{'='*60}")
    
    model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42,
        early_stopping_rounds=50,
        eval_metric="rmse",
    )
    
    print("  Fitting model...")
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_train, y_train), (X_valid, y_valid)],
        verbose=False,
    )
    
    print(f"  Best iteration: {model.best_iteration}")
    
    evals_result = model.evals_result()
    train_rmse = evals_result.get("validation_0", {}).get("rmse", [])
    valid_rmse = evals_result.get("validation_1", {}).get("rmse", [])
    holdout_rmse = None
    if X_holdout is not None and y_holdout is not None:
        booster = model.get_booster()
        if model.best_iteration is not None:
            num_rounds = model.best_iteration + 1
        else:
            num_rounds = len(train_rmse)
        holdout_rmse = []
        d_holdout = xgb.DMatrix(X_holdout)
        for i in range(1, num_rounds + 1):
            y_pred_holdout = booster.predict(d_holdout, ntree_limit=i)
            rmse = np.sqrt(mean_squared_error(y_holdout, y_pred_holdout))
            holdout_rmse.append(rmse)
    curves_path = OUTPUT_DIR / "training_curves.png"
    if train_rmse and valid_rmse:
        plot_training_curves(train_rmse, valid_rmse, holdout_rmse, curves_path)
    return model

def evaluate_model(model, X, y, dataset_name: str):
    """评估模型性能"""
    y_pred = model.predict(X)
    
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    # 计算预测误差分布
    errors = y - y_pred
    
    print(f"\n{dataset_name} Performance:")
    print(f"  R² Score:  {r2:.4f}")
    print(f"  MAE:       {mae:.4f}")
    print(f"  RMSE:      {rmse:.4f}")
    print(f"  Error Distribution:")
    print(f"    Mean Error: {errors.mean():.4f}")
    print(f"    Std Error:  {errors.std():.4f}")
    print(f"    Min Error:  {errors.min():.4f}")
    print(f"    Max Error:  {errors.max():.4f}")
    
    return {
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "predictions": y_pred,
        "errors": errors
    }

def shap_analysis(model, X_sample, feature_cols):
    """SHAP可解释性分析"""
    print(f"\n{'='*60}")
    print("SHAP Analysis (Feature Importance)...")
    print(f"{'='*60}")
    
    # 采样以加速计算（SHAP很慢）
    if len(X_sample) > 1000:
        print(f"  Sampling 1000 rows from {len(X_sample)} for SHAP...")
        X_shap = X_sample.sample(n=1000, random_state=42)
    else:
        X_shap = X_sample
    
    print("  Computing SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_shap)
    
    # 计算全局特征重要性
    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": np.abs(shap_values).mean(axis=0)
    }).sort_values("importance", ascending=False)
    
    print("\nTop 20 Important Features:")
    print(importance_df.head(20).to_string(index=False))
    
    # 保存SHAP summary plot
    plt.figure(figsize=(12, 10))
    shap.summary_plot(shap_values, X_shap, feature_names=feature_cols, show=False, max_display=20)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "shap_summary_full.png", dpi=150)
    print(f"\n  SHAP plot saved to: {OUTPUT_DIR / 'shap_summary_full.png'}")
    plt.close()
    
    return importance_df

def main():
    """主流程"""
    print(f"\n{'#'*60}")
    print("# 逆向工程总分算法 - 全量11月训练 + 12月验证")
    print(f"{'#'*60}")
    
    # ========== Step 1: 加载11月数据 ==========
    df_nov = load_all_data(EXTERNAL_DIR_NOV, "November")
    
    # ========== Step 2: 准备特征 ==========
    X_nov, y_nov, feature_cols = prepare_features(df_nov)
    
    print(f"\n{'='*60}")
    print("Splitting November Data (Train/Test = 80/20)...")
    print(f"{'='*60}")
    
    indices = np.arange(len(X_nov))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.2, random_state=42
    )
    X_train = X_nov.iloc[train_idx]
    X_test = X_nov.iloc[test_idx]
    y_train = y_nov.iloc[train_idx]
    y_test = y_nov.iloc[test_idx]
    df_train = df_nov.iloc[train_idx].reset_index(drop=True)
    df_test = df_nov.iloc[test_idx].reset_index(drop=True)
    
    print(f"  Train Set: {len(X_train)} samples")
    print(f"  Test Set:  {len(X_test)} samples")
    
    model = train_xgboost_with_curves(X_train, y_train, X_test, y_test)
    
    print(f"\n{'='*60}")
    print("Evaluating on November Data...")
    print(f"{'='*60}")
    
    results_train = evaluate_model(model, X_train, y_train, "Train Set (80% of Nov)")
    results_test = evaluate_model(model, X_test, y_test, "Test Set (20% of Nov)")

    df_train_pred = df_train[["ts_code", "trade_date", "total_score"]].copy()
    df_train_pred["predicted_score"] = results_train["predictions"]
    df_train_pred["error"] = results_train["errors"]
    df_train_pred.to_csv(OUTPUT_DIR / "prediction_nov_train.csv", index=False, encoding="utf-8")

    df_test_pred = df_test[["ts_code", "trade_date", "total_score"]].copy()
    df_test_pred["predicted_score"] = results_test["predictions"]
    df_test_pred["error"] = results_test["errors"]
    df_test_pred.to_csv(OUTPUT_DIR / "prediction_nov_test.csv", index=False, encoding="utf-8")
    
    # ========== Step 6: SHAP分析 ==========
    importance_df = shap_analysis(model, X_test, feature_cols)
    
    # ========== Step 7: 保存模型 ==========
    model_path = OUTPUT_DIR / "xgboost_model_nov.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved to: {model_path}")
    
    importance_df.to_csv(OUTPUT_DIR / "feature_importance.csv", index=False, encoding="utf-8")
    
    # ========== Step 8: 加载12月数据（Hold-out） ==========
    print(f"\n{'='*60}")
    print("Loading December Data (Hold-out Validation)...")
    print(f"{'='*60}")
    
    try:
        df_dec = load_all_data(EXTERNAL_DIR_DEC, "December")
        
        # 准备12月特征（必须使用相同的特征列）
        X_dec = df_dec[feature_cols].copy()
        y_dec = df_dec["total_score"].copy()
        
        print(f"\nDecember Data Loaded:")
        print(f"  Samples: {len(X_dec)}")
        print(f"  Target - Mean: {y_dec.mean():.2f}, Std: {y_dec.std():.2f}")
        
        # ========== Step 9: 在12月数据上验证 ==========
        print(f"\n{'='*60}")
        print("Evaluating on December Data (Hold-out)...")
        print(f"{'='*60}")
        
        results_dec = evaluate_model(model, X_dec, y_dec, "December Hold-out Set")
        
        # 保存12月预测结果
        df_dec_pred = df_dec[["ts_code", "trade_date", "total_score"]].copy()
        df_dec_pred["predicted_score"] = results_dec["predictions"]
        df_dec_pred["error"] = results_dec["errors"]
        df_dec_pred.to_csv(OUTPUT_DIR / "december_predictions.csv", index=False, encoding="utf-8")
        print(f"\nDecember predictions saved to: {OUTPUT_DIR / 'december_predictions.csv'}")
        
    except Exception as e:
        print(f"\n⚠️  December data loading failed: {e}")
        print("Skipping hold-out validation.")
    
    # ========== Step 10: 生成总结报告 ==========
    print(f"\n{'#'*60}")
    print("# Summary Report")
    print(f"{'#'*60}")
    print(f"\nNovember Train Set R²: {results_train['r2']:.4f}")
    print(f"November Test Set R²:  {results_test['r2']:.4f}")
    if 'results_dec' in locals():
        print(f"December Hold-out R²:  {results_dec['r2']:.4f}")
    
    print(f"\nAll outputs saved to: {OUTPUT_DIR}")
    print("\n✓ Training Complete!")

if __name__ == "__main__":
    main()
