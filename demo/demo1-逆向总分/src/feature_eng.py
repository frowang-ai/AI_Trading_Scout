
import re
from typing import List, Tuple

import numpy as np
import pandas as pd


def process_excel_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    处理Excel源数据的特征工程
    包含：One-Hot编码、清洗、特征选择
    """
    df_clean = df.copy()
    
    # 1. Industry One-Hot Encoding
    if "行业" in df_clean.columns:
        df_clean["行业"] = df_clean["行业"].astype(str).fillna("未知")
        # Clean special chars
        df_clean["行业"] = df_clean["行业"].str.replace(r"[\[\]']", "", regex=True)
        
        industry_dummies = pd.get_dummies(df_clean["行业"], prefix="industry")
        industry_dummies = industry_dummies.astype(int)
        df_clean = pd.concat([df_clean.drop(columns=["行业"]), industry_dummies], axis=1)
        
    # 2. Drop non-numeric columns (except keys)
    drop_cols = ["ts_code", "trade_date", "total_score"]
    
    # Clean all-NaN columns
    df_clean = df_clean.dropna(axis=1, how="all")
    
    # Select numeric columns
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in drop_cols]
    
    X = df_clean[feature_cols].copy()
    y = df_clean["total_score"].copy()
    
    # 3. Sanitize feature names for XGBoost
    clean_cols = [re.sub(r"[\[\]<>]", "", c) for c in X.columns]
    X.columns = clean_cols
    feature_cols = clean_cols
    
    return X, y, feature_cols


def process_tushare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    处理Tushare源数据的特征工程
    """
    df_clean = df.copy()
    drop_cols = ["ts_code", "trade_date", "total_score"]
    
    df_clean = df_clean.dropna(axis=1, how="all")
    
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in drop_cols]
    
    X = df_clean[feature_cols].copy()
    y = df_clean["total_score"].copy()

    return X, y, feature_cols
