"""
排序一致性检验 - 检查预测总分与真实总分的排序相关性

核心逻辑：
- 如果总分用于股票排序，那么R²不是最重要的指标
- 更关键的是：预测排序 vs 真实排序的相关性
- 使用 Spearman 相关系数（排序相关）和 Kendall's Tau（排序一致性）
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, kendalltau
import matplotlib.pyplot as plt

# 路径配置
current_dir = Path(__file__).parent.resolve()
output_excel = current_dir / "output_excel_only"

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

def plot_correlation_trends(df_daily, output_dir):
    """绘制排序相关性趋势图"""
    
    if df_daily is None or len(df_daily) == 0:
        return
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Spearman 相关系数
    axes[0].plot(range(len(df_daily)), df_daily['spearman'], marker='o', linewidth=2, markersize=6, label='Spearman ρ')
    axes[0].axhline(df_daily['spearman'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df_daily["spearman"].mean():.4f}')
    axes[0].set_xlabel('Trading Day Index', fontsize=12)
    axes[0].set_ylabel('Spearman Correlation', fontsize=12)
    axes[0].set_title('Daily Spearman Rank Correlation (Predicted vs True Score)', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[0].set_ylim([0.7, 1.0])
    
    # Kendall 相关系数
    axes[1].plot(range(len(df_daily)), df_daily['kendall'], marker='s', linewidth=2, markersize=6, label='Kendall τ', color='green')
    axes[1].axhline(df_daily['kendall'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df_daily["kendall"].mean():.4f}')
    axes[1].set_xlabel('Trading Day Index', fontsize=12)
    axes[1].set_ylabel('Kendall Tau', fontsize=12)
    axes[1].set_title('Daily Kendall Rank Correlation (Predicted vs True Score)', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    axes[1].set_ylim([0.5, 1.0])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'rank_correlation_trends.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Correlation trends plot saved to: {output_dir / 'rank_correlation_trends.png'}")
    plt.close()

def analyze_rank_differences(df, sample_date=None):
    """分析具体的排名差异"""
    
    if 'trade_date' in df.columns and sample_date is None:
        # 随机选择一天作为示例
        sample_date = df['trade_date'].unique()[0]
    
    if sample_date:
        df = df[df['trade_date'] == sample_date].copy()
        print(f"\n{'='*60}")
        print(f"Rank Difference Analysis for {sample_date}")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"Rank Difference Analysis (All Data)")
        print(f"{'='*60}")
    
    # 计算排名
    df['true_rank'] = df['true_score'].rank(ascending=False, method='min')
    df['pred_rank'] = df['predicted_score'].rank(ascending=False, method='min')
    df['rank_diff'] = abs(df['true_rank'] - df['pred_rank'])
    
    print(f"Total stocks: {len(df)}")
    print(f"\nRank Difference Statistics:")
    print(f"  Mean abs difference: {df['rank_diff'].mean():.1f}")
    print(f"  Median abs difference: {df['rank_diff'].median():.1f}")
    print(f"  Max abs difference: {df['rank_diff'].max():.0f}")
    print(f"  Std abs difference: {df['rank_diff'].std():.1f}")
    
    # 排名差异分布
    print(f"\nRank Difference Distribution:")
    print(f"  Within Top 50:   {(df['rank_diff'] <= 50).sum()} stocks ({(df['rank_diff'] <= 50).sum()/len(df)*100:.1f}%)")
    print(f"  Within Top 100:  {(df['rank_diff'] <= 100).sum()} stocks ({(df['rank_diff'] <= 100).sum()/len(df)*100:.1f}%)")
    print(f"  Within Top 200:  {(df['rank_diff'] <= 200).sum()} stocks ({(df['rank_diff'] <= 200).sum()/len(df)*100:.1f}%)")
    print(f"  Within Top 500:  {(df['rank_diff'] <= 500).sum()} stocks ({(df['rank_diff'] <= 500).sum()/len(df)*100:.1f}%)")
    
    # 查看Top 20的具体情况
    print(f"\n{'='*60}")
    print(f"Top 20 Stocks Comparison (True vs Predicted)")
    print(f"{'='*60}")
    
    df_top_true = df.nsmallest(20, 'true_rank')[['ts_code', 'true_score', 'predicted_score', 'true_rank', 'pred_rank', 'rank_diff']]
    print("\nBy True Score (Top 20):")
    print(df_top_true.to_string(index=False))
    
    return df

def main():
    """主流程"""
    
    print(f"\n{'#'*60}")
    print("# 排序一致性检验 - Excel特征版本")
    print(f"{'#'*60}")
    
    # 1. 加载12月预测结果
    print(f"\n{'='*60}")
    print("Loading December Predictions...")
    print(f"{'='*60}")
    
    df_dec = load_predictions(output_excel / "december_predictions_excel.csv")
    
    # 统一列名
    if 'total_score' in df_dec.columns:
        df_dec = df_dec.rename(columns={'total_score': 'true_score'})
    
    # 2. 计算排序相关性
    df_daily_corr = calculate_rank_correlation(df_dec)
    
    # 3. Top-N分析
    for top_n in [50, 100, 200]:
        df_overlap = analyze_top_stocks(df_dec, top_n=top_n)
    
    # 4. 绘制趋势图
    if df_daily_corr is not None:
        plot_correlation_trends(df_daily_corr, output_excel)
    
    # 5. 排名差异分析（选择第一天作为示例）
    if 'trade_date' in df_dec.columns:
        sample_date = sorted(df_dec['trade_date'].unique())[0]
        df_analyzed = analyze_rank_differences(df_dec, sample_date=sample_date)
    else:
        df_analyzed = analyze_rank_differences(df_dec)
    
    print(f"\n{'#'*60}")
    print("# 结论")
    print(f"{'#'*60}")
    print("""
关键发现：
1. Spearman相关系数 > 0.9 说明排序高度一致
2. Top-N重叠率 > 80% 说明选股能力强
3. 平均排名差异 < 100 说明实用价值高

如果上述指标良好，即使R²=0.77也足够用于实际交易！
    """)

if __name__ == "__main__":
    main()
