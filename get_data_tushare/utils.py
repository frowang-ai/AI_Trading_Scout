"""
工具函数模块。

提供日期处理、文件路径生成等辅助功能。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Sequence

from .config import DATE_FORMAT, RAW_DAILY_DIR


def date_to_str(d: date | datetime | str) -> str:
    """
    将日期转换为 YYYYMMDD 格式字符串。
    
    Args:
        d: 日期对象或字符串
    
    Returns:
        YYYYMMDD 格式字符串
    
    Example:
        >>> date_to_str(date(2023, 11, 30))
        '20231130'
        >>> date_to_str("2023-11-30")
        '20231130'
    """
    if isinstance(d, str):
        # 处理各种常见格式
        clean = d.replace("-", "").replace("/", "")[:8]
        return clean
    return d.strftime(DATE_FORMAT)


def str_to_date(s: str) -> date:
    """
    将 YYYYMMDD 格式字符串转换为 date 对象。
    
    Args:
        s: YYYYMMDD 格式字符串
    
    Returns:
        date 对象
    
    Example:
        >>> str_to_date("20231130")
        datetime.date(2023, 11, 30)
    """
    clean = s.replace("-", "").replace("/", "")[:8]
    return datetime.strptime(clean, DATE_FORMAT).date()


def get_raw_daily_api_path(api_name: str, trade_date: str) -> Path:
    """
    根据交易日期和 API 名称生成 Raw Layer 日线数据文件路径。
    
    路径格式: data/raw/daily/YYYY/{api_name}_YYYYMMDD.parquet
    """
    date_str = date_to_str(trade_date)
    year = date_str[:4]
    return RAW_DAILY_DIR / year / f"{api_name}_{date_str}.parquet"


def get_raw_daily_path(trade_date: str) -> Path:
    """
    根据交易日期生成 Raw Layer 日线数据文件路径。
    
    路径格式: data/raw/daily/YYYY/daily_YYYYMMDD.parquet
    
    Args:
        trade_date: 交易日期，YYYYMMDD 格式
    
    Returns:
        完整的文件路径
    
    Example:
        >>> get_raw_daily_path("20231130")
        PosixPath('data/raw/daily/2023/daily_20231130.parquet')
    """
    return get_raw_daily_api_path("daily", trade_date)


def ensure_parent_dir(file_path: Path) -> None:
    """
    确保文件的父目录存在。
    
    Args:
        file_path: 文件路径
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)


def get_yesterday() -> str:
    """
    获取昨天的日期字符串。
    
    Returns:
        YYYYMMDD 格式的昨日日期
    """
    return date_to_str(date.today() - timedelta(days=1))


def get_today() -> str:
    """
    获取今天的日期字符串。
    
    Returns:
        YYYYMMDD 格式的今日日期
    """
    return date_to_str(date.today())


def generate_date_range(start_date: str, end_date: str) -> list[str]:
    """
    生成日期范围列表（包含起止日期）。
    
    Args:
        start_date: 开始日期，YYYYMMDD
        end_date: 结束日期，YYYYMMDD
    
    Returns:
        日期字符串列表
    
    Example:
        >>> generate_date_range("20231128", "20231130")
        ['20231128', '20231129', '20231130']
    """
    start = str_to_date(start_date)
    end = str_to_date(end_date)
    
    result: list[str] = []
    current = start
    while current <= end:
        result.append(date_to_str(current))
        current += timedelta(days=1)
    
    return result


def filter_existing_dates(
    dates: Sequence[str],
    *,
    check_file_size: bool = True,
    min_file_size: int = 1024,
) -> list[str]:
    """
    过滤出尚未下载的日期（断点续传支持）。
    
    Args:
        dates: 待检查的日期列表
        check_file_size: 是否检查文件大小
        min_file_size: 最小有效文件大小（字节），小于此值视为无效
    
    Returns:
        尚未下载或文件无效的日期列表
    """
    missing: list[str] = []
    
    for d in dates:
        file_path = get_raw_daily_path(d)
        if not file_path.exists():
            missing.append(d)
        elif check_file_size and file_path.stat().st_size < min_file_size:
            # 文件太小，可能是空文件或下载中断
            missing.append(d)
    
    return missing


def filter_existing_dates_for_api(
    api_name: str,
    dates: Sequence[str],
    *,
    check_file_size: bool = True,
    min_file_size: int = 1024,
) -> list[str]:
    """
    按接口名称过滤尚未下载的日期（支持多接口断点续传）。
    """
    missing: list[str] = []
    
    for d in dates:
        file_path = get_raw_daily_api_path(api_name, d)
        if not file_path.exists():
            missing.append(d)
        elif check_file_size and file_path.stat().st_size < min_file_size:
            missing.append(d)
    
    return missing
