#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蓝色光标（300058）量价指标计算
================================
对应策略文档的七层量化分析框架：

  Layer 1  成交量异常程度   RVOL / vol_zscore / vol_shock
  Layer 2  主动买卖压力     主力净流入 / OFI（订单流不平衡）
  Layer 3  价格冲击         price_impact
  Layer 4  量价组合变量     开盘收益 / 日内收益 / 振幅 / 收盘位置
  Layer 5  VWAP             日 VWAP 及收盘价偏离
  Layer 6  流动性           换手率 / 已实现波动率
  Layer 7  综合信号         high_open_low_close（高开低走）/ failed_breakout 标签

数据来源：
  - pro.daily        : OHLCV 日线
  - pro.daily_basic  : 换手率、流通股本、量比
  - pro.moneyflow    : 大/中/小/特大单资金流向

输出：
  - _test_indicators_result.csv  : 完整指标表（{当前目录}/）
"""

from __future__ import annotations

import datetime
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ── 路径定位（遵循工程规范：基于 __file__）──────────────────────────────────
_CURRENT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _CURRENT_DIR.parent.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT))

import tushare as ts

from get_data_tushare.config import get_tushare_token

# ═══════════════════════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════════════════════

TS_CODE = "300058.SZ"  # 蓝色光标
_TODAY = datetime.date.today()
END_DATE = _TODAY.strftime("%Y%m%d")  # 动态：今天
START_DATE = (_TODAY - datetime.timedelta(days=365 * 3)).strftime(
    "%Y%m%d"
)  # 动态：近3年
ROLL_WIN = 20  # 滚动窗口（交易日）
OUTPUT_FILE = _CURRENT_DIR / "_test_indicators_result.csv"


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1: 数据获取
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_all(pro) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """拉取三个数据源，排序并返回。"""

    print("[1/3] 拉取 daily ...")
    daily = pro.daily(ts_code=TS_CODE, start_date=START_DATE, end_date=END_DATE)
    daily = daily.sort_values("trade_date").reset_index(drop=True)
    time.sleep(0.4)

    print("[2/3] 拉取 daily_basic ...")
    basic = pro.daily_basic(
        ts_code=TS_CODE,
        start_date=START_DATE,
        end_date=END_DATE,
        fields=(
            "ts_code,trade_date,turnover_rate,turnover_rate_f,"
            "volume_ratio,float_share,free_share,circ_mv"
        ),
    )
    basic = basic.sort_values("trade_date").reset_index(drop=True)
    time.sleep(0.4)

    print("[3/3] 拉取 moneyflow ...")
    mf = pro.moneyflow(ts_code=TS_CODE, start_date=START_DATE, end_date=END_DATE)
    mf = mf.sort_values("trade_date").reset_index(drop=True)

    print(f"  → daily: {len(daily)}行  basic: {len(basic)}行  moneyflow: {len(mf)}行")
    return daily, basic, mf


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2: 合并三表
# ═══════════════════════════════════════════════════════════════════════════════


def merge_tables(
    daily: pd.DataFrame,
    basic: pd.DataFrame,
    mf: pd.DataFrame,
) -> pd.DataFrame:
    """以 trade_date 为主键 inner join 三张表。"""

    # daily_basic 去掉重复字段（ts_code 已在 daily 里）
    basic_cols = [c for c in basic.columns if c not in ("ts_code",)]
    df = daily.merge(basic[basic_cols], on="trade_date", how="inner")

    # moneyflow 去掉重复字段
    mf_cols = [c for c in mf.columns if c not in ("ts_code",)]
    df = df.merge(mf[mf_cols], on="trade_date", how="inner")

    df = df.sort_values("trade_date").reset_index(drop=True)
    print(f"  → 合并后: {len(df)} 行 × {df.shape[1]} 列")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3: 计算指标（七层）
# ═══════════════════════════════════════════════════════════════════════════════


def calc_indicators(df: pd.DataFrame, roll: int = ROLL_WIN) -> pd.DataFrame:
    d = df.copy()

    # ── 单位换算 ──────────────────────────────────────────────────────────────
    # vol     : 手 → 手（保持，统一使用手）
    # amount  : 千元 → 万元（÷10，方便和 moneyflow 对齐）
    d["amount_wan"] = d["amount"] / 10  # 万元
    d["amount_yi"] = d["amount"] / 10_000  # 亿元（用于价格冲击）

    # ── 前收盘（昨收）──────────────────────────────────────────────────────────
    # daily 里已有 pre_close 字段，直接使用
    # pre_close = d["close"].shift(1)  # 备用

    # ══════════════════════════════════════════════════════════════════════════
    # Layer 5: VWAP（先算，Layer 4 需要用）
    # VWAP = amount(千元) × 1000 / (vol(手) × 100) = amount × 10 / vol
    # ══════════════════════════════════════════════════════════════════════════
    d["vwap"] = (d["amount"] * 10 / d["vol"]).round(4)  # 元/股
    d["close_vs_vwap_pct"] = ((d["close"] - d["vwap"]) / d["vwap"] * 100).round(
        4
    )  # %，正=收盘高于VWAP

    # ══════════════════════════════════════════════════════════════════════════
    # Layer 1: 成交量异常程度
    # ══════════════════════════════════════════════════════════════════════════

    vol_roll_mean = d["vol"].rolling(roll, min_periods=5).mean()
    vol_roll_std = d["vol"].rolling(roll, min_periods=5).std()

    # 相对成交量：今日 / 20日均量
    d["rvol_20"] = (d["vol"] / vol_roll_mean).round(4)

    # 成交量冲击：log(今日) - log(20日均量)
    d["vol_shock"] = (np.log(d["vol"]) - np.log(vol_roll_mean)).round(4)

    # 成交量 z-score：(今日 - 均值) / 标准差
    d["vol_zscore"] = ((d["vol"] - vol_roll_mean) / vol_roll_std).round(4)

    # 量比（直接来自 daily_basic）：volume_ratio = 今日均速 / 过去5日均速
    # 已在 d 中，字段名 volume_ratio

    # ══════════════════════════════════════════════════════════════════════════
    # Layer 2: 主动买卖压力（来自 moneyflow）
    # ══════════════════════════════════════════════════════════════════════════

    # 主力 = 大单 + 特大单
    d["main_buy_amount"] = d["buy_lg_amount"] + d["buy_elg_amount"]  # 万元
    d["main_sell_amount"] = d["sell_lg_amount"] + d["sell_elg_amount"]  # 万元
    d["main_net_amount"] = (
        d["main_buy_amount"] - d["main_sell_amount"]
    )  # 万元，正=净买入

    d["main_buy_vol"] = d["buy_lg_vol"] + d["buy_elg_vol"]  # 手
    d["main_sell_vol"] = d["sell_lg_vol"] + d["sell_elg_vol"]  # 手
    d["main_net_vol"] = d["main_buy_vol"] - d["main_sell_vol"]  # 手

    # 散户（小单）
    d["retail_net_amount"] = d["buy_sm_amount"] - d["sell_sm_amount"]  # 万元

    # 订单流不平衡 OFI（标准化到总成交额，方便跨期比较）
    # OFI = 主力净流入(万元) / 总成交额(万元)，范围 [-1, +1]
    d["ofi"] = (d["main_net_amount"] / d["amount_wan"]).round(4)

    # 主力占比：主力成交(买+卖) / 总成交，衡量主力参与度
    d["main_participation"] = (
        (d["main_buy_amount"] + d["main_sell_amount"]) / d["amount_wan"]
    ).round(4)

    # ══════════════════════════════════════════════════════════════════════════
    # Layer 3: 价格冲击
    # price_impact = |日收益率%| / 成交额(亿元)
    # 越小说明单位资金推动价格越难（市场深度越好）
    # 越大说明一点钱就能推很高（流动性差 or 买盘急）
    # ══════════════════════════════════════════════════════════════════════════

    d["ret_pct"] = d["pct_chg"].round(4)  # %
    d["price_impact"] = (d["pct_chg"].abs() / d["amount_yi"]).round(6)  # %/亿元

    # 20日滚动均值，方便判断今日是否异常
    d["price_impact_20ma"] = (
        d["price_impact"].rolling(roll, min_periods=5).mean().round(6)
    )

    # ══════════════════════════════════════════════════════════════════════════
    # Layer 4: 量价组合变量
    # ══════════════════════════════════════════════════════════════════════════

    # 开盘收益率：相对昨收的跳空幅度
    d["open_ret_pct"] = ((d["open"] / d["pre_close"] - 1) * 100).round(4)  # %

    # 日内收益率：从开盘到收盘
    d["intraday_ret_pct"] = ((d["close"] / d["open"] - 1) * 100).round(4)  # %

    # 振幅：(最高 - 最低) / 昨收
    d["amplitude_pct"] = ((d["high"] - d["low"]) / d["pre_close"] * 100).round(4)  # %

    # 收盘位置：0=收最低，1=收最高（判断多空强弱）
    hl_range = d["high"] - d["low"]
    d["close_position"] = np.where(
        hl_range > 0,
        ((d["close"] - d["low"]) / hl_range).round(4),
        0.5,  # 极少数高低相等时（停牌等），设为中性
    )

    # 成交量 × 日内收益（量价交互项）
    d["vol_x_intraday"] = (d["vol_shock"] * d["intraday_ret_pct"]).round(4)

    # ══════════════════════════════════════════════════════════════════════════
    # Layer 6: 流动性
    # ══════════════════════════════════════════════════════════════════════════

    # 换手率已在 daily_basic 中：turnover_rate / turnover_rate_f

    # 已实现波动率（20日日收益率标准差，年化）
    d["realized_vol_20d"] = (
        d["pct_chg"].rolling(roll, min_periods=5).std() * np.sqrt(252)
    ).round(4)  # %，年化

    # 成交额 20日均值（亿元），衡量流动性水平
    d["amount_yi_20ma"] = d["amount_yi"].rolling(roll, min_periods=5).mean().round(4)

    # ══════════════════════════════════════════════════════════════════════════
    # Layer 7: 综合信号标签（布尔，用于筛选典型形态）
    # ══════════════════════════════════════════════════════════════════════════

    # 异常放量：rvol > 2（成交量超过20日均量的2倍）
    d["sig_high_vol"] = d["rvol_20"] > 2.0

    # 高开低走放量：高开 + 日内下跌 + 收盘低于VWAP + 放量
    d["sig_high_open_low_close"] = (
        (d["open_ret_pct"] > 1.0)  # 高开超过1%
        & (d["intraday_ret_pct"] < -1.0)  # 日内跌超1%
        & (d["close_vs_vwap_pct"] < 0)  # 收盘低于VWAP
        & (d["rvol_20"] > 1.5)  # 放量（超过均量1.5倍）
    )

    # 缩量健康回调：跌幅小 + 缩量 + 收盘位置偏高
    d["sig_healthy_pullback"] = (
        (d["ret_pct"] < 0)  # 下跌
        & (d["ret_pct"] > -2.0)  # 跌幅不超过2%
        & (d["rvol_20"] < 0.8)  # 缩量（不足均量80%）
        & (d["close_position"] > 0.4)  # 收盘位置偏高
    )

    # 放量上涨且收于VWAP上方（偏强）
    d["sig_strong_up"] = (
        (d["ret_pct"] > 0)
        & (d["rvol_20"] > 1.5)
        & (d["close_vs_vwap_pct"] > 0)
        & (d["close_position"] > 0.6)
    )

    # 主力净流出（卖压）
    d["sig_main_outflow"] = d["main_net_amount"] < 0

    return d


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4: 输出与打印摘要
# ═══════════════════════════════════════════════════════════════════════════════

# 最终输出字段（有序）
OUTPUT_COLS = [
    # 基础行情
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "vol",
    "amount_wan",
    "amount_yi",
    # Layer 5: VWAP
    "vwap",
    "close_vs_vwap_pct",
    # Layer 1: 成交量异常
    "rvol_20",
    "vol_shock",
    "vol_zscore",
    "volume_ratio",
    # Layer 2: 主动买卖
    "main_buy_amount",
    "main_sell_amount",
    "main_net_amount",
    "main_net_vol",
    "retail_net_amount",
    "ofi",
    "main_participation",
    "net_mf_amount",  # tushare 原始净流入（含所有大小单）
    # Layer 3: 价格冲击
    "ret_pct",
    "price_impact",
    "price_impact_20ma",
    # Layer 4: 量价组合
    "open_ret_pct",
    "intraday_ret_pct",
    "amplitude_pct",
    "close_position",
    "vol_x_intraday",
    # Layer 6: 流动性
    "turnover_rate",
    "turnover_rate_f",
    "realized_vol_20d",
    "amount_yi_20ma",
    # Layer 7: 综合信号
    "sig_high_vol",
    "sig_high_open_low_close",
    "sig_healthy_pullback",
    "sig_strong_up",
    "sig_main_outflow",
]


def print_summary(d: pd.DataFrame) -> None:
    """打印最近20行 + 各信号触发统计。"""
    print(f"\n{'=' * 70}")
    print("  指标计算完成 — 最近10日概览")
    print("=" * 70)

    cols_preview = [
        "trade_date",
        "close",
        "ret_pct",
        "rvol_20",
        "vol_zscore",
        "ofi",
        "close_vs_vwap_pct",
        "open_ret_pct",
        "intraday_ret_pct",
        "close_position",
        "turnover_rate",
    ]
    print(d[cols_preview].tail(10).to_string(index=False))

    print(f"\n{'=' * 70}")
    print("  Layer 7 信号触发统计（全历史）")
    print("=" * 70)
    sig_cols = [c for c in OUTPUT_COLS if c.startswith("sig_")]
    total = len(d)
    for col in sig_cols:
        cnt = d[col].sum()
        label_map = {
            "sig_high_vol": "异常放量（rvol>2）",
            "sig_high_open_low_close": "高开低走放量",
            "sig_healthy_pullback": "缩量健康回调",
            "sig_strong_up": "放量强势上涨",
            "sig_main_outflow": "主力净流出日",
        }
        print(
            f"  {label_map.get(col, col):<18}: {cnt:>4}次 / {total}日  ({cnt / total * 100:.1f}%)"
        )

    print(f"\n{'=' * 70}")
    print("  高开低走放量 —— 具体发生日期")
    print("=" * 70)
    events = d[d["sig_high_open_low_close"]][
        [
            "trade_date",
            "open_ret_pct",
            "intraday_ret_pct",
            "rvol_20",
            "close_vs_vwap_pct",
            "main_net_amount",
        ]
    ]
    if len(events):
        print(events.to_string(index=False))
    else:
        print("  无触发")


def save_output(d: pd.DataFrame) -> None:
    out = d[[c for c in OUTPUT_COLS if c in d.columns]].copy()
    out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n✅ 已保存至: {OUTPUT_FILE}")
    print(f"   行数: {len(out)}  |  列数: {out.shape[1]}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    print("=" * 70)
    print(f"  蓝色光标（{TS_CODE}）七层量价指标计算")
    print(f"  时段: {START_DATE} ~ {END_DATE}   滚动窗口: {ROLL_WIN}日")
    print("=" * 70)

    token = get_tushare_token()
    pro = ts.pro_api(token)

    print("\n[获取数据]")
    daily, basic, mf = fetch_all(pro)

    print("\n[合并三表]")
    df = merge_tables(daily, basic, mf)

    print("\n[计算指标]")
    result = calc_indicators(df)

    print_summary(result)
    save_output(result)


if __name__ == "__main__":
    main()
