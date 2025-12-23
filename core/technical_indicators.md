# Technical Indicators Reference (AI_Trading_Scout)

This document records the main technical indicators used in the project, for future reference and refactoring.

- For each indicator we give:
  - Meaning and intuition
  - Typical usage
  - Calculation method
  - Two code sketches: pure numpy + pandas, and TA-Lib where available
- We assume a DataFrame with at least:

```python
import pandas as pd
import numpy as np

# columns:
#   code or ts_code: symbol
#   trade_date: date (YYYYMMDD or datetime)
#   open, high, low, close
#   volume: traded volume
```

To use TA-Lib you need:

```bash
pip install TA-Lib
```

and in code:

```python
import talib
```

---

## 1. MACD (dif, dem, histgram, macd_signal)

### Meaning and intuition

- Uses two EMAs of different length (fast and slow) to describe trend speed.
- dif = EMA_fast - EMA_slow, dem = EMA(dif), histgram = dif - dem.
- Crosses between dif and dem are often used as buy or sell signals.

### pandas implementation (per symbol)

```python
def macd_pandas(df, price_col="close", group_col="code",
                fast=12, slow=26, signal=9):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _macd(g: pd.DataFrame) -> pd.DataFrame:
        close = g[price_col].astype(float)
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        dif = ema_fast - ema_slow
        dem = dif.ewm(span=signal, adjust=False).mean()
        hist = dif - dem
        out = g.copy()
        out["dif"] = dif
        out["dem"] = dem
        out["histgram"] = hist
        prev_dif = dif.shift(1)
        prev_dem = dem.shift(1)
        sig = np.where(
            (prev_dif < prev_dem) & (dif > dem), 1,
            np.where((prev_dif > prev_dem) & (dif < dem), -1, 0)
        )
        out["macd_signal"] = sig
        return out

    return df.groupby(group_col, group_keys=False).apply(_macd)
```

### TA-Lib implementation

```python
def macd_talib(df, price_col="close", group_col="code",
               fast=12, slow=26, signal=9):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _macd(g: pd.DataFrame) -> pd.DataFrame:
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

    return df.groupby(group_col, group_keys=False).apply(_macd)
```

---

## 2. KDJ (slow K, slow D, J)

### Meaning and intuition

- Stochastic oscillator based on the position of close within the n day high low range.
- First compute RSV, then smooth to get K and D, J is 3K - 2D.

### pandas implementation

```python
def kdj_pandas(df, high_col="high", low_col="low", close_col="close",
               group_col="code", n=9, k_smooth=3, d_smooth=3):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _kdj(g: pd.DataFrame) -> pd.DataFrame:
        high = g[high_col].astype(float)
        low = g[low_col].astype(float)
        close = g[close_col].astype(float)
        ll = low.rolling(n).min()
        hh = high.rolling(n).max()
        rsv = (close - ll) / (hh - ll).replace(0, np.nan) * 100
        k = rsv.ewm(alpha=1 / k_smooth, adjust=False).mean()
        d = k.ewm(alpha=1 / d_smooth, adjust=False).mean()
        j = 3 * k - 2 * d
        out = g.copy()
        out["slowk"] = k
        out["k_kdj"] = d
        out["J_kdj"] = j
        out["slowkdj_signal"] = np.where(k > d, 1, -1)
        return out

    return df.groupby(group_col, group_keys=False).apply(_kdj)
```

### TA-Lib implementation

```python
def kdj_talib(df, high_col="high", low_col="low", close_col="close",
              group_col="code", fastk_period=9,
              slowk_period=3, slowd_period=3):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _kdj(g: pd.DataFrame) -> pd.DataFrame:
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

    return df.groupby(group_col, group_keys=False).apply(_kdj)
```

---

## 3. RSI (Relative Strength Index)

### pandas implementation

```python
def rsi_pandas(df, close_col="close", group_col="code", period=14):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _rsi(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float)
        diff = close.diff()
        gain = diff.clip(lower=0)
        loss = -diff.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        out = g.copy()
        out["RSI"] = rsi.fillna(0)
        return out

    return df.groupby(group_col, group_keys=False).apply(_rsi)
```

### TA-Lib implementation

```python
def rsi_talib(df, close_col="close", group_col="code", period=14):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _rsi(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float).values
        rsi = talib.RSI(close, timeperiod=period)
        out = g.copy()
        out["RSI"] = rsi
        return out

    return df.groupby(group_col, group_keys=False).apply(_rsi)
```

---

## 4. CCI (Commodity Channel Index)

### pandas implementation

```python
def cci_pandas(df, high_col="high", low_col="low", close_col="close",
               group_col="code", period=20):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _cci(g: pd.DataFrame) -> pd.DataFrame:
        high = g[high_col].astype(float)
        low = g[low_col].astype(float)
        close = g[close_col].astype(float)
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(
            lambda x: np.mean(np.abs(x - np.mean(x))), raw=False
        )
        cci = (tp - sma_tp) / (0.015 * mad)
        out = g.copy()
        out["CCI_val"] = cci
        return out

    return df.groupby(group_col, group_keys=False).apply(_cci)
```

### TA-Lib implementation

```python
def cci_talib(df, high_col="high", low_col="low", close_col="close",
              group_col="code", period=20):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _cci(g: pd.DataFrame) -> pd.DataFrame:
        high = g[high_col].astype(float).values
        low = g[low_col].astype(float).values
        close = g[close_col].astype(float).values
        cci = talib.CCI(high, low, close, timeperiod=period)
        out = g.copy()
        out["CCI_val"] = cci
        return out

    return df.groupby(group_col, group_keys=False).apply(_cci)
```

---

## 5. Bollinger Bands (lower, middle, upper)

### pandas implementation

```python
def bollinger_pandas(df, close_col="close", group_col="code",
                     period=20, std_mult=2.0):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _bb(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float)
        mid = close.rolling(period).mean()
        std = close.rolling(period).std(ddof=0)
        upper = mid + std_mult * std
        lower = mid - std_mult * std
        out = g.copy()
        out["lower"] = lower
        out["middle"] = mid
        out["upper"] = upper
        return out

    return df.groupby(group_col, group_keys=False).apply(_bb)
```

### TA-Lib implementation

```python
def bollinger_talib(df, close_col="close", group_col="code",
                    period=20, nbdev=2.0):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _bb(g: pd.DataFrame) -> pd.DataFrame:
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

    return df.groupby(group_col, group_keys=False).apply(_bb)
```

---

## 6. OBV (On Balance Volume)

### pandas implementation

```python
def obv_pandas(df, close_col="close", volume_col="volume",
               group_col="code"):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _obv(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float)
        vol = g[volume_col].astype(float)
        direction = np.sign(close.diff().fillna(0))
        obv = (direction * vol).cumsum()
        out = g.copy()
        out["OBV"] = obv
        return out

    return df.groupby(group_col, group_keys=False).apply(_obv)
```

### TA-Lib implementation

```python
def obv_talib(df, close_col="close", volume_col="volume",
              group_col="code"):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _obv(g: pd.DataFrame) -> pd.DataFrame:
        close = g[close_col].astype(float).values
        vol = g[volume_col].astype(float).values
        obv = talib.OBV(close, vol)
        out = g.copy()
        out["OBV"] = obv
        return out

    return df.groupby(group_col, group_keys=False).apply(_obv)
```

---

## 7. DMI and ADX

### pandas implementation (approximate TA-Lib logic)

```python
def dmi_adx_pandas(df, high_col="high", low_col="low", close_col="close",
                   group_col="code", period=14):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _dmi(g: pd.DataFrame) -> pd.DataFrame:
        high = g[high_col].astype(float)
        low = g[low_col].astype(float)
        close = g[close_col].astype(float)

        up = high.diff()
        down = -low.diff()
        plus_dm = np.where((up > down) & (up > 0), up, 0.0)
        minus_dm = np.where((down > up) & (down > 0), down, 0.0)

        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = tr.ewm(alpha=1 / period, adjust=False).mean()
        plus_di = 100 * pd.Series(plus_dm, index=g.index).ewm(
            alpha=1 / period, adjust=False
        ).mean() / atr
        minus_di = 100 * pd.Series(minus_dm, index=g.index).ewm(
            alpha=1 / period, adjust=False
        ).mean() / atr

        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
        adx = dx.ewm(alpha=1 / period, adjust=False).mean()

        out = g.copy()
        out["ADX"] = adx
        out["PLUS_DI"] = plus_di
        out["MINUS_DI"] = minus_di
        return out

    return df.groupby(group_col, group_keys=False).apply(_dmi)
```

### TA-Lib implementation

```python
def dmi_adx_talib(df, high_col="high", low_col="low", close_col="close",
                  group_col="code", period=14):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _dmi(g: pd.DataFrame) -> pd.DataFrame:
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

    return df.groupby(group_col, group_keys=False).apply(_dmi)
```

---

## 8. Volatility and Beta / Correlation (pandas only)

These are naturally expressed with pandas rolling statistics.

### Volatility (rolling std of returns)

```python
def volatility_pandas(df, ret_col="pct_chg", group_col="code", win=20):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _vol(g: pd.DataFrame) -> pd.DataFrame:
        r = g[ret_col].astype(float)
        out = g.copy()
        out["volatility"] = r.rolling(win).std()
        return out

    return df.groupby(group_col, group_keys=False).apply(_vol)
```

### Beta and correlation vs market index

```python
def beta_corr_pandas(df, stock_ret_col="pct_chg",
                     index_ret_col="mkt_ret",
                     group_col="code", win=60):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def _beta(g: pd.DataFrame) -> pd.DataFrame:
        r = g[stock_ret_col].astype(float)
        m = g[index_ret_col].astype(float)
        cov = r.rolling(win).cov(m)
        var_m = m.rolling(win).var()
        beta = cov / var_m.replace(0, np.nan)
        corr = r.rolling(win).corr(m)
        out = g.copy()
        out["BETA"] = beta
        out["CORR"] = corr
        return out

    return df.groupby(group_col, group_keys=False).apply(_beta)
```

---

## 9. Volume based features (examples)

Example for average volume ratio and "high volume days":

```python
def volume_features_pandas(df, volume_col="volume",
                           group_col="code", ma_win=50,
                           up_ratio=1.5, ma_ratio_th=1.2):
    df = df.sort_values([group_col, "trade_date"]).copy()

    def consecutive_count(cond: pd.Series) -> pd.Series:
        run = 0
        res = []
        for flag in cond.fillna(False).astype(bool):
            run = run + 1 if flag else 0
            res.append(run)
        return pd.Series(res, index=cond.index)

    def _vol(g: pd.DataFrame) -> pd.DataFrame:
        vol = g[volume_col].astype(float)
        vol_ma = vol.rolling(ma_win).mean()
        volume_ratio = vol / vol_ma
        ratio_prev = vol / vol.shift(1)
        out = g.copy()
        out["volume_ratio_50"] = volume_ratio
        out["high_volume_days"] = consecutive_count(ratio_prev > up_ratio)
        out["high_volume_ratio_days"] = consecutive_count(volume_ratio > ma_ratio_th)
        return out

    return df.groupby(group_col, group_keys=False).apply(_vol)
```

You can map these example columns to your project specific names (for example 平均量比_50天, 放量天数_volume, etc).

