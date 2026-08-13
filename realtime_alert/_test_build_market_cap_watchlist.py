#!/usr/bin/env python3
"""Offline tests for the top-market-cap realtime watchlist builder."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

from realtime_alert.build_market_cap_watchlist import (
    BLUE_CURSOR,
    build_watchlist,
    discover_latest_snapshot,
    write_watchlist_outputs,
)
from realtime_alert.collector import load_symbols


CURRENT_DIR = Path(__file__).parent.resolve()


def test_selects_top_n_sh_sz_and_forces_blue_cursor() -> None:
    rows = [
        {
            "ts_code": f"{600000 + index:06d}.SH",
            "trade_date": "20260812",
            "total_mv": 1000 - index,
            "name": f"stock-{index}",
            "list_date": "20200101",
        }
        for index in range(105)
    ]
    rows.extend(
        [
            {"ts_code": "000001.SZ", "trade_date": "20260812", "total_mv": 2000, "name": "平安银行", "list_date": "19910403"},
            {"ts_code": BLUE_CURSOR, "trade_date": "20260812", "total_mv": 1, "name": "蓝色光标", "list_date": "20100226"},
            {"ts_code": "920001.BJ", "trade_date": "20260812", "total_mv": 9999, "name": "bj", "list_date": "20200101"},
            {"ts_code": "900901.SH", "trade_date": "20260812", "total_mv": 9998, "name": "b-share", "list_date": "20200101"},
            {"ts_code": "200001.SZ", "trade_date": "20260812", "total_mv": 9997, "name": "b-share", "list_date": "20200101"},
            {"ts_code": "688825.SH", "trade_date": "20260812", "total_mv": 9996, "name": "长鑫科技", "list_date": "20260727"},
        ]
    )
    selected = build_watchlist(pd.DataFrame(rows), top_n=99)
    assert len(selected) == 100
    assert selected.iloc[0]["ts_code"] == "000001.SZ"
    assert selected.iloc[-1]["ts_code"] == BLUE_CURSOR
    assert selected.iloc[-1]["selection_type"] == "forced_blue_cursor"
    assert not selected["ts_code"].str.endswith(".BJ").any()
    assert "900901.SH" not in set(selected["ts_code"])
    assert "200001.SZ" not in set(selected["ts_code"])
    assert "688825.SH" not in set(selected["ts_code"])
    assert int(selected.iloc[0]["market_cap_rank"]) == 1
    assert int(selected.iloc[0]["market_cap_rank_all_sh_sz_a"]) == 2
    assert int(selected.attrs["excluded_under_3m_count"]) == 1
    assert selected["ts_code"].is_unique


def test_snapshot_discovery_uses_filename_date() -> None:
    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        root = Path(temp_dir)
        older = root / "daily_basic_20260811.parquet"
        latest = root / "daily_basic_20260812.parquet"
        older.touch()
        latest.touch()
        assert discover_latest_snapshot(root, "daily_basic") == latest


def test_outputs_are_accepted_by_collector() -> None:
    rows = [
        {
            "ts_code": f"{600000 + index:06d}.SH",
            "trade_date": "20260812",
            "total_mv": 1000 - index,
            "name": f"stock-{index}",
            "list_date": "20200101",
        }
        for index in range(99)
    ]
    rows.append(
        {"ts_code": BLUE_CURSOR, "trade_date": "20260812", "total_mv": 1, "name": "蓝色光标", "list_date": "20100226"}
    )
    selected = build_watchlist(pd.DataFrame(rows), top_n=99)
    with tempfile.TemporaryDirectory(dir=CURRENT_DIR) as temp_dir:
        output_dir = Path(temp_dir)
        paths = write_watchlist_outputs(
            selected,
            output_dir=output_dir,
            symbols_path=output_dir / "symbols.txt",
            source_path=output_dir / "daily_basic_20260812.parquet",
            names_source_path=None,
        )
        symbols = load_symbols(paths["symbols"], max_symbols=100)
        assert len(symbols) == 100
        assert symbols[-1] == BLUE_CURSOR
        assert paths["csv"].is_file()
        assert paths["metadata"].is_file()
        assert paths["versioned_symbols"].is_file()


def main() -> None:
    tests = [
        test_selects_top_n_sh_sz_and_forces_blue_cursor,
        test_snapshot_discovery_uses_filename_date,
        test_outputs_are_accepted_by_collector,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    main()
