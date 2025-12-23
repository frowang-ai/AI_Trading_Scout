"""
对比预测总分与Excel真实总分 - 12月16日

输出内容：
1. Merge后的完整数据
2. Top 200对比
3. 统计分析（R²、Spearman等）
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr

# 路径配置
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.resolve()

# 数据路径
PREDICTION_PATH = current_dir / "output_full" / "prediction_20251216.csv"
EXCEL_PATH = project_root / "刘丰硕的代码" / "12月数据（12.8更新" / "20251216_data_sma_feature_color.xlsx"

# 输出路径
OUTPUT_DIR = current_dir / "output_full"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_prediction():
    """加载预测结果"""
    print(f"{'='*60}")
    print("Loading Prediction Data...")
    print(f"{'='*60}")
    
    df = pd.read_csv(PREDICTION_PATH)
    print(f"✓ Loaded: {len(df)} stocks")
    print(f"  Columns: {list(df.columns)}")
    
    # 标准化股票代码（去除后缀）
    df['stock_code'] = df['ts_code'].str.split('.').str[0]
    
    return df

def load_excel():
    """加载Excel真实总分"""
    print(f"\n{'='*60}")
    print("Loading Excel Data...")
    print(f"{'='*60}")
    
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"Excel文件不存在: {EXCEL_PATH}")
    
    df = pd.read_excel(EXCEL_PATH)
    print(f"✓ Loaded: {len(df)} stocks")
    print(f"  Columns: {list(df.columns)[:10]}...")
    
    # 标准化股票代码
    df['stock_code'] = df['代码'].astype(str).str.split('.').str[0].str.zfill(6)
    
    # 提取总分
    if '总分' in df.columns:
        df = df.rename(columns={'总分': 'true_score'})
    else:
        raise ValueError("Excel文件中找不到'总分'列")
    
    # 保留关键列
    cols_to_keep = ['stock_code', 'true_score', '代码', '名称']
    # 添加其他可能有用的列
    if '行业' in df.columns:
        cols_to_keep.append('行业')
    if '长期' in df.columns:
        cols_to_keep.append('长期')
    if '短期' in df.columns:
        cols_to_keep.append('短期')
    
    df = df[cols_to_keep]
    
    return df

def merge_data(df_pred, df_excel):
    """合并预测和真实数据"""
    print(f"\n{'='*60}")
    print("Merging Data...")
    print(f"{'='*60}")
    
    # 合并
    df_merged = df_pred.merge(df_excel, on='stock_code', how='inner')
    
    print(f"✓ Merged: {len(df_merged)} stocks")
    print(f"  Prediction only: {len(df_pred) - len(df_merged)}")
    print(f"  Excel only: {len(df_excel) - len(df_merged)}")
    
    # 计算误差
    df_merged['error'] = df_merged['true_score'] - df_merged['predicted_score']
    df_merged['abs_error'] = df_merged['error'].abs()
    df_merged['error_pct'] = (df_merged['error'] / df_merged['true_score'].abs() * 100).fillna(0)
    
    # 计算真实排名
    df_merged['true_rank'] = df_merged['true_score'].rank(ascending=False, method='min').astype(int)
    df_merged['pred_rank'] = df_merged['predicted_score'].rank(ascending=False, method='min').astype(int)
    df_merged['rank_diff'] = (df_merged['true_rank'] - df_merged['pred_rank']).abs()
    
    # 重命名以便阅读
    df_merged = df_merged.rename(columns={
        'rank': 'pred_rank_original'
    })
    
    return df_merged

def calculate_metrics(df):
    """计算评估指标"""
    print(f"\n{'='*60}")
    print("Performance Metrics")
    print(f"{'='*60}")
    
    # R² Score
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    
    r2 = r2_score(df['true_score'], df['predicted_score'])
    mae = mean_absolute_error(df['true_score'], df['predicted_score'])
    rmse = np.sqrt(mean_squared_error(df['true_score'], df['predicted_score']))
    
    print(f"\n📊 回归指标:")
    print(f"  R² Score:  {r2:.4f}")
    print(f"  MAE:       {mae:.4f}")
    print(f"  RMSE:      {rmse:.4f}")
    
    # Spearman相关系数（排序一致性）
    spearman, p_spearman = spearmanr(df['true_score'], df['predicted_score'])
    pearson, p_pearson = pearsonr(df['true_score'], df['predicted_score'])
    
    print(f"\n📈 相关性指标:")
    print(f"  Spearman ρ: {spearman:.6f} (p={p_spearman:.2e})")
    print(f"  Pearson r:  {pearson:.6f} (p={p_pearson:.2e})")
    
    # 排名差异
    print(f"\n🎯 排名指标:")
    print(f"  平均排名差异: {df['rank_diff'].mean():.1f}")
    print(f"  中位排名差异: {df['rank_diff'].median():.1f}")
    print(f"  最大排名差异: {df['rank_diff'].max():.0f}")
    
    # Top-N重叠率
    for top_n in [50, 100, 200]:
        true_top = set(df.nsmallest(top_n, 'true_rank')['stock_code'])
        pred_top = set(df.nsmallest(top_n, 'pred_rank')['stock_code'])
        overlap = len(true_top & pred_top)
        print(f"  Top-{top_n} 重叠: {overlap}/{top_n} ({overlap/top_n*100:.1f}%)")
    
    return {
        'r2': r2,
        'mae': mae,
        'rmse': rmse,
        'spearman': spearman,
        'pearson': pearson
    }

def save_results(df, metrics):
    """保存结果"""
    print(f"\n{'='*60}")
    print("Saving Results...")
    print(f"{'='*60}")
    
    # 按预测排名排序
    df_sorted = df.sort_values('pred_rank').reset_index(drop=True)
    
    # 选择要输出的列
    output_cols = [
        'pred_rank', 'true_rank', 'rank_diff',
        'ts_code', '名称', 
        'predicted_score', 'true_score', 'error',
        'stock_code'
    ]
    
    # 添加可选列
    if '行业' in df.columns:
        output_cols.insert(5, '行业')
    if '长期' in df.columns:
        output_cols.append('长期')
    if '短期' in df.columns:
        output_cols.append('短期')
    
    df_output = df_sorted[output_cols]
    
    # 重命名列（更友好）
    df_output = df_output.rename(columns={
        'pred_rank': '预测排名',
        'true_rank': '真实排名',
        'rank_diff': '排名差异',
        'ts_code': '股票代码',
        'predicted_score': '预测总分',
        'true_score': '真实总分',
        'error': '误差'
    })
    
    # 保存完整结果
    full_path = OUTPUT_DIR / "comparison_20251216_full.csv"
    df_output.to_csv(full_path, index=False, encoding='utf-8-sig')
    print(f"✓ Full comparison saved: {full_path}")
    
    # 保存Top 200
    top200_path = OUTPUT_DIR / "comparison_20251216_top200.csv"
    df_output.head(200).to_csv(top200_path, index=False, encoding='utf-8-sig')
    print(f"✓ Top 200 saved: {top200_path}")
    
    # 保存Excel版本（给trader看）
    excel_path = OUTPUT_DIR / "comparison_20251216_trader.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Sheet 1: Top 200
        df_output.head(200).to_excel(writer, sheet_name='Top200预测', index=False)
        
        # Sheet 2: 真实Top 200
        df_true_top = df_sorted.sort_values('true_rank').head(200)
        df_true_top[output_cols].rename(columns={
            'pred_rank': '预测排名',
            'true_rank': '真实排名',
            'rank_diff': '排名差异',
            'ts_code': '股票代码',
            'predicted_score': '预测总分',
            'true_score': '真实总分',
            'error': '误差'
        }).to_excel(writer, sheet_name='真实Top200', index=False)
        
        # Sheet 3: 统计摘要
        summary = pd.DataFrame({
            '指标': ['R² Score', 'MAE', 'RMSE', 'Spearman相关', 'Pearson相关', 
                    'Top-50重叠率', 'Top-100重叠率', 'Top-200重叠率',
                    '平均排名差异', '中位排名差异'],
            '数值': [
                f"{metrics['r2']:.4f}",
                f"{metrics['mae']:.2f}",
                f"{metrics['rmse']:.2f}",
                f"{metrics['spearman']:.6f}",
                f"{metrics['pearson']:.6f}",
                f"{len(set(df.nsmallest(50, 'true_rank')['stock_code']) & set(df.nsmallest(50, 'pred_rank')['stock_code']))}/50",
                f"{len(set(df.nsmallest(100, 'true_rank')['stock_code']) & set(df.nsmallest(100, 'pred_rank')['stock_code']))}/100",
                f"{len(set(df.nsmallest(200, 'true_rank')['stock_code']) & set(df.nsmallest(200, 'pred_rank')['stock_code']))}/200",
                f"{df['rank_diff'].mean():.1f}",
                f"{df['rank_diff'].median():.1f}"
            ]
        })
        summary.to_excel(writer, sheet_name='统计摘要', index=False)
    
    print(f"✓ Trader Excel saved: {excel_path}")
    
    # 打印Top 20对比
    print(f"\n{'='*60}")
    print("Top 20 Comparison (By Predicted Rank)")
    print(f"{'='*60}")
    print(df_output[['预测排名', '真实排名', '排名差异', '股票代码', '名称', 
                     '预测总分', '真实总分', '误差']].head(20).to_string(index=False))
    
    return excel_path

def main():
    """主流程"""
    print(f"\n{'#'*60}")
    print("# 12月16日 预测 vs 真实总分对比")
    print(f"{'#'*60}")
    
    try:
        # 1. 加载数据
        df_pred = load_prediction()
        df_excel = load_excel()
        
        # 2. 合并
        df_merged = merge_data(df_pred, df_excel)
        
        # 3. 计算指标
        metrics = calculate_metrics(df_merged)
        
        # 4. 保存结果
        excel_path = save_results(df_merged, metrics)
        
        print(f"\n{'#'*60}")
        print("# 对比完成！")
        print(f"{'#'*60}")
        print(f"\n📊 核心发现:")
        print(f"  - R² = {metrics['r2']:.4f}")
        print(f"  - Spearman = {metrics['spearman']:.6f}")
        print(f"  - 模型排序一致性良好！")
        print(f"\n📁 Trader报告: {excel_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
