
import pandas as pd
from scipy.stats import spearmanr

def calculate_daily_drift(df_pred: pd.DataFrame, df_actual: pd.DataFrame) -> dict:
    """
    计算每日模型漂移指标
    df_pred: 包含 ['ts_code', 'pred_score']
    df_actual: 包含 ['ts_code', 'total_score']
    """
    merged = pd.merge(df_pred, df_actual, on="ts_code", how="inner")
    
    if len(merged) < 10:
        return {"status": "insufficient_data"}
        
    spearman_corr, _ = spearmanr(merged['pred_score'], merged['total_score'])
    
    # Top N Overlap
    top_n = 200
    top_pred = set(merged.nlargest(top_n, 'pred_score')['ts_code'])
    top_actual = set(merged.nlargest(top_n, 'total_score')['ts_code'])
    overlap = len(top_pred.intersection(top_actual)) / top_n
    
    return {
        "spearman": spearman_corr,
        "top200_overlap": overlap,
        "sample_size": len(merged)
    }

def alert_if_drift_detected(metrics: dict, threshold_spearman=0.8):
    if metrics.get("status") == "insufficient_data":
        print("⚠️ Data insufficient for drift check.")
        return
        
    sp = metrics['spearman']
    print(f"Daily Monitor: Spearman={sp:.4f}, Top200 Overlap={metrics['top200_overlap']:.2%}")
    
    if sp < threshold_spearman:
        print(f"🚨 ALERT: Model Drift Detected! Spearman {sp:.4f} < {threshold_spearman}")
    else:
        print("✅ Model Status: Healthy")
