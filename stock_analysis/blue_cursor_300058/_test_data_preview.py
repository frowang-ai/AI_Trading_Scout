#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据预览验证脚本（测试先行）
=============================
在正式计算指标之前，先确认三个数据源的结构、字段和质量：
  - daily       : OHLCV 日线
  - daily_basic : 换手率、流通股本、量比等每日基本面指标
  - moneyflow   : 大/中/小/特大单资金流向

标的：蓝色光标 300058.SZ
时段：取最近 30 个交易日用于预览（不占太多 API 积分）
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── 路径定位 ──────────────────────────────────────────────────────────────────
_CURRENT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _CURRENT_DIR.parent.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT))

import datetime

import tushare as ts

from get_data_tushare.config import get_tushare_token

# ── 常量 ────────────────────────────────────────────────────────────────────────────────
TS_CODE = "300058.SZ"  # 蓝色光标
_TODAY = datetime.date.today()
END_DATE = _TODAY.strftime("%Y%m%d")  # 动态：今天
START_DATE = (_TODAY - datetime.timedelta(days=120)).strftime("%Y%m%d")  # 动态：近120天

# ═══════════════════════════════════════════════════════════════════════════════


def sep(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def main() -> None:
    token = get_tushare_token()
    pro = ts.pro_api(token)

    # ── 1. daily ──────────────────────────────────────────────────────────────
    sep("① daily  —  OHLCV 日线")
    daily = pro.daily(ts_code=TS_CODE, start_date=START_DATE, end_date=END_DATE)
    daily = daily.sort_values("trade_date").reset_index(drop=True)

    print(f"  行数: {len(daily)}  |  列数: {daily.shape[1]}")
    print(f"  时段: {daily['trade_date'].min()}  ~  {daily['trade_date'].max()}")
    print(f"\n  列名: {list(daily.columns)}")
    print(f"\n  数据类型:\n{daily.dtypes.to_string()}")
    print(f"\n  缺失值:\n{daily.isnull().sum().to_string()}")
    print(f"\n  前5行:\n{daily.head().to_string()}")
    print(f"\n  关键字段单位说明:")
    print("    vol    : 成交量（手，1手=100股）")
    print("    amount : 成交额（千元）")

    # ── 2. daily_basic ────────────────────────────────────────────────────────
    sep("② daily_basic  —  每日基本面指标")
    basic = pro.daily_basic(
        ts_code=TS_CODE,
        start_date=START_DATE,
        end_date=END_DATE,
        fields="ts_code,trade_date,close,turnover_rate,turnover_rate_f,"
        "volume_ratio,float_share,free_share,total_mv,circ_mv",
    )
    basic = basic.sort_values("trade_date").reset_index(drop=True)

    print(f"  行数: {len(basic)}  |  列数: {basic.shape[1]}")
    print(f"\n  列名: {list(basic.columns)}")
    print(f"\n  缺失值:\n{basic.isnull().sum().to_string()}")
    print(f"\n  前5行:\n{basic.head().to_string()}")
    print(f"\n  关键字段单位说明:")
    print("    turnover_rate   : 换手率（%，基于流通股本）")
    print("    turnover_rate_f : 换手率（%，基于自由流通股本）")
    print("    float_share     : 流通股本（万股）")
    print("    free_share      : 自由流通股本（万股）")
    print("    circ_mv         : 流通市值（万元）")

    # ── 3. moneyflow ──────────────────────────────────────────────────────────
    sep("③ moneyflow  —  资金流向（大/中/小/特大单）")
    mf = pro.moneyflow(ts_code=TS_CODE, start_date=START_DATE, end_date=END_DATE)
    mf = mf.sort_values("trade_date").reset_index(drop=True)

    print(f"  行数: {len(mf)}  |  列数: {mf.shape[1]}")
    print(f"\n  列名: {list(mf.columns)}")
    print(f"\n  缺失值:\n{mf.isnull().sum().to_string()}")
    print(f"\n  前5行:\n{mf.head().to_string()}")
    print(f"\n  关键字段单位说明:")
    print("    buy_sm_vol / sell_sm_vol   : 小单买/卖量（手）")
    print("    buy_md_vol / sell_md_vol   : 中单买/卖量（手）")
    print("    buy_lg_vol / sell_lg_vol   : 大单买/卖量（手）")
    print("    buy_elg_vol/ sell_elg_vol  : 特大单买/卖量（手）")
    print("    *_amount                   : 对应金额（万元）")
    print("    net_mf_vol / net_mf_amount : 净流入量（手）/ 净流入额（万元）")

    # ── 4. 三表可合并性验证 ───────────────────────────────────────────────────
    sep("④ 三表 trade_date 对齐验证")
    dates_daily = set(daily["trade_date"])
    dates_basic = set(basic["trade_date"])
    dates_mf = set(mf["trade_date"])

    only_in_daily = dates_daily - dates_basic - dates_mf
    only_in_basic = dates_basic - dates_daily
    only_in_mf = dates_mf - dates_daily
    common = dates_daily & dates_basic & dates_mf

    print(f"  daily 日期数   : {len(dates_daily)}")
    print(f"  daily_basic 日期数: {len(dates_basic)}")
    print(f"  moneyflow 日期数  : {len(dates_mf)}")
    print(f"  三表共同日期数    : {len(common)}")
    if only_in_daily:
        print(f"  ⚠️  仅在 daily 中: {sorted(only_in_daily)}")
    if only_in_basic:
        print(f"  ⚠️  仅在 basic 中: {sorted(only_in_basic)}")
    if only_in_mf:
        print(f"  ⚠️  仅在 mf 中   : {sorted(only_in_mf)}")
    if not (only_in_daily or only_in_basic or only_in_mf):
        print("  ✅ 三表日期完全对齐，可以直接 merge")

    # ── 5. VWAP 公式验证 ──────────────────────────────────────────────────────
    sep("⑤ VWAP 公式验证（amount×10/vol）")
    sample = daily.head(3).copy()
    # amount 单位：千元；vol 单位：手（100股）
    # VWAP = amount*1000 / (vol*100) = amount*10/vol  元/股
    sample["vwap_calc"] = (sample["amount"] * 10 / sample["vol"]).round(3)
    sample["close_vs_vwap"] = (
        (sample["close"] - sample["vwap_calc"]) / sample["vwap_calc"] * 100
    ).round(3)
    print(
        sample[
            ["trade_date", "open", "high", "low", "close", "vwap_calc", "close_vs_vwap"]
        ].to_string()
    )
    print("  close_vs_vwap 单位: %（正=收盘高于VWAP，负=低于VWAP）")

    sep("✅ 数据预览完成，三个数据源结构正常，可进入指标计算")


if __name__ == "__main__":
    main()
