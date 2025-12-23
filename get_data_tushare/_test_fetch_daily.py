"""
日线数据获取模块单元测试。

测试策略：
1. 使用 Mock 替代真实 Tushare API 调用
2. 验证核心逻辑：路径生成、数据校验、文件保存
3. 遵循《工程实践规范》中的测试先行策略

运行方式:
    pytest get_data_tushare/_test_fetch_daily.py -v
    
    或直接运行:
    python get_data_tushare/_test_fetch_daily.py
"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

# 确保可以直接运行此测试文件
_CURRENT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _CURRENT_DIR.parent.resolve()
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pandas as pd
import pytest

# 测试工具函数（不依赖外部 API）
from get_data_tushare.utils import (
    date_to_str,
    str_to_date,
    get_raw_daily_path,
    get_raw_daily_api_path,
    generate_date_range,
    filter_existing_dates,
    filter_existing_dates_for_api,
    ensure_parent_dir,
)
from get_data_tushare.config import RAW_DAILY_DIR


# =============================================================================
# utils.py 测试
# =============================================================================

class TestDateConversion:
    """日期转换函数测试。"""
    
    def test_date_to_str_from_date_object(self):
        """测试 date 对象转字符串。"""
        d = date(2023, 11, 30)
        assert date_to_str(d) == "20231130"
    
    def test_date_to_str_from_string_yyyymmdd(self):
        """测试 YYYYMMDD 格式字符串。"""
        assert date_to_str("20231130") == "20231130"
    
    def test_date_to_str_from_string_with_dash(self):
        """测试带连字符的日期字符串。"""
        assert date_to_str("2023-11-30") == "20231130"
    
    def test_date_to_str_from_string_with_slash(self):
        """测试带斜杠的日期字符串。"""
        assert date_to_str("2023/11/30") == "20231130"
    
    def test_str_to_date(self):
        """测试字符串转 date 对象。"""
        result = str_to_date("20231130")
        assert result == date(2023, 11, 30)
    
    def test_str_to_date_with_dash(self):
        """测试带连字符字符串转 date。"""
        result = str_to_date("2023-11-30")
        assert result == date(2023, 11, 30)


class TestPathGeneration:
    """路径生成函数测试。"""
    
    def test_get_raw_daily_path_format(self):
        """测试 Raw Layer 路径格式。"""
        path = get_raw_daily_path("20231130")
        
        # 验证路径结构: .../data/raw/daily/2023/daily_20231130.parquet
        assert path.name == "daily_20231130.parquet"
        assert path.parent.name == "2023"
        assert "raw" in path.parts
        assert "daily" in path.parts
    
    def test_get_raw_daily_path_uses_project_data_dir(self):
        """测试路径基于项目 data 目录。"""
        path = get_raw_daily_path("20231130")
        assert RAW_DAILY_DIR in path.parents or path.is_relative_to(RAW_DAILY_DIR.parent.parent)
    
    def test_get_raw_daily_path_different_years(self):
        """测试不同年份的路径。"""
        path_2022 = get_raw_daily_path("20221231")
        path_2023 = get_raw_daily_path("20230101")
        
        assert path_2022.parent.name == "2022"
        assert path_2023.parent.name == "2023"


class TestDateRange:
    """日期范围生成测试。"""
    
    def test_generate_date_range_single_day(self):
        """测试单日范围。"""
        result = generate_date_range("20231130", "20231130")
        assert result == ["20231130"]
    
    def test_generate_date_range_multiple_days(self):
        """测试多日范围。"""
        result = generate_date_range("20231128", "20231130")
        assert result == ["20231128", "20231129", "20231130"]
    
    def test_generate_date_range_cross_month(self):
        """测试跨月范围。"""
        result = generate_date_range("20231130", "20231202")
        assert len(result) == 3
        assert "20231130" in result
        assert "20231201" in result
        assert "20231202" in result


class TestFilterExistingDates:
    """断点续传过滤测试。"""
    
    def test_filter_all_missing(self):
        """测试全部缺失的情况。"""
        dates = ["20231128", "20231129", "20231130"]
        
        # 使用临时目录，确保文件不存在
        with patch("get_data_tushare.utils.RAW_DAILY_DIR", Path("/nonexistent")):
            with patch("get_data_tushare.utils.get_raw_daily_path") as mock_path:
                mock_path.side_effect = lambda d: Path(f"/nonexistent/{d}.parquet")
                result = filter_existing_dates(dates)
        
        assert len(result) == 3
    
    def test_filter_with_existing_file(self, tmp_path: Path):
        """测试存在文件时的过滤。"""
        # 创建一个"已存在"的文件
        existing_file = tmp_path / "2023" / "20231130.parquet"
        existing_file.parent.mkdir(parents=True)
        existing_file.write_bytes(b"x" * 2048)  # 大于 min_file_size
        
        dates = ["20231129", "20231130"]
        
        with patch("get_data_tushare.utils.get_raw_daily_path") as mock_path:
            def fake_path(d):
                if d == "20231130":
                    return existing_file
                return tmp_path / "2023" / f"{d}.parquet"
            
            mock_path.side_effect = fake_path
            result = filter_existing_dates(dates)
        
        assert "20231129" in result
        assert "20231130" not in result


class TestEnsureParentDir:
    """目录创建测试。"""
    
    def test_ensure_parent_dir_creates_nested(self, tmp_path: Path):
        """测试创建嵌套目录。"""
        file_path = tmp_path / "a" / "b" / "c" / "test.parquet"
        assert not file_path.parent.exists()
        
        ensure_parent_dir(file_path)
        
        assert file_path.parent.exists()


# =============================================================================
# fetcher_daily.py 测试（使用 Mock）
# =============================================================================

class TestDailyFetcherWithMock:
    """日线数据获取器测试（Mock API）。"""
    
    @pytest.fixture
    def mock_client(self):
        """创建 Mock Tushare 客户端。"""
        client = MagicMock()
        return client
    
    @pytest.fixture
    def sample_daily_df(self) -> pd.DataFrame:
        """创建样本日线数据。"""
        return pd.DataFrame({
            "ts_code": ["000001.SZ", "000002.SZ", "600000.SH"],
            "trade_date": ["20231130", "20231130", "20231130"],
            "open": [10.5, 15.2, 8.3],
            "high": [10.8, 15.5, 8.6],
            "low": [10.3, 15.0, 8.1],
            "close": [10.6, 15.3, 8.4],
            "pre_close": [10.4, 15.1, 8.2],
            "change": [0.2, 0.2, 0.2],
            "pct_chg": [1.92, 1.32, 2.44],
            "vol": [100000, 200000, 150000],
            "amount": [1050000, 3040000, 1260000],
        })
    
    @pytest.fixture
    def sample_calendar_df(self) -> pd.DataFrame:
        """创建样本交易日历。"""
        return pd.DataFrame({
            "exchange": ["SSE", "SSE", "SSE"],
            "cal_date": ["20231128", "20231129", "20231130"],
            "is_open": ["1", "1", "1"],
            "pretrade_date": ["20231127", "20231128", "20231129"],
        })
    
    def test_fetch_cross_section(self, mock_client, sample_daily_df):
        """测试获取横截面数据。"""
        from get_data_tushare.fetcher_daily import DailyFetcher
        
        mock_client.daily.return_value = sample_daily_df
        
        fetcher = DailyFetcher(client=mock_client)
        df = fetcher.fetch_cross_section("20231130")
        
        mock_client.daily.assert_called_once_with(trade_date="20231130")
        assert len(df) == 3
        assert "ts_code" in df.columns
    
    def test_fetch_trade_calendar(self, mock_client, sample_calendar_df):
        """测试获取交易日历。"""
        from get_data_tushare.fetcher_daily import DailyFetcher
        
        mock_client.trade_cal.return_value = sample_calendar_df
        
        fetcher = DailyFetcher(client=mock_client)
        dates = fetcher.fetch_trade_calendar("20231128", "20231130")
        
        assert dates == ["20231128", "20231129", "20231130"]
    
    def test_save_to_raw(self, mock_client, sample_daily_df, tmp_path: Path):
        """测试保存数据到 Raw Layer。"""
        from get_data_tushare.fetcher_daily import DailyFetcher
        
        fetcher = DailyFetcher(client=mock_client)
        
        # Mock 路径为临时目录
        with patch("get_data_tushare.fetcher_daily.get_raw_daily_path") as mock_path:
            file_path = tmp_path / "2023" / "20231130.parquet"
            mock_path.return_value = file_path
            
            result_path = fetcher.save_to_raw(sample_daily_df, "20231130")
        
        assert result_path.exists()
        assert result_path.suffix == ".parquet"
        
        # 验证文件可读
        df_loaded = pd.read_parquet(result_path)
        assert len(df_loaded) == 3
    
    def test_save_to_raw_rejects_empty_df(self, mock_client):
        """测试拒绝保存空 DataFrame。"""
        from get_data_tushare.fetcher_daily import DailyFetcher, DailyFetcherError
        
        fetcher = DailyFetcher(client=mock_client)
        
        with pytest.raises(DailyFetcherError, match="数据为空"):
            fetcher.save_to_raw(pd.DataFrame(), "20231130")
    
    def test_normalize_dtypes(self, sample_daily_df):
        """测试数据类型标准化。"""
        from get_data_tushare.fetcher_daily import DailyFetcher
        
        df = DailyFetcher._normalize_dtypes(sample_daily_df)
        
        assert df["ts_code"].dtype == object  # str
        assert df["trade_date"].dtype == object
        assert pd.api.types.is_float_dtype(df["open"])
        assert pd.api.types.is_float_dtype(df["vol"])


# =============================================================================
# 集成测试（需要真实 Token，默认跳过）
# =============================================================================

@pytest.mark.skip(reason="需要真实 Tushare Token，手动启用")
class TestDailyFetcherIntegration:
    """集成测试（需要真实 API）。"""
    
    def test_fetch_real_data(self):
        """测试真实 API 调用。"""
        from get_data_tushare import DailyFetcher
        
        fetcher = DailyFetcher()
        df = fetcher.fetch_cross_section("20231130")
        
        assert not df.empty
        assert "ts_code" in df.columns
        print(f"获取到 {len(df)} 条数据")


# =============================================================================
# 运行入口
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
