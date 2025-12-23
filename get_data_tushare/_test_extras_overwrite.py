from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

_CURRENT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _CURRENT_DIR.parent.resolve()
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from get_data_tushare.fetcher_daily import DailyFetcher, DailyFetcherError
from get_data_tushare.utils import get_raw_daily_api_path


def _sample_df():
    return pd.DataFrame({"ts_code": ["000001.SZ"], "trade_date": ["20251130"], "name": ["A"]})


def test_save_ci_index_dim_skips_when_exists(tmp_path: Path):
    fetcher = DailyFetcher(client=MagicMock())

    # stub build to return a small df
    with patch.object(fetcher, "build_ci_index_dim", return_value=_sample_df()):
        # patch path function
        file_path = tmp_path / "ci_index_dim_20251130.parquet"
        file_path.parent.mkdir(parents=True)
        file_path.write_bytes(b"x" * 2048)

        with patch("get_data_tushare.fetcher_daily.get_raw_daily_api_path", return_value=file_path):
            mtime_before = file_path.stat().st_mtime
            p = fetcher.save_ci_index_dim_to_raw("20251130", overwrite=False)
            assert p == file_path
            assert file_path.exists()
            # ensure not overwritten (mtime unchanged)
            assert file_path.stat().st_mtime == mtime_before


def test_save_ci_index_dim_overwrite_when_forced(tmp_path: Path):
    fetcher = DailyFetcher(client=MagicMock())

    df = _sample_df()
    with patch.object(fetcher, "build_ci_index_dim", return_value=df):
        file_path = tmp_path / "ci_index_dim_20251130.parquet"
        file_path.parent.mkdir(parents=True)
        file_path.write_bytes(b"x" * 2048)

        with patch("get_data_tushare.fetcher_daily.get_raw_daily_api_path", return_value=file_path):
            p = fetcher.save_ci_index_dim_to_raw("20251130", overwrite=True)
            assert p == file_path
            df_loaded = pd.read_parquet(p)
            assert len(df_loaded) == len(df)
            assert "ts_code" in df_loaded.columns


def test_save_industry_panel_skip_and_overwrite(tmp_path: Path):
    fetcher = DailyFetcher(client=MagicMock())
    df = _sample_df()
    with patch.object(fetcher, "build_industry_concept_panel_from_snapshots", return_value=df):
        file_path = tmp_path / "industry_concept_panel_20251130.parquet"
        file_path.parent.mkdir(parents=True)
        file_path.write_bytes(b"x" * 2048)

        with patch("get_data_tushare.fetcher_daily.get_raw_daily_api_path", return_value=file_path):
            # skip
            p = fetcher.save_industry_concept_panel_to_raw("20251130", overwrite=False)
            assert p == file_path

            # overwrite
            p2 = fetcher.save_industry_concept_panel_to_raw("20251130", overwrite=True)
            assert p2 == file_path
            df_loaded = pd.read_parquet(p2)
            assert len(df_loaded) == len(df)


def test_save_raw_industry_concept_skips_existing(tmp_path: Path):
    # Prepare a fake client returning small non-empty dataframes
    client = MagicMock()
    client.query.side_effect = lambda *args, **kwargs: _sample_df()

    fetcher = DailyFetcher(client=client)

    # map names to files under tmp_path
    mapping = {}
    names = [
        "stock_basic",
        "bak_basic",
        "index_classify_L1",
        "index_classify_L2",
        "index_classify_L3",
        "index_member_all",
        "ci_index_member",
        "ths_index",
        "ths_member",
        "dc_index",
        "dc_member",
    ]
    for n in names:
        p = tmp_path / f"{n}_20251130.parquet"
        p.parent.mkdir(parents=True, exist_ok=True)
        mapping[n] = p

    # Pre-create two existing files that should be skipped
    mapping["stock_basic"].write_bytes(b"x" * 2048)
    mapping["bak_basic"].write_bytes(b"x" * 2048)

    def fake_get_path(name, date_str):
        return mapping[name]

    with patch("get_data_tushare.fetcher_daily.get_raw_daily_api_path", side_effect=fake_get_path):
        paths = fetcher.save_raw_industry_concept("20251130", overwrite=False)
        # Ensure that returned paths include all keys and existing ones refer to existing files
        assert "stock_basic" in paths and paths["stock_basic"] == mapping["stock_basic"]
        assert "bak_basic" in paths and paths["bak_basic"] == mapping["bak_basic"]
        # Non-existing ones should have been created
        for n, p in mapping.items():
            assert p.exists()

        # Now force overwrite and ensure files are still present (and overwritten without errors)
        paths2 = fetcher.save_raw_industry_concept("20251130", overwrite=True)
        for n in mapping:
            assert paths2[n] == mapping[n]
            assert mapping[n].exists()


if __name__ == "__main__":
    pytest.main([__file__, "-q"])