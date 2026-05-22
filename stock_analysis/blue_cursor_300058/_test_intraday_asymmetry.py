#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日内涨跌速度不对称分析
=======================
用 1 分钟 K 线量化用户观察到的"快速拉升 → 缓慢回落"现象。

核心指标：
  peak_time       : 当日最高价出现的时间点（分钟序号）
  peak_frac       : 最高价出现在全天的哪个阶段（0=开盘，1=收盘）
  up_speed_pct_m  : 上涨速度（% / 分钟）= 开盘→最高 的涨幅 / 所用分钟数
  down_speed_pct_m: 下跌速度（% / 分钟）= 最高→收盘 的跌幅 / 所用分钟数
  speed_ratio     : up_speed / down_speed（>1 说明涨得快跌得慢，即"快涨慢跌"）
  morning_capture : 前30分钟内完成了全天高低差的多少比例
  path_corr       : 日内收益率序列的自相关（负值=冲高回落；正值=趋势延续）
"""

from __future__ import annotations

import datetime
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 无 GUI 环境下保存图片
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ── 路径 ──────────────────────────────────────────────────────────────────────
_CURRENT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _CURRENT_DIR.parent.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT))

import tushare as ts

from get_data_tushare.config import get_tushare_token

# ── 常量 ──────────────────────────────────────────────────────────────────────
TS_CODE = "300058.SZ"
# 拉最近 30 个交易日的分钟数据
_TODAY = datetime.date.today()
END_DT = _TODAY.strftime("%Y-%m-%d 20:00:00")
START_DT = (_TODAY - datetime.timedelta(days=45)).strftime("%Y-%m-%d 09:00:00")
FREQ = "1min"
# 分析哪些最近的交易日（取最近 N 个有完整数据的日子）
RECENT_N = 15
OUTPUT_CSV = _CURRENT_DIR / "_test_intraday_asymmetry.csv"
OUTPUT_PNG = _CURRENT_DIR / "_test_intraday_paths.png"
CACHE_PARQUET = _CURRENT_DIR / "_test_mins_cache.parquet"  # 本地缓存，节省每日限额

# A 股分钟数总数（09:30-11:30 + 13:00-15:00 = 240 根）
TOTAL_MINS = 240


# ═══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_mins(pro) -> pd.DataFrame:
    """拉取分钟数据并做基本清洗。优先读本地缓存，节省每日 API 限额。"""

    # ── 检查缓存 ────────────────────────────────────────────────────────────
    if CACHE_PARQUET.exists():
        cached = pd.read_parquet(CACHE_PARQUET)
        cached["trade_time"] = pd.to_datetime(cached["trade_time"])
        cached_end = cached["trade_time"].max().strftime("%Y-%m-%d")
        today_str = _TODAY.strftime("%Y-%m-%d")

        if cached_end >= today_str:
            print(f"  [缓存命中] 读取本地 {CACHE_PARQUET.name}")
            print(f"  → 缓存数据最新至: {cached_end}，跳过 API 调用")
            return _clean_mins(cached)
        else:
            print(f"  [缓存过期] 最新至 {cached_end}，需要补增量 ...")
            # 只拉缓存之后的新数据
            incr_start = (
                cached["trade_time"].max() - datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d 09:00:00")
            new_df = _call_api(pro, incr_start, END_DT)
            if new_df is not None and not new_df.empty:
                combined = pd.concat([cached, new_df], ignore_index=True)
                combined = combined.drop_duplicates(subset=["trade_time"]).sort_values(
                    "trade_time"
                )
                combined.to_parquet(CACHE_PARQUET, index=False)
                print(f"  缓存已更新 → {CACHE_PARQUET.name}")
                return _clean_mins(combined)
            else:
                print("  增量拉取失败，使用旧缓存")
                return _clean_mins(cached)

    # ── 无缓存，全量拉取 ─────────────────────────────────────────────────────
    print(f"  [无缓存] 全量拉取 {TS_CODE} {FREQ} 分钟数据 ...")
    df = _call_api(pro, START_DT, END_DT)
    if df is None or df.empty:
        raise ValueError("未获取到分钟数据，请检查权限或时间范围")
    df.to_parquet(CACHE_PARQUET, index=False)
    print(f"  数据已缓存 → {CACHE_PARQUET.name}")
    return _clean_mins(df)


def _call_api(pro, start: str, end: str) -> pd.DataFrame | None:
    """实际调用 stk_mins API。"""
    print(f"  拉取 {TS_CODE} {FREQ} 分钟数据 ...")
    try:
        df = pro.stk_mins(
            ts_code=TS_CODE,
            freq=FREQ,
            start_date=start,
            end_date=end,
        )
        return df
    except Exception as e:
        print(f"  ⚠️  API 调用失败: {e}")
        return None


def _clean_mins(df: pd.DataFrame) -> pd.DataFrame:
    """整理列、排序、生成 date / minute_seq。"""
    df = df.copy()
    if df is None or df.empty:
        raise ValueError("未获取到分钟数据，请检查权限或时间范围")

    df["trade_time"] = pd.to_datetime(df["trade_time"])
    df = df.sort_values("trade_time").reset_index(drop=True)
    df["date"] = df["trade_time"].dt.date.astype(str).str.replace("-", "")
    df["minute_seq"] = df.groupby("date").cumcount()  # 当天第几根（0-based）
    print(f"  → {len(df)} 根，覆盖日期：{df['date'].nunique()} 天")
    return df


def build_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """对每个交易日，计算日内速度不对称指标。"""
    rows = []
    dates = sorted(df["date"].unique())

    for d in dates:
        day = df[df["date"] == d].copy().reset_index(drop=True)

        # 需要至少 120 根才算完整（否则可能是半天）
        if len(day) < 120:
            continue

        open_p = day.iloc[0]["open"]
        close_p = day.iloc[-1]["close"]
        high_p = day["high"].max()
        low_p = day["low"].min()

        # 最高价出现的位置
        peak_idx = day["high"].idxmax()
        peak_time = day.iloc[peak_idx]["trade_time"]
        peak_min = day.iloc[peak_idx]["minute_seq"]  # 第几分钟（0-based）
        total_min = len(day) - 1  # 全天总分钟数

        # 上涨速度：开盘 → 最高
        up_pct = (high_p - open_p) / open_p * 100  # 涨幅%
        up_mins = max(peak_min, 1)  # 用了几分钟
        up_speed = up_pct / up_mins  # %/分钟

        # 下跌速度：最高 → 收盘
        down_pct = (high_p - close_p) / high_p * 100  # 跌幅%（高→收）
        down_mins = max(total_min - peak_min, 1)
        down_speed = down_pct / down_mins  # %/分钟

        # 速度比：>1 = 涨快跌慢（"快涨慢跌"）；<1 = 涨慢跌快
        speed_ratio = up_speed / down_speed if down_speed > 0 else np.nan

        # 最高价在全天的时间位置（0=开盘 1=收盘）
        peak_frac = peak_min / total_min

        # 前30分钟内的最高价 vs 全天高点
        early = day[day["minute_seq"] <= 30]
        early_high = early["high"].max() if not early.empty else open_p
        morning_capture = (early_high - open_p) / (high_p - open_p + 1e-9)

        # 日内逐分钟收益率（相对开盘价）
        day["ret_from_open"] = (day["close"] - open_p) / open_p * 100
        ret_series = day["ret_from_open"].values

        # 日内路径自相关（lag=1）：负值代表冲高回落
        if len(ret_series) > 10:
            path_corr = pd.Series(ret_series).diff().dropna().autocorr(lag=1)
        else:
            path_corr = np.nan

        # 全天涨跌幅
        day_ret = (close_p - open_p) / open_p * 100  # 日内涨跌（开→收）
        pre_close = day.iloc[0]["open"]  # 用开盘价代替（无隔夜数据）

        rows.append(
            {
                "date": d,
                "open": round(open_p, 3),
                "high": round(high_p, 3),
                "low": round(low_p, 3),
                "close": round(close_p, 3),
                "day_ret_pct": round(day_ret, 3),
                "up_pct": round(up_pct, 3),
                "down_pct": round(down_pct, 3),
                "up_mins": int(up_mins),
                "down_mins": int(down_mins),
                "up_speed": round(up_speed, 5),  # %/分钟
                "down_speed": round(down_speed, 5),  # %/分钟
                "speed_ratio": round(speed_ratio, 3)
                if not np.isnan(speed_ratio)
                else None,
                "peak_time": str(peak_time),
                "peak_frac": round(peak_frac, 3),  # 0=开盘即最高 1=收盘最高
                "morning_capture": round(morning_capture, 3),
                "path_corr": round(path_corr, 3) if not np.isnan(path_corr) else None,
                "n_bars": len(day),
            }
        )

    return pd.DataFrame(rows)


def print_summary(summary: pd.DataFrame) -> None:
    recent = summary.tail(RECENT_N).copy()
    print(f"\n{'=' * 80}")
    print(f"  日内速度不对称分析 — 最近 {len(recent)} 个交易日")
    print("=" * 80)
    cols = [
        "date",
        "day_ret_pct",
        "up_pct",
        "down_pct",
        "up_speed",
        "down_speed",
        "speed_ratio",
        "peak_frac",
        "morning_capture",
        "path_corr",
    ]
    print(recent[cols].to_string(index=False))

    print(f"\n{'=' * 80}")
    print("  指标含义速查")
    print("=" * 80)
    print("  day_ret_pct    : 日内涨跌幅（开→收）%")
    print("  up_pct         : 开盘→最高 的涨幅 %")
    print("  down_pct       : 最高→收盘 的跌幅 %")
    print("  up_speed       : 上涨速度 % / 分钟（越大越急）")
    print("  down_speed     : 下跌速度 % / 分钟（越大越急）")
    print("  speed_ratio    : up_speed / down_speed  ← 核心指标")
    print("                   >1 = 涨得快、跌得慢（'快涨慢跌'）")
    print("                   <1 = 涨得慢、跌得快（'慢涨快跌'）")
    print("  peak_frac      : 最高价出现在全天的比例（0=开盘 0.1=前30分 1=收盘）")
    print("  morning_capture: 前30分钟内完成了全天涨幅的比例（1=全在早盘）")
    print("  path_corr      : 日内逐分钟涨跌自相关（负=冲高回落 正=趋势延续）")

    # 典型"快涨慢跌"日
    fast_up = recent[
        (recent["speed_ratio"].notna())
        & (recent["speed_ratio"] > 1.5)
        & (recent["day_ret_pct"] < 0)
    ]
    print(f"\n{'=' * 80}")
    print("  典型'快涨慢跌'日（speed_ratio > 1.5 且收盘下跌）")
    print("=" * 80)
    if len(fast_up):
        print(fast_up[cols].to_string(index=False))
    else:
        print("  近期无满足条件的日子")


def plot_intraday_paths(df: pd.DataFrame, summary: pd.DataFrame) -> None:
    """绘制最近 N 天的日内价格路径（相对开盘价的累计收益 %）。"""
    dates = summary.tail(RECENT_N)["date"].tolist()

    n_cols = 5
    n_rows = (len(dates) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 3.5), squeeze=False)
    fig.suptitle(
        f"蓝色光标 {TS_CODE} 日内价格路径（相对开盘，%）",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )

    for i, d in enumerate(dates):
        ax = axes[i // n_cols][i % n_cols]
        day = df[df["date"] == d].copy().reset_index(drop=True)
        if day.empty:
            ax.set_visible(False)
            continue

        open_p = day.iloc[0]["open"]
        ret = (day["close"] - open_p) / open_p * 100
        mins = day["minute_seq"].values

        # 颜色：收盘涨则红，收盘跌则绿（A股习惯）
        final_ret = ret.iloc[-1]
        color = "#d62728" if final_ret >= 0 else "#2ca02c"

        ax.plot(mins, ret, color=color, linewidth=1.2)
        ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
        ax.fill_between(mins, ret, 0, where=(ret >= 0), alpha=0.15, color="#d62728")
        ax.fill_between(mins, ret, 0, where=(ret < 0), alpha=0.15, color="#2ca02c")

        # 标注最高点
        peak_idx = day["high"].idxmax()
        peak_min = day.iloc[peak_idx]["minute_seq"]
        peak_ret = (day.iloc[peak_idx]["high"] - open_p) / open_p * 100
        ax.annotate(
            f"↑{peak_ret:.1f}%",
            xy=(peak_min, peak_ret),
            fontsize=7,
            color="#d62728",
            ha="center",
            va="bottom",
        )

        # 获取 summary 行
        row = summary[summary["date"] == d]
        sr = row["speed_ratio"].values[0] if len(row) else ""
        pf = row["peak_frac"].values[0] if len(row) else ""
        sr_str = f"SR={sr:.1f}" if sr else ""
        pf_str = f"PF={pf:.2f}" if pf else ""

        ax.set_title(f"{d[4:6]}/{d[6:]}  {sr_str}  {pf_str}", fontsize=8.5)
        ax.set_xlabel("分钟序号", fontsize=7)
        ax.set_ylabel("相对开盘 %", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.set_xlim(0, TOTAL_MINS)

    # 隐藏多余的格子
    for j in range(len(dates), n_rows * n_cols):
        axes[j // n_cols][j % n_cols].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=130, bbox_inches="tight")
    print(f"\n✅ 路径图已保存: {OUTPUT_PNG}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    print("=" * 70)
    print(f"  蓝色光标 日内涨跌速度不对称分析")
    print(f"  时段: {START_DT[:10]} ~ {END_DT[:10]}   频率: {FREQ}")
    print("=" * 70)

    token = get_tushare_token()
    pro = ts.pro_api(token)

    mins_df = fetch_mins(pro)

    print("\n[计算日内指标] ...")
    summary = build_daily_summary(mins_df)
    print(f"  → 共 {len(summary)} 个完整交易日")

    print_summary(summary)

    summary.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✅ 结果已保存: {OUTPUT_CSV}")

    print("\n[绘制日内路径图] ...")
    plot_intraday_paths(mins_df, summary)


if __name__ == "__main__":
    main()
