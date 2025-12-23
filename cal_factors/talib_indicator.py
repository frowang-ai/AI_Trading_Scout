from typing import Optional

import numpy as np
import pandas as pd

try:
    import talib
except ImportError as e:
    raise ImportError(
        "talib is required for cal_factors.talib_indicator. "
        "Install with `pip install TA-Lib`."
    ) from e


def _group(df: pd.DataFrame, code_col: str) -> pd.core.groupby.DataFrameGroupBy:
    return df.sort_values([code_col, "trade_date"]).groupby(code_col, group_keys=False)


def add_macd(df: pd.DataFrame,
             price_col: str = "close",
             code_col: str = "ts_code",
             fast: int = 12,
             slow: int = 26,
             signal: int = 9) -> pd.DataFrame:
    """
    Add MACD fields: dif, dem (signal), histgram, macd_signal.
    """
    df = df.copy()

    def _fn(g: pd.DataFrame) -> pd.DataFrame:
        close = g[price_col].astype(float).values
        macd, macdsignal, macdhist = talib.MACD(
            close,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal,
        )
        out = g.copy()
        out["dif"] = macd
        out["dem"] = macdsignal
        out["histgram"] = macdhist
        prev_macd = pd.Series(macd).shift(1)
        prev_sig = pd.Series(macdsignal).shift(1)
        sig = np.where(
            (prev_macd < prev_sig) & (macd > macdsignal), 1,
            np.where((prev_macd > prev_sig) & (macd < macdsignal), -1, 0)
        )
        out["macd_signal"] = sig
        return out

    return _group(df, code_col).apply(_fn)


def add_kdj(df: pd.DataFrame,
            high_col: str = "high",
            low_col: str = "low",
            close_col: str = "close",
            code_col: str = "ts_code",
            fastk_period: int = 9,
            slowk_period: int = 3,
            slowd_period: int = 3) -> pd.DataFrame:
    """
    Add KDJ-style fields using TA-Lib STOCH:
    slowk, slowd (as k_kdj), J_kdj and slowkdj_signal.
    """
    df = df.copy()

    def _fn(g: pd.DataFrame) -> pd.DataFrame:
        high = g[high_col].astype(float).values
        low = g[low_col].astype(float).values
        close = g[close_col].astype(float).values
        slowk, slowd = talib.STOCH(
            high, low, close,
            fastk_period=fastk_period,
            slowk_period=slowk_period, slowk_matype=0,
            slowd_period=slowd_period, slowd_matype=0,
        )
        j = 3 * slowk - 2 * slowd
        out = g.copy()
        out["slowk"] = slowk
        out["k_kdj"] = slowd
        out["J_kdj"] = j
        out["slowkdj_signal"] = np.where(slowk > slowd, 1, -1)
        return out

    return _group(df, code_col).apply(_fn)


def add_rsi(df: pd.DataFrame,
            close_col: str = "close",
            code_col: str = "ts_code",
            period: int = 14) -> pd.DataFrame:
    """
    Add RSI field: RSI (and alias rsi).
    """
    df = df.copy()

    def _fn(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float).values
        rsi = talib.RSI(close, timeperiod=period)
        out = g.copy()
        out["RSI"] = rsi
        out["rsi"] = rsi
        return out

    return _group(df, code_col).apply(_fn)


def add_cci(df: pd.DataFrame,
            high_col: str = "high",
            low_col: str = "low",
            close_col: str = "close",
            code_col: str = "ts_code",
            period: int = 20) -> pd.DataFrame:
    """
    Add CCI_val field (you can derive thresholds like CCI_-90 / CCI_90 outside).
    """
    df = df.copy()

    def _fn(g: pd.DataFrame) -> pd.DataFrame:
        high = g[high_col].astype(float).values
        low = g[low_col].astype(float).values
        close = g[close_col].astype(float).values
        cci = talib.CCI(high, low, close, timeperiod=period)
        out = g.copy()
        out["CCI_val"] = cci
        return out

    return _group(df, code_col).apply(_fn)


def add_bollinger(df: pd.DataFrame,
                  close_col: str = "close",
                  code_col: str = "ts_code",
                  period: int = 20,
                  nbdev: float = 2.0) -> pd.DataFrame:
    """
    Add Bollinger bands: lower, middle, upper.
    """
    df = df.copy()

    def _fn(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float).values
        upper, middle, lower = talib.BBANDS(
            close,
            timeperiod=period,
            nbdevup=nbdev,
            nbdevdn=nbdev,
            matype=0,
        )
        out = g.copy()
        out["lower"] = lower
        out["middle"] = middle
        out["upper"] = upper
        return out

    return _group(df, code_col).apply(_fn)


def add_obv(df: pd.DataFrame,
            close_col: str = "close",
            volume_col: str = "volume",
            code_col: str = "ts_code") -> pd.DataFrame:
    """
    Add OBV field using TA-Lib.
    """
    df = df.copy()

    def _fn(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float).values
        vol = g[volume_col].astype(float).values
        obv = talib.OBV(close, vol)
        out = g.copy()
        out["OBV"] = obv
        return out

    return _group(df, code_col).apply(_fn)


def add_dmi_adx(df: pd.DataFrame,
                high_col: str = "high",
                low_col: str = "low",
                close_col: str = "close",
                code_col: str = "ts_code",
                period: int = 14) -> pd.DataFrame:
    """
    Add DMI/ADX fields: ADX, PLUS_DI, MINUS_DI.
    """
    df = df.copy()

    def _fn(g: pd.DataFrame) -> pd.DataFrame:
        high = g[high_col].astype(float).values
        low = g[low_col].astype(float).values
        close = g[close_col].astype(float).values
        adx = talib.ADX(high, low, close, timeperiod=period)
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=period)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=period)
        out = g.copy()
        out["ADX"] = adx
        out["PLUS_DI"] = plus_di
        out["MINUS_DI"] = minus_di
        return out

    return _group(df, code_col).apply(_fn)


def add_all_talib_indicators(df: pd.DataFrame,
                             code_col: str = "ts_code",
                             price_cols: Optional[dict] = None) -> pd.DataFrame:
    """
    Convenience function: run all TA-Lib based indicators in one call.

    price_cols is an optional mapping to adapt existing column names, e.g.:
        {"open": "开盘", "high": "最高", "low": "最低",
         "close": "close", "volume": "成交量"}
    """
    cols = price_cols or {}

    def col(name: str, default: str) -> str:
        return cols.get(name, default)

    out = df.copy()
    out = add_macd(out, price_col=col("close", "close"), code_col=code_col)
    out = add_kdj(
        out,
        high_col=col("high", "high"),
        low_col=col("low", "low"),
        close_col=col("close", "close"),
        code_col=code_col,
    )
    out = add_rsi(out, close_col=col("close", "close"), code_col=code_col)
    out = add_cci(
        out,
        high_col=col("high", "high"),
        low_col=col("low", "low"),
        close_col=col("close", "close"),
        code_col=code_col,
    )
    out = add_bollinger(
        out,
        close_col=col("close", "close"),
        code_col=code_col,
    )
    out = add_obv(
        out,
        close_col=col("close", "close"),
        volume_col=col("volume", "volume"),
        code_col=code_col,
    )
    out = add_dmi_adx(
        out,
        high_col=col("high", "high"),
        low_col=col("low", "low"),
        close_col=col("close", "close"),
        code_col=code_col,
    )
    return out


