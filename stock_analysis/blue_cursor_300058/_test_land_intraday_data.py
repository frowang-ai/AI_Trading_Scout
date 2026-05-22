#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline checks for land_intraday_data.py.

This test does not call Tushare. It validates the segment planner, minute-data
cleaning, and daily intraday feature formulas on synthetic bars.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from land_intraday_data import TS_CODE, build_segments, calculate_intraday_features, clean_minutes


def make_synthetic_day(trade_date: str = "20260511", n_bars: int = 240) -> pd.DataFrame:
    start = pd.Timestamp(f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]} 09:30:00")
    rows = []
    price = 10.0
    for idx in range(n_bars):
        trade_time = start + pd.Timedelta(minutes=idx)
        high = price + (1.0 if idx == 30 else 0.02)
        close = price + 0.01
        if idx == 120:
            close = 10.5
        if idx == 180:
            close = 10.2
        rows.append(
            {
                "ts_code": TS_CODE,
                "trade_time": trade_time,
                "open": price,
                "high": high,
                "low": price - 0.02,
                "close": close,
                "vol": 1000 + idx,
                "amount": (1000 + idx) * close * 100,
            }
        )
        price += 0.001
    return pd.DataFrame(rows)


def test_build_segments() -> None:
    segments = build_segments(dt.date(2026, 1, 1), dt.date(2026, 2, 5), 30)
    assert [seg.key for seg in segments] == [
        "2026-01-01__2026-01-31",
        "2026-02-01__2026-02-05",
    ]


def test_clean_minutes_deduplicates_and_orders() -> None:
    raw = make_synthetic_day(n_bars=5)
    duplicated = pd.concat([raw.iloc[[2]], raw, raw.iloc[[2]]], ignore_index=True)
    cleaned = clean_minutes(duplicated)

    assert len(cleaned) == 5
    assert cleaned["trade_time"].is_monotonic_increasing
    assert cleaned["trade_date"].iloc[0] == "20260511"
    assert cleaned["minute_seq"].tolist() == [0, 1, 2, 3, 4]


def test_calculate_intraday_features() -> None:
    cleaned = clean_minutes(make_synthetic_day())
    features = calculate_intraday_features(cleaned)

    assert len(features) == 1
    row = features.iloc[0]
    assert row["trade_date"] == "20260511"
    assert row["n_bars"] == 240
    assert 0 <= row["peak_frac"] <= 1
    assert row["vol_30m_ratio"] > 0
    assert pd.notna(row["first_5m_ret"])
    assert pd.notna(row["first_15m_ret"])
    assert pd.notna(row["first_15m_vwap_dev"])
    assert pd.notna(row["morning_fade"])
    assert pd.notna(row["pm_reclaim"])


def main() -> None:
    test_build_segments()
    test_clean_minutes_deduplicates_and_orders()
    test_calculate_intraday_features()
    print("OK: land_intraday_data offline tests passed")


if __name__ == "__main__":
    main()
