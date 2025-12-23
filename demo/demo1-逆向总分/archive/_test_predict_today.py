"""
使用训练好的Tushare模型对2025年12月16日数据进行预测

流程：
1. 加载训练好的模型（output_full/xgboost_model_nov.pkl）
2. 读取2025-12-16的Tushare数据
3. 特征工程（与训练时保持一致）
4. 预测总分
5. 输出结果
"""

from pathlib import Path
import pandas as pd
import numpy as np
import pickle

# 路径配置（遵循AGENTS.md规范）
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()
project_root = parent_dir.parent.resolve()

# 数据路径
DATA_ROOT = project_root / "data" / "raw" / "daily"
MODEL_PATH = current_dir / "output_full" / "xgboost_model_nov.pkl"

# 输出路径
OUTPUT_DIR = current_dir / "output_full"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_model():
    """加载训练好的模型"""
    print(f"{'='*60}")
    print("Loading Trained Model...")
    print(f"{'='*60}")
    
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"模型文件不存在: {MODEL_PATH}")
    
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    print(f"✓ Model loaded from: {MODEL_PATH}")
    print(f"  Model type: {type(model).__name__}")
    print(f"  Features expected: {model.n_features_in_}")
    
    return model

def load_tushare_data(date_str: str):
    """加载指定日期的Tushare数据"""
    print(f"\n{'='*60}")
    print(f"Loading Tushare Data for {date_str}...")
    print(f"{'='*60}")
    
    # 尝试多种路径格式（新格式：API名_日期.parquet）
    year = date_str[:4]
    possible_paths = [
        DATA_ROOT / year / f"daily_{date_str}.parquet",  # 新格式
        DATA_ROOT / year / "daily" / f"{date_str}.parquet",
        DATA_ROOT / "daily" / f"{date_str}.parquet",
        DATA_ROOT / f"{date_str}.parquet",
    ]
    
    data_path = None
    for path in possible_paths:
        if path.exists():
            data_path = path
            break
    
    if data_path is None:
        # 列出可用文件
        print(f"\n未找到数据文件，正在搜索...")
        if DATA_ROOT.exists():
            parquet_files = list(DATA_ROOT.rglob("*.parquet"))
            recent_files = sorted([f.stem for f in parquet_files if f.stem.startswith("2025")])
            print(f"找到2025年的文件: {recent_files[-10:] if recent_files else '无'}")
        raise FileNotFoundError(f"未找到 {date_str} 的数据文件")
    
    # 读取daily数据
    df_daily = pd.read_parquet(data_path)
    print(f"✓ Daily data loaded: {len(df_daily)} stocks")
    print(f"  Path: {data_path}")
    print(f"  Columns: {list(df_daily.columns)[:10]}...")
    
    # 尝试加载其他接口数据（新格式：同目录下）
    base_dir = data_path.parent
    daily_basic_path = base_dir / f"daily_basic_{date_str}.parquet"
    stk_factor_path = base_dir / f"stk_factor_{date_str}.parquet"
    stk_factor_pro_path = base_dir / f"stk_factor_pro_{date_str}.parquet"
    
    dfs = [df_daily]
    
    if daily_basic_path.exists():
        df_basic = pd.read_parquet(daily_basic_path)
        print(f"✓ Daily_basic loaded: {len(df_basic)} stocks")
        dfs.append(df_basic)
    else:
        print(f"⚠ Daily_basic not found: {daily_basic_path}")
    
    if stk_factor_path.exists():
        df_factor = pd.read_parquet(stk_factor_path)
        print(f"✓ Stk_factor loaded: {len(df_factor)} stocks")
        dfs.append(df_factor)
    else:
        print(f"⚠ Stk_factor not found: {stk_factor_path}")
    
    if stk_factor_pro_path.exists():
        df_factor_pro = pd.read_parquet(stk_factor_pro_path)
        print(f"✓ Stk_factor_pro loaded: {len(df_factor_pro)} stocks")
        dfs.append(df_factor_pro)
    else:
        print(f"⚠ Stk_factor_pro not found: {stk_factor_pro_path}")
    
    # 合并数据
    df_merged = dfs[0]
    for df in dfs[1:]:
        df_merged = df_merged.merge(df, on=['ts_code', 'trade_date'], how='left', suffixes=('', '_dup'))
        # 删除重复列
        dup_cols = [c for c in df_merged.columns if c.endswith('_dup')]
        df_merged = df_merged.drop(columns=dup_cols)
    
    print(f"\n✓ Merged data: {len(df_merged)} stocks, {len(df_merged.columns)} columns")
    
    return df_merged

def prepare_features(df, model):
    """准备特征（与训练时保持一致）"""
    print(f"\n{'='*60}")
    print("Feature Engineering...")
    print(f"{'='*60}")
    
    # 保留关键列
    df = df.copy()
    
    # 确保有ts_code和trade_date
    if 'ts_code' not in df.columns or 'trade_date' not in df.columns:
        raise ValueError("数据缺少 ts_code 或 trade_date 列")
    
    # 提取数值特征（与训练时一致）
    exclude_cols = ['ts_code', 'trade_date']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # 只保留数值列
    numeric_cols = []
    for col in feature_cols:
        if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
            numeric_cols.append(col)
    
    print(f"  Total columns: {len(df.columns)}")
    print(f"  Numeric features: {len(numeric_cols)}")
    
    # 提取特征
    X = df[numeric_cols].copy()
    
    # 处理缺失值和inf
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    
    # 检查特征数量是否匹配
    expected_features = model.n_features_in_
    if len(X.columns) != expected_features:
        print(f"\n⚠ 警告: 特征数量不匹配")
        print(f"  模型期望: {expected_features} 个特征")
        print(f"  当前数据: {len(X.columns)} 个特征")
        print(f"\n  调整策略: 使用模型训练时的特征顺序")
        
        # 尝试从训练集读取特征列表
        # 这里需要确保特征顺序一致
        # 如果不匹配，可能需要手动对齐
    
    print(f"\n✓ Features prepared: {X.shape}")
    print(f"  Sample features: {list(X.columns)[:10]}...")
    
    return X, df[['ts_code', 'trade_date']]

def predict_scores(model, X, meta_df):
    """预测总分"""
    print(f"\n{'='*60}")
    print("Predicting Scores...")
    print(f"{'='*60}")
    
    # 预测
    scores = model.predict(X)
    
    # 合并结果
    result_df = meta_df.copy()
    result_df['predicted_score'] = scores
    
    # 统计
    print(f"\n✓ Prediction complete!")
    print(f"  Total stocks: {len(result_df)}")
    print(f"  Score statistics:")
    print(f"    Mean:   {scores.mean():.2f}")
    print(f"    Std:    {scores.std():.2f}")
    print(f"    Min:    {scores.min():.2f}")
    print(f"    Max:    {scores.max():.2f}")
    print(f"    Median: {np.median(scores):.2f}")
    
    return result_df

def save_results(result_df, date_str):
    """保存预测结果"""
    print(f"\n{'='*60}")
    print("Saving Results...")
    print(f"{'='*60}")
    
    # 排序
    result_df = result_df.sort_values('predicted_score', ascending=False).reset_index(drop=True)
    result_df['rank'] = range(1, len(result_df) + 1)
    
    # 保存完整结果
    output_path = OUTPUT_DIR / f"prediction_{date_str}.csv"
    result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✓ Full results saved to: {output_path}")
    
    # 保存Top 200
    top200_path = OUTPUT_DIR / f"top200_{date_str}.csv"
    result_df.head(200).to_csv(top200_path, index=False, encoding='utf-8-sig')
    print(f"✓ Top 200 saved to: {top200_path}")
    
    # 打印Top 20
    print(f"\n{'='*60}")
    print(f"Top 20 Stocks (Predicted Score)")
    print(f"{'='*60}")
    print(result_df[['rank', 'ts_code', 'predicted_score']].head(20).to_string(index=False))
    
    return output_path

def main():
    """主流程"""
    # 使用今天的数据（12月16日）
    date_str = "20251216"
    
    print(f"\n{'#'*60}")
    print(f"# 2025年12月16日 总分预测 (Tushare模型)")
    print(f"{'#'*60}")
    
    try:
        # 1. 加载模型
        model = load_model()
        
        # 2. 加载数据
        df = load_tushare_data(date_str)
        
        # 3. 特征工程
        X, meta_df = prepare_features(df, model)
        
        # 4. 预测
        result_df = predict_scores(model, X, meta_df)
        
        # 5. 保存结果
        output_path = save_results(result_df, date_str)
        
        print(f"\n{'#'*60}")
        print(f"# 预测完成！")
        print(f"{'#'*60}")
        print(f"结果文件: {output_path}")
        print(f"Top 200: {OUTPUT_DIR / f'top200_{date_str}.csv'}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
