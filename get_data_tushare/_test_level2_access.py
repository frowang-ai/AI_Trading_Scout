#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Level 2 / 高频数据权限探测脚本
================================
测试当前 Tushare Token 是否具备以下数据权限：

  Level 2 相关接口：
    - stk_mins   历史分钟行情（1/5/15/30/60min）  需单独开权限
    - rt_k       A股实时日线                       需权限
    - rt_min     A股实时分钟                       需权限
    - realtime_quote  实时盘口TICK（爬虫版）       0积分免费

  基础接口（用于验证 Token 本身连通性）：
    - daily      日线行情                          普通权限

用法：
    直接运行此文件即可，无需额外参数。
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Optional

# ── 路径定位（遵循工程规范：基于 __file__）──────────────────────────────────
_CURRENT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _CURRENT_DIR.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT))

# ── 加载 Token ─────────────────────────────────────────────────────────────
from get_data_tushare.config import get_tushare_token  # noqa: E402

try:
    import tushare as ts
except ImportError:
    print("[ERROR] tushare 未安装，请运行: pip install tushare")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════════


def _tag(ok: bool) -> str:
    return "✅ 有权限" if ok else "❌ 无权限/被拦截"


def _probe(name: str, fn, *args, **kwargs) -> tuple[bool, Optional[str]]:
    """
    探测一个接口是否可用。
    返回 (success: bool, error_msg: str | None)
    """
    try:
        df = fn(*args, **kwargs)
        # 空 DataFrame 不代表失败，只要不抛异常就认为有权限
        row_info = (
            f"返回 {len(df)} 行"
            if df is not None and hasattr(df, "__len__")
            else "调用成功"
        )
        return True, row_info
    except Exception as e:
        msg = str(e)
        return False, msg


# ═══════════════════════════════════════════════════════════════════════════════
# 主测试逻辑
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    print("=" * 65)
    print("  Tushare Level 2 / 高频数据权限探测")
    print("=" * 65)

    # ── 初始化 ──────────────────────────────────────────────────────────────
    try:
        token = get_tushare_token()
        print(f"\n[Token] {token[:8]}...{token[-4:]}  (已加载)\n")
    except ValueError as e:
        print(f"\n[FATAL] {e}")
        sys.exit(1)

    pro = ts.pro_api(token)

    results: list[dict] = []

    # ─────────────────────────────────────────────────────────────────────────
    # 0. 基础连通性：daily（普通权限，应该必过）
    # ─────────────────────────────────────────────────────────────────────────
    print("── [0] 基础连通性测试（daily 日线，普通权限）─────────────────────")
    ok, info = _probe(
        "daily",
        pro.daily,
        ts_code="000001.SZ",
        start_date="20250101",
        end_date="20250110",
    )
    print(f"    daily          : {_tag(ok)}  |  {info}")
    results.append(
        {
            "接口": "daily",
            "说明": "A股日线（基准测试）",
            "所需积分": "普通",
            "结果": ok,
            "详情": info,
        }
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 1. 历史分钟行情：stk_mins（Level 2 核心，需单独开权限）
    # ─────────────────────────────────────────────────────────────────────────
    print("\n── [1] 历史分钟行情（stk_mins，需单独权限）──────────────────────")
    ok, info = _probe(
        "stk_mins",
        pro.stk_mins,
        ts_code="000001.SZ",
        freq="1min",
        start_date="2025-01-06 09:00:00",
        end_date="2025-01-06 10:00:00",
    )
    print(f"    stk_mins       : {_tag(ok)}  |  {info}")
    results.append(
        {
            "接口": "stk_mins",
            "说明": "历史分钟行情（Level 2核心）",
            "所需积分": "单独开权",
            "结果": ok,
            "详情": info,
        }
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 2. 实时日线：rt_k（需权限；非交易时间返回空或上次数据）
    # ─────────────────────────────────────────────────────────────────────────
    print("\n── [2] 实时日线（rt_k，需权限）─────────────────────────────────")
    ok, info = _probe(
        "rt_k",
        pro.rt_k,
        ts_code="000001.SZ",
    )
    print(f"    rt_k           : {_tag(ok)}  |  {info}")
    results.append(
        {
            "接口": "rt_k",
            "说明": "A股实时日线",
            "所需积分": "需权限",
            "结果": ok,
            "详情": info,
        }
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 3. 实时分钟：rt_min（需权限）
    # ─────────────────────────────────────────────────────────────────────────
    print("\n── [3] 实时分钟（rt_min，需权限）───────────────────────────────")
    ok, info = _probe(
        "rt_min",
        pro.rt_min,
        ts_code="000001.SZ",
        freq="1MIN",
    )
    print(f"    rt_min         : {_tag(ok)}  |  {info}")
    results.append(
        {
            "接口": "rt_min",
            "说明": "A股实时分钟",
            "所需积分": "需权限",
            "结果": ok,
            "详情": info,
        }
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 4. 爬虫版实时盘口 TICK：realtime_quote（0积分免费，但需账号）
    # ─────────────────────────────────────────────────────────────────────────
    print("\n── [4] 实时盘口 TICK 爬虫版（realtime_quote，0积分免费）────────")
    try:
        df = ts.get_realtime_quotes("000001")  # tushare 旧版接口
        ok = df is not None and len(df) > 0
        info = f"返回 {len(df)} 行" if ok else "返回空"
    except Exception as e:
        ok = False
        info = str(e)
    print(f"    realtime_quote : {_tag(ok)}  |  {info}")
    results.append(
        {
            "接口": "realtime_quote",
            "说明": "实时盘口TICK（爬虫，0积分）",
            "所需积分": "0积分",
            "结果": ok,
            "详情": info,
        }
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 5. 逐笔成交 realtime_tick（爬虫版，0积分）
    # ─────────────────────────────────────────────────────────────────────────
    print("\n── [5] 逐笔成交爬虫版（realtime_tick，0积分）───────────────────")
    try:
        df = ts.get_today_ticks("000001")
        ok = df is not None and len(df) > 0
        info = f"返回 {len(df)} 行" if ok else "返回空（非交易时段属正常）"
    except Exception as e:
        ok = False
        info = str(e)
    print(f"    realtime_tick  : {_tag(ok)}  |  {info}")
    results.append(
        {
            "接口": "realtime_tick",
            "说明": "逐笔成交（爬虫，0积分）",
            "所需积分": "0积分",
            "结果": ok,
            "详情": info,
        }
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 汇总
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  汇总结果")
    print("=" * 65)
    print(f"  {'接口':<18} {'说明':<24} {'所需积分':<10} {'结果'}")
    print("  " + "-" * 61)
    for r in results:
        tag = "✅" if r["结果"] else "❌"
        print(f"  {r['接口']:<18} {r['说明']:<24} {r['所需积分']:<10} {tag}")

    level2_ok = [
        r for r in results if r["结果"] and r["接口"] in ("stk_mins", "rt_k", "rt_min")
    ]
    print()
    if level2_ok:
        print(f"  🎉 Level 2 有权限的接口: {[r['接口'] for r in level2_ok]}")
    else:
        print(
            "  ⚠️  当前 Token 暂无 Level 2 数据权限（stk_mins / rt_k / rt_min 均被拦截）"
        )
        print("     如需开通，请前往 https://tushare.pro/user/points 查看积分/权限说明")

    print("=" * 65)


if __name__ == "__main__":
    main()
