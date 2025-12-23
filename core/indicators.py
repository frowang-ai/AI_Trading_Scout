import numpy as np
import pandas as pd
from typing import Tuple


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    diff = close.diff()
    gain = diff.clip(lower=0)
    loss = -diff.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val.fillna(0)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    dif = ema_fast - ema_slow
    dem = ema(dif, signal)
    hist = dif - dem
    return dif, dem, hist


def typical_price(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    return (high + low + close) / 3


def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    tp = typical_price(high, low, close)
    sma_tp = tp.rolling(period).mean()
    mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=False)
    cci_val = (tp - sma_tp) / (0.015 * mad)
    return cci_val.fillna(0)


def stochastic_kdj(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 9, k_smooth: int = 3, d_smooth: int = 3) -> Tuple[pd.Series, pd.Series, pd.Series]:
    ll = low.rolling(n).min()
    hh = high.rolling(n).max()
    rsv = (close - ll) / (hh - ll).replace(0, np.nan) * 100
    k = rsv.ewm(alpha=1/k_smooth, adjust=False).mean()
    d = k.ewm(alpha=1/d_smooth, adjust=False).mean()
    j = 3 * k - 2 * d
    return k.fillna(0), d.fillna(0), j.fillna(0)


def bollinger(close: pd.Series, period: int = 20, std_mult: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    mid = close.rolling(period).mean()
    std = close.rolling(period).std(ddof=0)
    upper = mid + std_mult * std
    lower = mid - std_mult * std
    return lower.fillna(0), mid.fillna(0), upper.fillna(0)


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff().fillna(0))
    return (direction * volume).fillna(0).cumsum()


def dmi_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.DataFrame({"tr1": tr1, "tr2": tr2, "tr3": tr3}).max(axis=1)
    atr = pd.Series(tr).ewm(alpha=1/period, adjust=False).mean()
    plus_di = 100 * (pd.Series(plus_dm).ewm(alpha=1/period, adjust=False).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm).ewm(alpha=1/period, adjust=False).mean() / atr)
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan))
    adx = pd.Series(dx).ewm(alpha=1/period, adjust=False).mean()
    return adx.fillna(0), plus_di.fillna(0), minus_di.fillna(0)


def consecutive_count(condition: pd.Series) -> pd.Series:
    cnt = []
    run = 0
    last = None
    for val in condition.fillna(False).astype(bool):
        if val:
            run = (run + 1) if last else 1
        else:
            run = 0
        cnt.append(run)
        last = val
    return pd.Series(cnt, index=condition.index)


def compute_all_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.sort_values(["ts_code", "trade_date"], inplace=True)
    df["日期"] = pd.to_datetime(df["trade_date"], format="%Y%m%d", errors="coerce")
    df["lst_close"] = df.groupby("ts_code")["close"].shift(1)
    df["涨跌幅"] = (df["close"] / df["lst_close"] - 1.0) * 100
    df["jump"] = (df["开盘"] / df["lst_close"] - 1.0) * 100
    df["平均量比_50天"] = df.groupby("ts_code")["成交量"].transform(lambda s: s / s.rolling(50).mean())
    df["volume_ratio_calc"] = df.groupby("ts_code")["成交量"].transform(lambda s: s / s.shift(1))
    df["放量天数_volume"] = df.groupby("ts_code")["volume_ratio_calc"].transform(lambda s: consecutive_count(s > 1.5))
    df["平均量比_50天_volume"] = df.groupby("ts_code")["平均量比_50天"].transform(lambda s: consecutive_count(s > 1.2))
    df["波动率"] = df.groupby("ts_code")["涨跌幅"].transform(lambda s: s.rolling(20).std())
    df["volatile_consec"] = df.groupby("ts_code")["涨跌幅"].transform(lambda s: consecutive_count(s.abs() > 2))
    dif, dem, hist = macd(df["close"])
    df["dif"], df["dem"], df["histgram"] = dif, dem, hist
    df["macd_signal"] = np.where((df["dif"].shift(1) < df["dem"].shift(1)) & (df["dif"] > df["dem"]), 1,
                               np.where((df["dif"].shift(1) > df["dem"].shift(1)) & (df["dif"] < df["dem"]), -1, 0))
    df["dif_dem"] = df["dif"] - df["dem"]
    df["macd_consec"] = df.groupby("ts_code")["dif_dem"].transform(lambda s: consecutive_count(s > 0))
    df["dif_0"] = (df["dif"] > 0).astype(int)
    df["dem_0"] = (df["dem"] > 0).astype(int)
    df["macdcons_consec"] = df.groupby("ts_code")["dif_0"].transform(lambda s: consecutive_count(s > 0))
    df["demcons_consec"] = df.groupby("ts_code")["dem_0"].transform(lambda s: consecutive_count(s > 0))
    k, d, j = stochastic_kdj(df["最高"], df["最低"], df["close"])
    df["slowk"], df["k_kdj"], df["slowkdj_signal"] = k, d, np.where(k > d, 1, -1)
    df["slowkdj_consec"] = df.groupby("ts_code")["slowkdj_signal"].transform(lambda s: consecutive_count(s > 0))
    rsi_val = rsi(df["close"])
    df["RSI"], df["rsi"] = rsi_val, rsi_val
    df["rsi_consec"] = df.groupby("ts_code")["RSI"].transform(lambda s: consecutive_count(s > 50))
    df["超买"] = (df["RSI"] >= 70).astype(int)
    df["超卖"] = (df["RSI"] <= 30).astype(int)
    cci_val = cci(df["最高"], df["最低"], df["close"])
    df["CCI_-90"] = (cci_val <= -90).astype(int)
    df["CCI_90"] = (cci_val >= 90).astype(int)
    df["cci_-90"] = cci_val
    df["cci_90"] = cci_val
    df["cci_lower_consec"] = df.groupby("ts_code")["CCI_-90"].transform(lambda s: consecutive_count(s > 0))
    df["cci_upper_consec"] = df.groupby("ts_code")["CCI_90"].transform(lambda s: consecutive_count(s > 0))
    lower, middle, upper = bollinger(df["close"]) 
    df["lower"], df["middle"], df["upper"] = lower, middle, upper
    df["bands_lower"], df["bands_middle"], df["bands_upper"] = lower, middle, upper
    df["bands_lower_consec"] = df.groupby("ts_code")["close"].transform(lambda s: consecutive_count(s < lower))
    df["bands_middle_consec"] = df.groupby("ts_code")["close"].transform(lambda s: consecutive_count(s > middle))
    df["bands_upper_consec"] = df.groupby("ts_code")["close"].transform(lambda s: consecutive_count(s > upper))
    df["OBV"] = obv(df["close"], df["成交量"]).fillna(0)
    df["obv"] = df["OBV"]
    df["obv_consec"] = df.groupby("ts_code")["OBV"].transform(lambda s: consecutive_count(s.diff() > 0))
    adx, plus_di, minus_di = dmi_adx(df["最高"], df["最低"], df["close"])
    df["ADX"], df["PLUS_DI"] = adx, plus_di
    df["pdi_adx"] = plus_di - adx
    df["pdi_ndi"] = plus_di - minus_di
    df["dmi_consec"] = df.groupby("ts_code")["pdi_ndi"].transform(lambda s: consecutive_count(s > 0))
    df["dmiadx_consec"] = df.groupby("ts_code")["pdi_adx"].transform(lambda s: consecutive_count(s > 0))
    if "行业" not in df.columns:
        df["行业"] = ""
    df["lon"] = df["close"]
    df["lonma"] = df.groupby("ts_code")["close"].transform(lambda s: s.rolling(20).mean())
    df["lon_lonma"] = (df["lon"] > df["lonma"]).astype(int)
    df["lon_lonma_diff"] = df["lon"] - df["lonma"]
    df["lon_consec"] = df.groupby("ts_code")["lon_lonma"].transform(lambda s: consecutive_count(s > 0))
    df["lon_0"] = (df["lon"] > 0).astype(int)
    df["loncons_consec"] = df.groupby("ts_code")["lon_0"].transform(lambda s: consecutive_count(s > 0))
    df["lonma_0"] = (df["lonma"] > 0).astype(int)
    df["lonmacons_consec"] = df.groupby("ts_code")["lonma_0"].transform(lambda s: consecutive_count(s > 0))
    df["dma"] = df["close"] - df["lonma"]
    df["dma_consec"] = df.groupby("ts_code")["dma"].transform(lambda s: consecutive_count(s > 0))
    df["code2"] = df["ts_code"]
    df["name2"] = df.get("名称", "")
    df["zhangdiefu2"] = df["涨跌幅"]
    df["volume_consec2"] = df["放量天数_volume"]
    df["volume_50_consec2"] = df["平均量比_50天_volume"]
    return df

