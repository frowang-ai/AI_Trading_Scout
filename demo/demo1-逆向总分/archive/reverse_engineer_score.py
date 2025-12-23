from __future__ import annotations
import pandas as pd
from pathlib import Path
import sys

# Add project root to sys.path to allow importing get_data_tushare
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from get_data_tushare.config import DATA_ROOT

# External data directory
EXTERNAL_DIR = PROJECT_ROOT / "刘丰硕的代码/2025年11月潘哥数据（全）"

def get_external_file(date_str: str) -> Path | None:
    # Find file matching the date
    for fp in EXTERNAL_DIR.glob("*.xlsx"):
        if date_str in fp.stem:
            return fp
    return None

def load_data(date_str: str) -> pd.DataFrame:
    print(f"Loading data for {date_str}...")
    
    # 1. Load External Data (Target)
    ext_fp = get_external_file(date_str)
    if not ext_fp:
        raise FileNotFoundError(f"No external file found for {date_str}")
    
    print(f"  Reading external file: {ext_fp.name}")
    df_ext = pd.read_excel(ext_fp)
    
    # Normalize external columns
    # We need 'ts_code' and '总分' (Total Score)
    # And maybe 'trade_date' to be safe
    
    # Helper to find column by multiple names
    cols_map = {str(c): str(c) for c in df_ext.columns}
    def get_col(*names):
        for n in names:
            if n in cols_map:
                return n
        return None

    c_code = get_col("code2", "ts_code", "代码", "code")
    c_score = get_col("总分", "total_score")
    
    if not c_code or not c_score:
        raise ValueError(f"Could not find ts_code or total_score in {ext_fp.name}")
        
    # Standardize ts_code
    # Assuming similar logic to compare_november_data.py
    # But let's keep it simple for now and refine if needed
    # The external file usually has 'code2' as '000001.SZ' or '600000.SH'
    # If not, we might need the suffix logic.
    # Let's use the logic from compare_november_data.py for robustness
    
    df_target = pd.DataFrame()
    
    # Copy-paste logic for ts_code from compare_november_data.py
    base = df_ext[c_code].astype(str).str.strip()
    if base.str.contains(r"\.").any():
        df_target["ts_code"] = base
    else:
        # Add suffix
        is_bjs = "bjs" in ext_fp.stem.lower()
        suffix = base.str[0].map(lambda x: ".SH" if x == "6" else (".SZ" if not is_bjs else ".BJ"))
        df_target["ts_code"] = base + suffix
        
    df_target["total_score"] = pd.to_numeric(df_ext[c_score], errors="coerce")
    df_target["trade_date"] = date_str
    
    # Drop rows with missing score
    df_target = df_target.dropna(subset=["total_score"])
    
    print(f"  External data loaded: {len(df_target)} rows")

    # 2. Load Internal Data (Features)
    # We need: daily, daily_basic, stk_factor, stk_factor_pro
    
    def read_parquet_safe(name: str) -> pd.DataFrame:
        fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"{name}_{date_str}.parquet"
        if fp.exists():
            return pd.read_parquet(fp)
        print(f"  Warning: {fp.name} not found")
        return pd.DataFrame()

    df_daily = read_parquet_safe("daily")
    df_basic = read_parquet_safe("daily_basic")
    df_factor = read_parquet_safe("stk_factor")
    df_pro = read_parquet_safe("stk_factor_pro")
    
    # Merge Internal Data
    # Start with daily
    if df_daily.empty:
        raise FileNotFoundError(f"Daily data not found for {date_str}")
        
    df_features = df_daily.copy()
    
    # Merge others
    for df_other in [df_basic, df_factor, df_pro]:
        if not df_other.empty:
            # Ensure keys are string
            df_other["ts_code"] = df_other["ts_code"].astype(str)
            df_features = pd.merge(df_features, df_other, on=["ts_code", "trade_date"], how="left", suffixes=("", "_dup"))

    # Remove duplicate columns if any
    df_features = df_features.loc[:, ~df_features.columns.str.endswith("_dup")]
    
    print(f"  Internal features loaded: {len(df_features)} rows, {len(df_features.columns)} columns")
    
    # 3. Merge Target and Features
    df_final = pd.merge(df_target, df_features, on=["ts_code", "trade_date"], how="inner")
    
    print(f"  Final dataset: {len(df_final)} rows")
    return df_final

import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# ... (existing imports)

# ... (existing load_data function)

def train_model(df: pd.DataFrame):
    print("\nTraining XGBoost Model...")
    
    # Prepare X and y
    drop_cols = ["ts_code", "trade_date", "total_score"]
    # Also drop columns that are clearly not features (like 'change' which is absolute price change, maybe keep it?)
    # Drop columns with too many NaNs
    
    # 1. Handle NaNs
    # XGBoost handles NaNs, but let's check if any column is all NaNs
    df_clean = df.dropna(axis=1, how="all")
    
    # 2. Select Features
    # Exclude non-numeric
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in drop_cols]
    
    X = df_clean[feature_cols]
    y = df_clean["total_score"]
    
    print(f"  Features: {len(feature_cols)}")
    
    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train
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
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # 5. Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"  R2 Score: {r2:.4f}")
    print(f"  MAE: {mae:.4f}")
    
    # 6. SHAP Analysis
    print("  Calculating SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # Plot
    plt.figure(figsize=(10, 10))
    shap.summary_plot(shap_values, X_test, show=False)
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "shap_summary.png")
    print(f"  SHAP summary saved to {Path(__file__).parent / 'shap_summary.png'}")
    
    # Top features
    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": np.abs(shap_values).mean(axis=0)
    }).sort_values("importance", ascending=False)
    
    print("\nTop 10 Important Features:")
    print(importance.head(10))
    
    return model, importance

if __name__ == "__main__":
    try:
        # Load data for one day
        df = load_data("20251106")
        
        # Train model
        train_model(df)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

