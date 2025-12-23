
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Mock the environment
PROJECT_ROOT = Path(r'f:\codeF\llm_projects\AI_Trading_Scout')
EXTERNAL_DIR_NOV = PROJECT_ROOT / "刘丰硕的代码/2025年11月潘哥数据（全）"

def load_single_day_test(date_str, external_dir):
    # Simplified version of the function in the script
    ext_fp = None
    for fp in external_dir.glob(f"{date_str}*.xlsx"):
        if "bjs" not in fp.stem.lower():
            ext_fp = fp
            break
    
    if not ext_fp:
        print("File not found")
        return pd.DataFrame()
    
    df_ext = pd.read_excel(ext_fp, nrows=100) # Read only 100 rows for speed
    
    # Rename columns logic
    cols_map = {str(c): str(c) for c in df_ext.columns}
    def get_col(*names):
        for n in names:
            if n in cols_map:
                return n
        return None
    
    c_code = get_col("code2", "ts_code", "代码", "code")
    c_score = get_col("总分", "total_score")
    
    # Drop logic
    cols_to_drop = ["Unnamed: 0", c_code, "名称", "日期", c_score, "lst_close", "长期", "短期"]
    cols_to_drop = [c for c in cols_to_drop if c and c in df_ext.columns]
    df_clean = df_ext.drop(columns=cols_to_drop, errors="ignore")

    print(f"Columns before encoding: {df_clean.columns.tolist()}")

    if "行业" in df_clean.columns:
        print("Found '行业' column")
        df_clean["行业"] = df_clean["行业"].astype(str).fillna("未知")
        industry_dummies = pd.get_dummies(df_clean["行业"], prefix="industry")
        # Force int type to ensure they are picked up as numeric
        industry_dummies = industry_dummies.astype(int) 
        df_clean = pd.concat([df_clean.drop(columns=["行业"]), industry_dummies], axis=1)
    else:
        print("'行业' column NOT found")
    
    # Select numeric
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    print(f"Numeric columns selected: {[c for c in numeric_cols if 'industry' in c]}")
    
    return df_clean

# Run for one day
load_single_day_test("20251103", EXTERNAL_DIR_NOV)
