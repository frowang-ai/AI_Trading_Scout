"""
Tushare API 客户端封装。

本模块提供 TushareClient 类，负责：
- API 连接管理（单例模式）
- 限流控制
- 自动重试机制

遵循 SOLID 原则中的单一职责原则（SRP）：只负责底层 API 交互。
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

import pandas as pd

from .config import (
    API_CALL_INTERVAL,
    MAX_RETRY_ATTEMPTS,
    RETRY_INITIAL_WAIT,
    get_tushare_token,
)

if TYPE_CHECKING:
    import tushare as ts

logger = logging.getLogger(__name__)


class TushareClientError(Exception):
    """Tushare 客户端异常基类。"""


class TushareAPIError(TushareClientError):
    """Tushare API 调用异常。"""


class TushareClient:
    """
    Tushare Pro API 客户端封装。
    
    采用单例模式确保全局只有一个 API 实例，
    内置限流控制和重试机制。
    
    Attributes:
        _instance: 单例实例
        _pro: Tushare Pro API 对象
        _last_call_time: 上次 API 调用时间戳
    
    Example:
        >>> client = TushareClient()
        >>> df = client.query("daily", trade_date="20231130")
    """
    
    _instance: TushareClient | None = None
    _initialized: bool = False
    
    def __new__(cls) -> TushareClient:
        """单例模式实现。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """
        初始化 Tushare 客户端。
        
        单例模式下只初始化一次。
        """
        if TushareClient._initialized:
            return
        
        try:
            import tushare as ts_module
        except ImportError as e:
            raise TushareClientError(
                "tushare 库未安装，请运行: pip install tushare"
            ) from e
        
        token = get_tushare_token()
        self._pro: ts.pro_api = ts_module.pro_api(token)
        self._last_call_time: float = 0.0
        
        TushareClient._initialized = True
        logger.info("TushareClient 初始化完成")
    
    @property
    def pro(self) -> ts.pro_api:
        """获取 Tushare Pro API 对象。"""
        return self._pro
    
    def _wait_for_rate_limit(self) -> None:
        """
        限流等待。
        
        确保两次 API 调用之间的间隔不小于 API_CALL_INTERVAL。
        """
        elapsed = time.time() - self._last_call_time
        if elapsed < API_CALL_INTERVAL:
            sleep_time = API_CALL_INTERVAL - elapsed
            time.sleep(sleep_time)
    
    def _update_call_time(self) -> None:
        """更新最后调用时间戳。"""
        self._last_call_time = time.time()
    
    def query(
        self,
        api_name: str,
        *,
        retry: bool = True,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        执行 Tushare API 查询。
        
        Args:
            api_name: API 接口名称，如 "daily", "trade_cal"
            retry: 是否启用重试机制，默认 True
            **kwargs: 传递给 API 的参数
        
        Returns:
            API 返回的 DataFrame
        
        Raises:
            TushareAPIError: API 调用失败且重试耗尽时抛出
        
        Example:
            >>> client = TushareClient()
            >>> df = client.query("daily", trade_date="20231130")
            >>> df = client.query("trade_cal", exchange="SSE", is_open="1")
        """
        last_exception: Exception | None = None
        attempts = MAX_RETRY_ATTEMPTS if retry else 1
        
        for attempt in range(1, attempts + 1):
            try:
                self._wait_for_rate_limit()
                
                # 调用 Tushare API
                result = self._pro.query(api_name, **kwargs)
                
                self._update_call_time()
                
                if result is None:
                    result = pd.DataFrame()
                
                return result
                
            except Exception as e:
                last_exception = e
                wait_time = RETRY_INITIAL_WAIT * (2 ** (attempt - 1))
                
                if attempt < attempts:
                    logger.warning(
                        f"API 调用失败 [{api_name}]，第 {attempt}/{attempts} 次重试，"
                        f"等待 {wait_time:.1f}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"API 调用失败 [{api_name}]，重试耗尽: {e}")
        
        raise TushareAPIError(
            f"API [{api_name}] 调用失败，已重试 {attempts} 次"
        ) from last_exception
    
    def daily(self, **kwargs: Any) -> pd.DataFrame:
        """
        获取日线行情数据。
        
        Args:
            **kwargs: 支持的参数:
                - ts_code: 股票代码（可选）
                - trade_date: 交易日期 YYYYMMDD（可选）
                - start_date: 开始日期（可选）
                - end_date: 结束日期（可选）
        
        Returns:
            日线行情 DataFrame
        """
        return self.query("daily", **kwargs)
    
    def trade_cal(self, **kwargs: Any) -> pd.DataFrame:
        """
        获取交易日历。
        
        Args:
            **kwargs: 支持的参数:
                - exchange: 交易所代码（默认 SSE）
                - start_date: 开始日期
                - end_date: 结束日期
                - is_open: 是否交易日 "0"/"1"
        
        Returns:
            交易日历 DataFrame
        """
        return self.query("trade_cal", **kwargs)
    
    @classmethod
    def reset(cls) -> None:
        """
        重置单例实例（仅用于测试）。
        
        Warning:
            此方法仅应在单元测试中使用！
        """
        cls._instance = None
        cls._initialized = False
