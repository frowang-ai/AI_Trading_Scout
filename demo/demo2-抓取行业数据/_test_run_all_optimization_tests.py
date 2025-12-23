"""
综合测试：完整验证优化方案的可行性

包括：
1. 中信行业查询方式验证
2. 快照复用性能测试
3. 完整优化方案模拟
"""

from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 100)
    print("行业概念数据获取优化方案 - 综合测试")
    print("=" * 100)
    
    # 测试1：中信行业查询优化
    print("\n\n" + "█" * 100)
    print("█" + " " * 98 + "█")
    print("█" + " " * 30 + "测试模块 1: 中信行业查询优化" + " " * 36 + "█")
    print("█" + " " * 98 + "█")
    print("█" * 100)
    
    try:
        from ._test_ci_query_optimization import main as test_ci_main
        test_ci_main()
    except Exception as e:
        print(f"❌ 测试1失败：{e}")
        import traceback
        traceback.print_exc()
    
    # 测试2：快照复用方案
    print("\n\n" + "█" * 100)
    print("█" + " " * 98 + "█")
    print("█" + " " * 32 + "测试模块 2: 快照复用方案" + " " * 38 + "█")
    print("█" + " " * 98 + "█")
    print("█" * 100)
    
    try:
        from ._test_snapshot_reuse import main as test_snapshot_main
        test_snapshot_main()
    except Exception as e:
        print(f"❌ 测试2失败：{e}")
        import traceback
        traceback.print_exc()
    
    # 最终总结
    print("\n\n" + "=" * 100)
    print("最终建议")
    print("=" * 100)
    
    print("""
📋 优化方案分阶段实施建议：

【第一阶段：紧急修复】（预计提升 80% 性能）
  ✓ 修复中信行业查询逻辑（按指数查询替代按股票查询）
  ✓ 如不支持按指数查询，则添加缓存机制
  → 目标：将 --extras-all 耗时从 20 分钟降至 4-5 分钟

【第二阶段：架构优化】（预计提升 95% 性能）
  ✓ 实现快照复用机制
  ✓ 将 industry_concept_panel 改为从快照构建
  ✓ industry_raw 作为数据中间层，每日更新一次
  → 目标：panel 构建耗时降至 10 秒以内

【第三阶段：增量优化】（长期优化）
  ✓ 实现增量更新（只更新变化部分）
  ✓ 添加数据版本管理
  ✓ 支持历史回溯查询
  → 目标：支持大规模历史数据回补

📊 预期性能对比：

  当前方案：
    - API 调用：6200+ 次
    - 耗时：20-25 分钟
    - 问题：大量冗余查询，依赖 API 稳定性

  优化后（第一阶段）：
    - API 调用：~800 次
    - 耗时：3-5 分钟
    - 改进：87% API 调用减少

  优化后（第二阶段）：
    - API 调用：~800 次（仅 raw 层）+ 0 次（panel 层）
    - 耗时：3-5 分钟（raw）+ <10 秒（panel）
    - 改进：解耦数据获取与处理，支持离线构建

🎯 推荐执行顺序：
  1. 运行本测试套件，确认技术可行性 ✓
  2. 根据测试结果，决定采用方案1还是方案1+方案2
  3. 实施第一阶段优化（紧急修复）
  4. 观察效果，再决定是否进行第二阶段

⚠️ 风险提示：
  - 需要验证 ci_index_member 接口的查询能力
  - 快照方案需要额外存储空间（每日约 50-100MB）
  - 需要处理数据同步时序问题（先 raw 后 panel）
""")


if __name__ == "__main__":
    run_all_tests()
