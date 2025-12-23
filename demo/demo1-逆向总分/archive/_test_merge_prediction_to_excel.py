"""
将预测总分merge到Excel完整原始表中

目的：给trader提供完整数据表 + 预测总分列，方便直接使用
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

def normalize_stock_code(code):
    """标准化股票代码为6位数字"""
    code_str = str(code).strip()
    # 移除后缀
    if '.' in code_str:
        code_str = code_str.split('.')[0]
    # 补齐6位
    if code_str.isdigit():
        return code_str.zfill(6)
    return code_str

print(f"{'='*70}")
print("将预测总分merge到Excel完整表中")
print(f"{'='*70}\n")

# 1. 加载预测结果
print("1. 加载预测数据...")
pred_df = pd.read_csv(PREDICTION_PATH)
# 从ts_code提取股票代码并标准化
pred_df['stock_code_norm'] = pred_df['ts_code'].str.split('.').str[0].apply(normalize_stock_code)
print(f"   ✓ {len(pred_df)} 只股票\n")

# 2. 加载Excel完整原始数据（保留所有列）
print("2. 加载Excel完整数据...")
excel_df = pd.read_excel(EXCEL_PATH)
excel_df['stock_code_norm'] = excel_df['代码'].apply(normalize_stock_code)
print(f"   ✓ {len(excel_df)} 只股票")
print(f"   ✓ {len(excel_df.columns)} 列: {', '.join(str(c) for c in excel_df.columns[:5])}...\n")

# 3. 将预测分数merge到Excel表（保留Excel所有列）
print("3. 合并预测分数到Excel表...")
merged = excel_df.merge(
    pred_df[['stock_code_norm', 'predicted_score']], 
    on='stock_code_norm', 
    how='left'  # 保留所有Excel股票
)

# 删除临时列
merged = merged.drop('stock_code_norm', axis=1)

print(f"   ✓ 合并完成: {len(merged)} 只股票")
print(f"   - 有预测分数: {merged['predicted_score'].notna().sum()} 只")
print(f"   - 无预测分数: {merged['predicted_score'].isna().sum()} 只")
print(f"   ✓ 总列数: {len(merged.columns)} (原始 {len(excel_df.columns)} + 预测总分 1)\n")

# 4. 按预测分数排序（无预测的排最后）
merged_sorted = merged.sort_values('predicted_score', ascending=False, na_position='last')

# 5. 输出完整表格
output_path = OUTPUT_DIR / "20251216_data_with_prediction.xlsx"
print("4. 输出完整表格...")
merged_sorted.to_excel(output_path, index=False, engine='openpyxl')
print(f"   ✓ {output_path}")
print(f"   ✓ {len(merged_sorted)} 只股票 × {len(merged_sorted.columns)} 列\n")

# 6. 计算性能指标（仅针对有预测的股票）
merged_valid = merged[merged['predicted_score'].notna()].copy()
print(f"5. 性能指标 (基于 {len(merged_valid)} 只有效股票):")

r2 = 1 - np.sum((merged_valid['总分'] - merged_valid['predicted_score'])**2) / \
         np.sum((merged_valid['总分'] - merged_valid['总分'].mean())**2)
spearman_corr, _ = spearmanr(merged_valid['predicted_score'], merged_valid['总分'])
pearson_corr, _ = pearsonr(merged_valid['predicted_score'], merged_valid['总分'])

print(f"   - R² Score: {r2:.4f}")
print(f"   - Spearman相关系数: {spearman_corr:.6f}")
print(f"   - Pearson相关系数: {pearson_corr:.6f}")

# 排名分析
merged_valid['pred_rank'] = merged_valid['predicted_score'].rank(ascending=False, method='first')
merged_valid['actual_rank'] = merged_valid['总分'].rank(ascending=False, method='first')
merged_valid['rank_diff'] = abs(merged_valid['pred_rank'] - merged_valid['actual_rank'])

for k in [50, 100, 200]:
    pred_topk = set(merged_valid.nsmallest(k, 'pred_rank').index)
    actual_topk = set(merged_valid.nsmallest(k, 'actual_rank').index)
    overlap = len(pred_topk & actual_topk)
    print(f"   - Top-{k} Overlap: {overlap}/{k} ({overlap/k*100:.1f}%)")

print(f"   - 平均排名差异: {merged_valid['rank_diff'].mean():.1f} 位\n")

# 7. 展示预测Top 20
print("6. 预测 Top 20 股票:")
print(f"{'-'*70}")
key_cols = ['代码', '名称', 'predicted_score', '总分']
# 动态选择可用列
optional_cols = ['涨跌幅', 'close', '成交额', '换手率', 'zhangdiefu2']
for col in optional_cols:
    if col in merged_valid.columns:
        key_cols.append(col)
        
top20 = merged_valid.sort_values('predicted_score', ascending=False).head(20)[key_cols]
top20_display = top20.copy()
top20_display.columns = ['代码', '简称', '预测总分', '真实总分'] + \
                         [c for c in key_cols[4:]]
print(top20_display.to_string(index=False))

print(f"\n{'='*70}")
print("✅ 完成！Trader可以直接使用 20251216_data_with_prediction.xlsx")
print(f"{'='*70}")
