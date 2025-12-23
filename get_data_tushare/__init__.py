"""
Tushare 数据获取模块。

本模块提供从 Tushare Pro API 获取 A 股市场数据的完整解决方案，包括：
- 日线行情数据的按日获取（Cross-Sectional Fetching）
- 历史数据回补（Initialization）
- 每日增量更新（Daily Update）

使用示例:
    >>> from get_data_tushare import DailyFetcher, fetch_daily_data
    >>> 
    >>> # 方式一：使用 DailyFetcher 类
    >>> fetcher = DailyFetcher()
    >>> df = fetcher.fetch_cross_section("20231130")
    >>> 
    >>> # 方式二：使用便捷函数
    >>> df = fetch_daily_data("20231130")

注意:
    使用前请确保已设置环境变量 TUSHARE_TOKEN
"""

from .client import TushareClient, TushareClientError, TushareAPIError
from .config import (
    DATA_ROOT,
    RAW_DAILY_DIR,
    PROJECT_ROOT,
    get_tushare_token,
)
from .fetcher_daily import (
    DailyFetcher,
    DailyFetcherError,
    fetch_daily_data,
    run_backfill,
)
from .utils import (
    date_to_str,
    str_to_date,
    get_raw_daily_path,
    get_today,
    get_yesterday,
)

__all__ = [
    # Client
    "TushareClient",
    "TushareClientError",
    "TushareAPIError",
    # Config
    "DATA_ROOT",
    "RAW_DAILY_DIR",
    "PROJECT_ROOT",
    "get_tushare_token",
    # Fetcher
    "DailyFetcher",
    "DailyFetcherError",
    "fetch_daily_data",
    "run_backfill",
    # Utils
    "date_to_str",
    "str_to_date",
    "get_raw_daily_path",
    "get_today",
    "get_yesterday",
]
