"""
仅使用外部Excel特征训练 - 对比实验
目标：验证外部Excel自身特征对"总分"的预测能力
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path
import sys
import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle
from typing import List

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# 路径配置
CURRENT_DIR = Path(__file__).parent.resolve()
EXTERNAL_DIR_NOV = PROJECT_ROOT / "刘丰硕的代码/2025年11月潘哥数据（全）"
EXTERNAL_DIR_DEC = PROJECT_ROOT / "刘丰硕的代码/12月数据（12.8更新"
OUTPUT_DIR = CURRENT_DIR / "output_excel_only"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def list_dates_from_dir(directory: Path) -> List[str]:
    """从目录中提取所有日期（排除BJS文件）"""
    dates = set()
    for fp in directory.glob("*.xlsx"):
        if "bjs" in fp.stem.lower():
            continue
        parts = fp.stem.split("_")
        if parts and parts[0].startswith("2025"):
            dates.add(parts[0])
    return sorted(list(dates))

def load_single_day(date_str: str, external_dir: Path) -> pd.DataFrame:
    """加载单日数据（仅使用外部Excel特征）"""
    # 1. 找到外部文件
    ext_fp = None
    for fp in external_dir.glob(f"{date_str}*.xlsx"):
        if "bjs" not in fp.stem.lower():
            ext_fp = fp
            break
    
    if not ext_fp:
        return pd.DataFrame()
    
    # 2. 读取外部数据
    try:
        df_ext = pd.read_excel(ext_fp)
    except Exception as e:
        print(f"  Error reading {ext_fp.name}: {e}")
        return pd.DataFrame()
    
    # 3. 标准化列名
    cols_map = {str(c): str(c) for c in df_ext.columns}
    def get_col(*names):
        for n in names:
            if n in cols_map:
                return n
        return None
    
    c_code = get_col("code2", "ts_code", "代码", "code")
    c_date = get_col("trade_date", "日期")
    c_score = get_col("总分", "total_score")
    
    if not c_code or not c_score:
        return pd.DataFrame()
    
    # 4. 处理ts_code
    base = df_ext[c_code].astype(str).str.strip()
    if not base.str.contains(r"\.").any():
        is_bjs = "bjs" in ext_fp.stem.lower()
        suffix = base.str[0].map(lambda x: ".SH" if x == "6" else (".SZ" if not is_bjs else ".BJ"))
        df_ext["ts_code"] = base + suffix
    else:
        df_ext["ts_code"] = base
    
    # 5. 处理trade_date
    if c_date:
        s = df_ext[c_date]
        if pd.api.types.is_datetime64_any_dtype(s):
            df_ext["trade_date"] = s.dt.strftime("%Y%m%d")
        else:
            df_ext["trade_date"] = pd.to_datetime(s.astype(str).str.slice(0, 10), errors="coerce").dt.strftime("%Y%m%d")
    else:
        df_ext["trade_date"] = date_str
    
    # 6. 提取total_score
    df_ext["total_score"] = pd.to_numeric(df_ext[c_score], errors="coerce")
    
    cols_to_drop = [
        "Unnamed: 0",  # 索引列
        c_code, "代码", "code", "code2",  # 股票代码的各种命名
        "名称", "name", "name2",  # 股票名称
        c_date, "日期",  # 日期的各种命名（但保留我们新建的trade_date）
        c_score, "总分" if c_score != "总分" else None,  # 总分列（这是目标变量）
        "lst_close",  # 昨收价（可能造成数据泄露）
        "长期", "短期",  # 类别特征
    ]
    
    # 过滤None并删除
    cols_to_drop = [c for c in cols_to_drop if c and c in df_ext.columns]
    df_clean = df_ext.drop(columns=cols_to_drop, errors="ignore")

    if "行业" in df_clean.columns:
        df_clean["行业"] = df_clean["行业"].astype(str).fillna("未知")
        # 清理行业名称中的特殊字符 (如 ['银行'] -> 银行)
        df_clean["行业"] = df_clean["行业"].str.replace(r"[\[\]']", "", regex=True)
        
        industry_dummies = pd.get_dummies(df_clean["行业"], prefix="industry")
        # 强制转换为int (0/1)，确保被识别为数值特征
        industry_dummies = industry_dummies.astype(int)
        df_clean = pd.concat([df_clean.drop(columns=["行业"]), industry_dummies], axis=1)
    
    # 8. 确保关键列存在
    if "ts_code" not in df_clean.columns or "trade_date" not in df_clean.columns or "total_score" not in df_clean.columns:
        return pd.DataFrame()
    
    # 9. 只保留数值列（加上关键列）
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    keep_cols = ["ts_code", "trade_date", "total_score"] + [c for c in numeric_cols if c not in ["ts_code", "trade_date", "total_score"]]
    df_numeric = df_clean[keep_cols]
    
    # 10. 删除total_score为NaN的行
    df_numeric = df_numeric.dropna(subset=["total_score"])
    
    return df_numeric

def load_all_data(external_dir: Path, month_name: str) -> pd.DataFrame:
    """加载指定月份的所有数据"""
    print(f"\n{'='*60}")
    print(f"Loading {month_name} Data (Excel Features Only)...")
    print(f"{'='*60}")
    
    dates = list_dates_from_dir(external_dir)
    print(f"Found {len(dates)} trading days: {dates}")
    
    all_data = []
    for date_str in dates:
        print(f"  Loading {date_str}...", end=" ")
        df = load_single_day(date_str, external_dir)
        if not df.empty:
            print(f"✓ {len(df)} rows, {len(df.columns)-3} features")
            all_data.append(df)
        else:
            print("✗ Failed")
    
    if not all_data:
        raise ValueError(f"No data loaded for {month_name}")
    
    df_concat = pd.concat(all_data, ignore_index=True)
    print(f"\n{month_name} Total: {len(df_concat)} rows, {len(df_concat.columns)-3} features")
    
    return df_concat

def prepare_features(df: pd.DataFrame):
    """准备特征矩阵X和目标y"""
    drop_cols = ["ts_code", "trade_date", "total_score"]
    
    # 清理全NaN列
    df_clean = df.dropna(axis=1, how="all")
    
    # 选择数值列
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in drop_cols]
    
    X = df_clean[feature_cols].copy()
    
    # Sanitize feature names for XGBoost (remove [, ], <)
    import re
    clean_cols = [re.sub(r"[\[\]<>]", "", c) for c in X.columns]
    X.columns = clean_cols
    feature_cols = clean_cols

    y = df_clean["total_score"].copy()
    
    print(f"\nFeature Engineering:")
    print(f"  Total Features: {len(feature_cols)}")
    print(f"  Feature names: {feature_cols[:20]}...")  # 显示前20个
    print(f"  Samples: {len(X)}")
    print(f"  Target (total_score) - Mean: {y.mean():.2f}, Std: {y.std():.2f}, Range: [{y.min():.1f}, {y.max():.1f}]")
    
    return X, y, feature_cols

def train_xgboost(X_train, y_train, X_test, y_test):
    """训练XGBoost模型"""
    print(f"\n{'='*60}")
    print("Training XGBoost Model (Excel Features Only)...")
    print(f"{'='*60}")
    
    # 数据清理：替换 inf 和极大值
    print("  Cleaning data (replacing inf/nan)...")
    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.replace([np.inf, -np.inf], np.nan)
    
    # 填充 NaN（用中位数）
    X_train = X_train.fillna(X_train.median())
    X_test = X_test.fillna(X_train.median())  # 使用训练集中位数
    
    model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42,
        early_stopping_rounds=50
    )
    
    print("  Fitting model...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=False
    )
    
    print(f"  Best iteration: {model.best_iteration}")
    
    return model

def evaluate_model(model, X, y, dataset_name: str):
    """评估模型性能"""
    y_pred = model.predict(X)
    
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
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
    print("SHAP Analysis (Excel Feature Importance)...")
    print(f"{'='*60}")
    
    if len(X_sample) > 1000:
        print(f"  Sampling 1000 rows from {len(X_sample)} for SHAP...")
        X_shap = X_sample.sample(n=1000, random_state=42)
    else:
        X_shap = X_sample
    
    print("  Computing SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_shap)
    
    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": np.abs(shap_values).mean(axis=0)
    }).sort_values("importance", ascending=False)
    
    print("\n🔥 Top 30 Important Excel Features:")
    print(importance_df.head(30).to_string(index=False))
    
    # 保存完整特征重要性到CSV
    importance_df.to_csv(OUTPUT_DIR / "feature_importance_excel.csv", index=False, encoding="utf-8-sig")
    print(f"  Full feature importance saved to: {OUTPUT_DIR / 'feature_importance_excel.csv'}")
    
    # 保存SHAP summary plot
    plt.figure(figsize=(12, 10))
    shap.summary_plot(shap_values, X_shap, feature_names=feature_cols, show=False, max_display=30)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "shap_summary_excel.png", dpi=150)
    print(f"  SHAP plot saved to: {OUTPUT_DIR / 'shap_summary_excel.png'}")
    plt.close()
    
    return importance_df

def main():
    """主流程"""
    print(f"\n{'#'*60}")
    print("# 逆向工程总分算法 - 仅使用外部Excel特征")
    print(f"{'#'*60}")
    
    # Step 1: 加载11月数据
    df_nov = load_all_data(EXTERNAL_DIR_NOV, "November")
    
    # Step 2: 准备特征
    X_nov, y_nov, feature_cols = prepare_features(df_nov)
    
    # Step 3: Train/Test Split
    print(f"\n{'='*60}")
    print("Splitting November Data (Train/Test = 80/20)...")
    print(f"{'='*60}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_nov, y_nov, test_size=0.2, random_state=42
    )
    
    print(f"  Train Set: {len(X_train)} samples")
    print(f"  Test Set:  {len(X_test)} samples")
    
    # Step 4: 训练模型
    model = train_xgboost(X_train, y_train, X_test, y_test)
    
    # Step 5: 评估模型
    print(f"\n{'='*60}")
    print("Evaluating on November Data...")
    print(f"{'='*60}")
    
    results_train = evaluate_model(model, X_train, y_train, "Train Set (80% of Nov)")
    results_test = evaluate_model(model, X_test, y_test, "Test Set (20% of Nov)")
    
    # Step 6: SHAP分析
    importance_df = shap_analysis(model, X_test, feature_cols)
    
    # Step 7: 保存模型
    model_path = OUTPUT_DIR / "xgboost_model_excel.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved to: {model_path}")
    
    importance_df.to_csv(OUTPUT_DIR / "feature_importance_excel.csv", index=False, encoding="utf-8")
    
    # Step 8: 加载12月数据
    print(f"\n{'='*60}")
    print("Loading December Data (Hold-out Validation)...")
    print(f"{'='*60}")
    
    try:
        df_dec = load_all_data(EXTERNAL_DIR_DEC, "December")
        
        X_dec = df_dec[feature_cols].copy()
        y_dec = df_dec["total_score"].copy()
        
        print(f"\nDecember Data Loaded:")
        print(f"  Samples: {len(X_dec)}")
        print(f"  Target - Mean: {y_dec.mean():.2f}, Std: {y_dec.std():.2f}")
        
        # Step 9: 在12月数据上验证
        print(f"\n{'='*60}")
        print("Evaluating on December Data (Hold-out)...")
        print(f"{'='*60}")
        
        results_dec = evaluate_model(model, X_dec, y_dec, "December Hold-out Set")
        
        df_dec_pred = df_dec[["ts_code", "trade_date", "total_score"]].copy()
        df_dec_pred["predicted_score"] = results_dec["predictions"]
        df_dec_pred["error"] = results_dec["errors"]
        df_dec_pred.to_csv(OUTPUT_DIR / "december_predictions_excel.csv", index=False, encoding="utf-8")
        print(f"\nDecember predictions saved to: {OUTPUT_DIR / 'december_predictions_excel.csv'}")
        
    except Exception as e:
        print(f"\n⚠️  December data loading failed: {e}")
        print("Skipping hold-out validation.")
    
    # Step 10: 生成总结报告
    print(f"\n{'#'*60}")
    print("# Summary Report (Excel Features Only)")
    print(f"{'#'*60}")
    print(f"\nNovember Train Set R²: {results_train['r2']:.4f}")
    print(f"November Test Set R²:  {results_test['r2']:.4f}")
    if 'results_dec' in locals():
        print(f"December Hold-out R²:  {results_dec['r2']:.4f}")
    
    print(f"\nAll outputs saved to: {OUTPUT_DIR}")
    print("\n✓ Training Complete!")
    
    print(f"\n{'='*60}")
    print("对比：Tushare特征 vs Excel特征")
    print(f"{'='*60}")
    print("请查看两个输出目录的结果进行对比：")
    print(f"  - output_full/ (Tushare特征)")
    print(f"  - output_excel_only/ (Excel特征)")

if __name__ == "__main__":
    main()
