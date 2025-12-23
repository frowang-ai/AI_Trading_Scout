"""
排序一致性检验 - Tushare特征版本

检查output_full目录下的Tushare特征模型的排序一致性
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, kendalltau
import matplotlib.pyplot as plt

# 路径配置
current_dir = Path(__file__).parent.resolve()
output_tushare = current_dir / "output_full"

def load_predictions(csv_path):
    """加载预测结果"""
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} predictions from {csv_path.name}")
    print(f"Columns: {list(df.columns)}")
    return df

def calculate_rank_correlation(df):
    """计算排序相关性指标"""
    
    # 1. 整体相关性（全部股票混在一起）
    spearman_all, p_spearman_all = spearmanr(df['true_score'], df['predicted_score'])
    kendall_all, p_kendall_all = kendalltau(df['true_score'], df['predicted_score'])
    
    print(f"\n{'='*60}")
    print("Overall Rank Correlation (All Stocks Merged)")
    print(f"{'='*60}")
    print(f"Spearman's ρ:  {spearman_all:.6f} (p-value: {p_spearman_all:.2e})")
    print(f"Kendall's τ:   {kendall_all:.6f} (p-value: {p_kendall_all:.2e})")
    
    # 2. 按日期分组计算（每天内部排序）
    if 'trade_date' in df.columns:
        daily_results = []
        
        for date in sorted(df['trade_date'].unique()):
            df_day = df[df['trade_date'] == date]
            
            if len(df_day) > 1:
                sp_corr, sp_p = spearmanr(df_day['true_score'], df_day['predicted_score'])
                kd_corr, kd_p = kendalltau(df_day['true_score'], df_day['predicted_score'])
                
                daily_results.append({
                    'date': date,
                    'n_stocks': len(df_day),
                    'spearman': sp_corr,
                    'kendall': kd_corr,
                    'spearman_p': sp_p,
                    'kendall_p': kd_p
                })
        
        df_daily = pd.DataFrame(daily_results)
        
        print(f"\n{'='*60}")
        print(f"Daily Rank Correlation ({len(df_daily)} trading days)")
        print(f"{'='*60}")
        print(f"Average Spearman's ρ: {df_daily['spearman'].mean():.6f} (std: {df_daily['spearman'].std():.6f})")
        print(f"Average Kendall's τ:  {df_daily['kendall'].mean():.6f} (std: {df_daily['kendall'].std():.6f})")
        print(f"\nSpearman ρ - Min: {df_daily['spearman'].min():.6f}, Max: {df_daily['spearman'].max():.6f}")
        print(f"Kendall τ  - Min: {df_daily['kendall'].min():.6f}, Max: {df_daily['kendall'].max():.6f}")
        
        return df_daily
    
    return None

def analyze_top_stocks(df, top_n=100):
    """分析Top N股票的排序一致性"""
    
    print(f"\n{'='*60}")
    print(f"Top-{top_n} Stocks Ranking Analysis")
    print(f"{'='*60}")
    
    if 'trade_date' not in df.columns:
        # 整体分析
        df_sorted_true = df.nlargest(top_n, 'true_score')
        df_sorted_pred = df.nlargest(top_n, 'predicted_score')
        
        overlap = len(set(df_sorted_true['ts_code']) & set(df_sorted_pred['ts_code']))
        print(f"Overlap in Top-{top_n}: {overlap}/{top_n} ({overlap/top_n*100:.1f}%)")
    
    else:
        # 每日分析
        daily_overlaps = []
        
        for date in sorted(df['trade_date'].unique()):
            df_day = df[df['trade_date'] == date]
            
            if len(df_day) >= top_n:
                df_sorted_true = df_day.nlargest(top_n, 'true_score')
                df_sorted_pred = df_day.nlargest(top_n, 'predicted_score')
                
                overlap = len(set(df_sorted_true['ts_code']) & set(df_sorted_pred['ts_code']))
                overlap_pct = overlap / top_n * 100
                
                daily_overlaps.append({
                    'date': date,
                    'overlap': overlap,
                    'overlap_pct': overlap_pct
                })
        
        df_overlap = pd.DataFrame(daily_overlaps)
        
        print(f"Average Top-{top_n} Overlap: {df_overlap['overlap_pct'].mean():.2f}% (std: {df_overlap['overlap_pct'].std():.2f}%)")
        print(f"Min/Max Overlap: {df_overlap['overlap_pct'].min():.2f}% / {df_overlap['overlap_pct'].max():.2f}%")
        
        return df_overlap
    
    return None

def main():
    """主流程"""
    
    print(f"\n{'#'*60}")
    print("# 排序一致性检验 - Tushare特征版本")
    print(f"{'#'*60}")
    
    # 1. 加载12月预测结果
    print(f"\n{'='*60}")
    print("Loading December Predictions (Tushare Features)...")
    print(f"{'='*60}")
    
    df_dec = load_predictions(output_tushare / "december_predictions.csv")
    
    # 统一列名
    if 'total_score' in df_dec.columns:
        df_dec = df_dec.rename(columns={'total_score': 'true_score'})
    
    # 2. 计算排序相关性
    df_daily_corr = calculate_rank_correlation(df_dec)
    
    # 3. Top-N分析
    for top_n in [50, 100, 200]:
        df_overlap = analyze_top_stocks(df_dec, top_n=top_n)
    
    print(f"\n{'#'*60}")
    print("# Tushare特征版本 - 总结")
    print(f"{'#'*60}")
    
    if df_daily_corr is not None:
        print(f"\nSpearman 平均值: {df_daily_corr['spearman'].mean():.6f}")
        print(f"Kendall 平均值:  {df_daily_corr['kendall'].mean():.6f}")

if __name__ == "__main__":
    main()
