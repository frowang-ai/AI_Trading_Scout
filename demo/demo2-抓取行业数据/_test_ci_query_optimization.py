"""
测试中信行业查询优化方案：按指数查询 vs 按股票查询

目的：验证 ci_index_member 接口是否支持按 l1_code/l2_code/l3_code 查询，
      以及对比两种查询方式的效率差异。
"""

from pathlib import Path
import sys
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

from get_data_tushare.client import TushareClient
from get_data_tushare.utils import get_yesterday


def test_ci_query_by_index():
    """测试：能否按中信指数代码查询成员"""
    print("=" * 60)
    print("测试1：中信行业接口按指数查询")
    print("=" * 60)
    
    client = TushareClient()
    date_str = get_yesterday()
    
    # 1. 获取中信指数列表
    print(f"\n1. 获取中信指数日线数据（获取所有指数代码）")
    ci_daily = client.query("ci_daily", trade_date=date_str)
    if ci_daily is None or ci_daily.empty:
        print("❌ 无法获取中信指数列表")
        return False
    
    ci_codes = ci_daily["ts_code"].dropna().unique().tolist()
    print(f"   ✓ 共 {len(ci_codes)} 个中信指数")
    
    # 2. 测试按指数查询成员（尝试不同参数）
    print(f"\n2. 测试按指数代码查询成员（样本：前3个指数）")
    
    test_codes = ci_codes[:3]
    for i, code in enumerate(test_codes, 1):
        print(f"\n   [{i}] 测试指数: {code}")
        
        # 尝试1: 按 index_code 查询
        print(f"       尝试参数: index_code={code}")
        df1 = client.query("ci_index_member", index_code=code)
        if df1 is not None and not df1.empty:
            print(f"       ✓ index_code 可用！返回 {len(df1)} 条成员记录")
            print(f"       示例列：{list(df1.columns[:10])}")
            return True  # 找到可用方法就返回
        else:
            print(f"       ✗ index_code 不可用")
        
        # 尝试2: 按 l3_code 查询
        print(f"       尝试参数: l3_code={code}")
        df2 = client.query("ci_index_member", l3_code=code)
        if df2 is not None and not df2.empty:
            print(f"       ✓ l3_code 可用！返回 {len(df2)} 条成员记录")
            print(f"       示例列：{list(df2.columns[:10])}")
            return True
        else:
            print(f"       ✗ l3_code 不可用")
        
        # 尝试3: 按 l2_code 查询
        print(f"       尝试参数: l2_code={code}")
        df3 = client.query("ci_index_member", l2_code=code)
        if df3 is not None and not df3.empty:
            print(f"       ✓ l2_code 可用！返回 {len(df3)} 条成员记录")
            return True
        else:
            print(f"       ✗ l2_code 不可用")
        
        # 尝试4: 按 l1_code 查询
        print(f"       尝试参数: l1_code={code}")
        df4 = client.query("ci_index_member", l1_code=code)
        if df4 is not None and not df4.empty:
            print(f"       ✓ l1_code 可用！返回 {len(df4)} 条成员记录")
            return True
        else:
            print(f"       ✗ l1_code 不可用")
    
    print("\n   ❌ 所有参数均不可用，中信接口可能不支持按指数查询")
    return False


def test_ci_query_by_stock():
    """测试：按股票查询的方式（当前实现）"""
    print("\n" + "=" * 60)
    print("测试2：中信行业接口按股票查询（当前方式）")
    print("=" * 60)
    
    client = TushareClient()
    date_str = get_yesterday()
    
    # 获取股票列表（只测试前10只）
    print(f"\n获取股票列表...")
    stock_basic = client.query(
        "stock_basic", 
        exchange="", 
        list_status="L", 
        fields="ts_code,symbol,name"
    )
    
    if stock_basic is None or stock_basic.empty:
        print("❌ 无法获取股票列表")
        return False
    
    test_stocks = stock_basic["ts_code"].tolist()[:10]
    print(f"✓ 测试样本：前 {len(test_stocks)} 只股票")
    
    # 测试按股票查询
    success_count = 0
    start_time = time.time()
    
    for i, ts_code in enumerate(test_stocks, 1):
        df = client.query("ci_index_member", ts_code=ts_code)
        if df is not None and not df.empty:
            # 日期过滤
            df = df.copy()
            for c in ["in_date", "out_date"]:
                if c in df.columns:
                    df[c] = df[c].fillna("")
            in_ok = (df["in_date"] == "") | (df["in_date"] <= date_str)
            out_ok = (df["out_date"] == "") | (df["out_date"] >= date_str)
            df = df[in_ok & out_ok]
            
            if not df.empty:
                success_count += 1
                if i == 1:  # 只打印第一个样本
                    print(f"\n   样本 [{ts_code}] 返回字段：{list(df.columns)}")
                    print(f"   样本数据：\n{df.head(1)}")
    
    elapsed = time.time() - start_time
    
    print(f"\n✓ 成功查询 {success_count}/{len(test_stocks)} 只股票的中信行业")
    print(f"✓ 耗时：{elapsed:.2f} 秒（10 只股票）")
    print(f"✓ 推算全市场 5460 只股票耗时：{elapsed * 5460 / 10 / 60:.1f} 分钟")
    
    return True


def test_alternative_ci_source():
    """测试：查找替代数据源"""
    print("\n" + "=" * 60)
    print("测试3：查找中信行业的替代数据源")
    print("=" * 60)
    
    client = TushareClient()
    date_str = get_yesterday()
    
    # 方案1: 从 bak_basic 获取（历史基本面数据）
    print(f"\n方案1：从 bak_basic 获取中信行业信息")
    try:
        bak_basic = client.query("bak_basic", trade_date=date_str)
        if bak_basic is not None and not bak_basic.empty:
            print(f"   ✓ bak_basic 返回 {len(bak_basic)} 条记录")
            print(f"   ✓ 字段：{list(bak_basic.columns)}")
            
            # 检查是否有行业字段
            industry_cols = [c for c in bak_basic.columns if "industry" in c.lower() or "ci_" in c.lower()]
            if industry_cols:
                print(f"   ✓ 发现行业相关字段：{industry_cols}")
                print(f"\n   样本数据：")
                print(bak_basic[["ts_code", "name"] + industry_cols].head(3))
            else:
                print(f"   ✗ 未发现行业字段")
    except Exception as e:
        print(f"   ✗ bak_basic 查询失败：{e}")
    
    # 方案2: 从 stk_factor 获取
    print(f"\n方案2：从 stk_factor 获取行业信息")
    try:
        # 只查询一只股票测试
        test_stock = "000001.SZ"
        stk_factor = client.query("stk_factor", ts_code=test_stock, trade_date=date_str)
        if stk_factor is not None and not stk_factor.empty:
            print(f"   ✓ stk_factor 可用，字段：{list(stk_factor.columns)}")
        else:
            print(f"   ✗ stk_factor 无数据或不支持此查询")
    except Exception as e:
        print(f"   ✗ stk_factor 查询失败：{e}")
    
    # 方案3: 从 index_classify 获取中信指数分类
    print(f"\n方案3：从 index_classify 获取中信指数分类")
    try:
        ci_classify = client.query("index_classify", src="CI")
        if ci_classify is not None and not ci_classify.empty:
            print(f"   ✓ 中信指数分类可用，共 {len(ci_classify)} 个指数")
            print(f"   ✓ 字段：{list(ci_classify.columns)}")
            print(f"\n   样本数据：")
            print(ci_classify.head(5))
            return ci_classify
        else:
            print(f"   ✗ 中信指数分类为空")
    except Exception as e:
        print(f"   ✗ index_classify(CI) 查询失败：{e}")
    
    return None


def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("中信行业查询优化方案测试")
    print("=" * 80)
    
    try:
        # 测试1：能否按指数查询
        can_query_by_index = test_ci_query_by_index()
        
        # 测试2：按股票查询的效率（当前方式）
        test_ci_query_by_stock()
        
        # 测试3：查找替代数据源
        ci_classify = test_alternative_ci_source()
        
        # 总结
        print("\n" + "=" * 80)
        print("测试结论")
        print("=" * 80)
        
        if can_query_by_index:
            print("✅ 方案可行：中信接口支持按指数查询")
            print("   → 建议：改为按指数查询（类似申万实现）")
            print("   → 预期：API 调用从 5460 次降至 ~50 次（减少 99%）")
        else:
            print("❌ 中信接口不支持按指数查询")
            if ci_classify is not None:
                print("✅ 备用方案：使用 index_classify(CI) + ci_index_member 组合查询")
                print(f"   → 可按 {len(ci_classify)} 个中信指数逐一查询成员")
            else:
                print("⚠️  警告：需要保持当前按股票查询的方式（低效但可用）")
                print("   → 建议：考虑缓存策略，避免每次重复查询")
        
    except Exception as e:
        print(f"\n❌ 测试过程出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
