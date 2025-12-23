"""
分析Excel数据与Tushare数据的股票数量重叠情况

对比内容：
1. 11月Excel vs 11月Tushare的股票重叠
2. 12月Excel vs 12月Tushare的股票重叠
3. 分析缺失股票的特征
"""

from pathlib import Path
import pandas as pd
import numpy as np

# 路径配置
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()

# Excel数据路径（修正：需要回到项目根目录）
project_root = parent_dir.parent.resolve()
EXCEL_NOV_DIR = project_root / "刘丰硕的代码" / "2025年11月潘哥数据（全）"
EXCEL_DEC_DIR = project_root / "刘丰硕的代码" / "12月数据（12.8更新"

# Tushare数据路径（训练使用的数据）
TUSHARE_DATA_ROOT = parent_dir.parent / "data" / "raw" / "daily"

def load_excel_stocks(excel_dir, month_name="11月"):
    """加载Excel数据的股票列表"""
    print(f"\n{'='*60}")
    print(f"Loading {month_name} Excel Data...")
    print(f"{'='*60}")
    
    if not excel_dir.exists():
        print(f"⚠ 目录不存在: {excel_dir}")
        return None
    
    # 查找xlsx文件
    xlsx_files = list(excel_dir.glob("*.xlsx"))
    if not xlsx_files:
        print(f"⚠ 未找到xlsx文件")
        return None
    
    # 按日期收集所有股票
    all_stocks = set()
    date_stocks = {}
    
    for xlsx_file in sorted(xlsx_files):
        try:
            df = pd.read_excel(xlsx_file)
            
            # 提取代码列
            if '代码' in df.columns:
                # 格式化股票代码：补齐6位，添加后缀
                stocks_raw = df['代码'].astype(str).tolist()
                stocks_formatted = []
                
                for code in stocks_raw:
                    # 移除可能的.0后缀（Excel数字格式问题）
                    code = code.split('.')[0]
                    
                    # 跳过无效代码
                    if len(code) < 5 or not code.isdigit():
                        continue
                    
                    # 补齐6位
                    code = code.zfill(6)
                    
                    stocks_formatted.append(code)
                
                date_str = xlsx_file.stem.split('_')[0]  # 提取日期
                date_stocks[date_str] = set(stocks_formatted)
                all_stocks.update(stocks_formatted)
        except Exception as e:
            print(f"⚠ 读取失败 {xlsx_file.name}: {e}")
    
    print(f"✓ {month_name} Excel数据:")
    print(f"  文件数: {len(xlsx_files)}")
    print(f"  交易日: {len(date_stocks)}")
    print(f"  独立股票数: {len(all_stocks)}")
    
    return {
        'all_stocks': all_stocks,
        'date_stocks': date_stocks,
        'files': xlsx_files
    }

def load_tushare_stocks(data_root, year_month, month_name="11月"):
    """加载Tushare数据的股票列表"""
    print(f"\n{'='*60}")
    print(f"Loading {month_name} Tushare Data...")
    print(f"{'='*60}")
    
    # 查找指定年月的parquet文件
    year = year_month[:4]
    month_prefix = year_month[:6]
    
    # Tushare数据路径
    tushare_dir = data_root / year
    if not tushare_dir.exists():
        print(f"⚠ Tushare目录不存在: {tushare_dir}")
        return None
    
    # 查找daily文件
    daily_files = list(tushare_dir.glob(f"daily_{month_prefix}*.parquet"))
    
    if not daily_files:
        print(f"⚠ 未找到{month_name}的Tushare数据")
        return None
    
    all_stocks = set()
    date_stocks = {}
    
    for parquet_file in sorted(daily_files):
        try:
            df = pd.read_parquet(parquet_file)
            date_str = parquet_file.stem.split('_')[1]  # 提取日期
            stocks = df['ts_code'].astype(str).tolist()
            date_stocks[date_str] = set(stocks)
            all_stocks.update(stocks)
        except Exception as e:
            print(f"⚠ 读取失败 {parquet_file.name}: {e}")
    
    print(f"✓ {month_name} Tushare数据:")
    print(f"  文件数: {len(daily_files)}")
    print(f"  交易日: {len(date_stocks)}")
    print(f"  独立股票数: {len(all_stocks)}")
    
    return {
        'all_stocks': all_stocks,
        'date_stocks': date_stocks,
        'files': daily_files
    }

def analyze_overlap(excel_data, tushare_data, month_name="11月"):
    """分析重叠情况"""
    print(f"\n{'='*60}")
    print(f"{month_name} 股票重叠分析")
    print(f"{'='*60}")
    
    if excel_data is None or tushare_data is None:
        print("⚠ 数据缺失，无法分析")
        return
    
    excel_stocks = excel_data['all_stocks']
    tushare_stocks = tushare_data['all_stocks']
    
    # 标准化股票代码（Excel可能缺少.SH/.SZ后缀）
    def normalize_code(code_set):
        """标准化股票代码"""
        normalized = set()
        for code in code_set:
            # 移除后缀
            base_code = code.split('.')[0]
            normalized.add(base_code)
        return normalized
    
    excel_norm = normalize_code(excel_stocks)
    tushare_norm = normalize_code(tushare_stocks)
    
    # 计算重叠
    overlap = excel_norm & tushare_norm
    excel_only = excel_norm - tushare_norm
    tushare_only = tushare_norm - excel_norm
    
    print(f"\n📊 整体重叠情况:")
    print(f"  Excel股票数:     {len(excel_norm):5d}")
    print(f"  Tushare股票数:   {len(tushare_norm):5d}")
    print(f"  重叠股票数:      {len(overlap):5d} ({len(overlap)/len(excel_norm)*100:.1f}% of Excel)")
    print(f"  Excel独有:       {len(excel_only):5d}")
    print(f"  Tushare独有:     {len(tushare_only):5d}")
    
    # 按日期分析
    print(f"\n📅 按日期重叠情况:")
    
    excel_dates = set(excel_data['date_stocks'].keys())
    tushare_dates = set(tushare_data['date_stocks'].keys())
    common_dates = excel_dates & tushare_dates
    
    print(f"  Excel交易日:     {len(excel_dates)}")
    print(f"  Tushare交易日:   {len(tushare_dates)}")
    print(f"  共同交易日:      {len(common_dates)}")
    
    if common_dates:
        daily_overlaps = []
        for date in sorted(common_dates):
            excel_day = normalize_code(excel_data['date_stocks'][date])
            tushare_day = normalize_code(tushare_data['date_stocks'][date])
            overlap_day = excel_day & tushare_day
            
            daily_overlaps.append({
                'date': date,
                'excel_count': len(excel_day),
                'tushare_count': len(tushare_day),
                'overlap': len(overlap_day),
                'overlap_pct': len(overlap_day) / len(excel_day) * 100 if len(excel_day) > 0 else 0
            })
        
        df_daily = pd.DataFrame(daily_overlaps)
        print(f"\n  每日平均重叠率: {df_daily['overlap_pct'].mean():.2f}%")
        print(f"  最低重叠率:      {df_daily['overlap_pct'].min():.2f}% ({df_daily.loc[df_daily['overlap_pct'].idxmin(), 'date']})")
        print(f"  最高重叠率:      {df_daily['overlap_pct'].max():.2f}% ({df_daily.loc[df_daily['overlap_pct'].idxmax(), 'date']})")
    
    # 分析Excel独有股票
    if len(excel_only) > 0:
        print(f"\n🔍 Excel独有股票样本 (前20):")
        for i, code in enumerate(sorted(excel_only)[:20], 1):
            print(f"  {i:2d}. {code}")
    
    # 分析Tushare独有股票
    if len(tushare_only) > 0 and len(tushare_only) < 100:
        print(f"\n🔍 Tushare独有股票样本 (前20):")
        for i, code in enumerate(sorted(tushare_only)[:20], 1):
            print(f"  {i:2d}. {code}")
    
    return {
        'overlap': overlap,
        'excel_only': excel_only,
        'tushare_only': tushare_only,
        'overlap_pct': len(overlap) / len(excel_norm) * 100 if len(excel_norm) > 0 else 0
    }

def main():
    """主流程"""
    print(f"\n{'#'*60}")
    print("# Excel vs Tushare 股票数量重叠分析")
    print(f"{'#'*60}")
    
    # 1. 分析11月数据
    excel_nov = load_excel_stocks(EXCEL_NOV_DIR, "11月")
    tushare_nov = load_tushare_stocks(TUSHARE_DATA_ROOT, "202511", "11月")
    
    if excel_nov and tushare_nov:
        result_nov = analyze_overlap(excel_nov, tushare_nov, "11月")
    
    # 2. 分析12月数据
    excel_dec = load_excel_stocks(EXCEL_DEC_DIR, "12月")
    tushare_dec = load_tushare_stocks(TUSHARE_DATA_ROOT, "202512", "12月")
    
    if excel_dec and tushare_dec:
        result_dec = analyze_overlap(excel_dec, tushare_dec, "12月")
    
    # 3. 总结
    print(f"\n{'#'*60}")
    print("# 总结")
    print(f"{'#'*60}")
    
    if excel_nov and tushare_nov:
        print(f"\n11月重叠率: {result_nov['overlap_pct']:.2f}%")
    
    if excel_dec and tushare_dec:
        print(f"12月重叠率: {result_dec['overlap_pct']:.2f}%")
    
    print(f"\n结论:")
    print(f"  - Excel数据通常包含全市场股票")
    print(f"  - Tushare数据可能排除了ST、退市等特殊股票")
    print(f"  - 重叠股票数占Excel股票数的比例反映数据一致性")

if __name__ == "__main__":
    main()
