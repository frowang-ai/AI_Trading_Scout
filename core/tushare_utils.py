import os
import time
from typing import List, Optional

import pandas as pd

try:
    import tushare as ts
except Exception:
    ts = None

from . import config_core as cfg


def get_pro(token: Optional[str] = None):
    if ts is None:
        raise ImportError("tushare 未安装")
    tok = token or cfg.TUSHARE_TOKEN or os.getenv("TUSHARE_TOKEN")
    if not tok:
        raise ValueError("缺少 TUSHARE_TOKEN")
    return ts.pro_api(tok)


def fetch_stock_basic(pro=None, exchange: Optional[str] = None, list_status: str = "L") -> pd.DataFrame:
    pro = pro or get_pro()
    return pro.stock_basic(exchange=exchange, list_status=list_status,
                           fields="ts_code,symbol,name,area,industry,fullname,market,exchange,list_date")


def fetch_daily(pro=None, ts_codes: Optional[List[str]] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    pro = pro or get_pro()
    frames = []
    if ts_codes:
        for code in ts_codes:
            frames.append(pro.daily(ts_code=code, start_date=start_date, end_date=end_date))
            time.sleep(0.05)
    else:
        frames.append(pro.daily(start_date=start_date, end_date=end_date))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def fetch_daily_basic(pro=None, ts_codes: Optional[List[str]] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    pro = pro or get_pro()
    frames = []
    fields = "ts_code,trade_date,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,total_mv,circ_mv"
    if ts_codes:
        for code in ts_codes:
            frames.append(pro.daily_basic(ts_code=code, start_date=start_date, end_date=end_date, fields=fields))
            time.sleep(0.05)
    else:
        frames.append(pro.daily_basic(start_date=start_date, end_date=end_date, fields=fields))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def fetch_index_daily(pro=None, index_ts_code: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    pro = pro or get_pro()
    code = index_ts_code or cfg.MARKET_INDEX_TS_CODE
    return pro.index_daily(ts_code=code, start_date=start_date, end_date=end_date)


def merge_daily_with_basic(daily: pd.DataFrame, basic: pd.DataFrame) -> pd.DataFrame:
    df = daily.merge(basic, on=["ts_code", "trade_date"], how="left")
    df.rename(columns={
        "open": "开盘",
        "high": "最高",
        "low": "最低",
        "close": "close",
        "vol": "成交量",
        "pct_chg": "涨跌幅",
        "turnover_rate": "换手率%",
        "total_mv": "总市值(亿)",
    }, inplace=True)
    if "总市值(亿)" in df.columns:
        df["总市值(亿)"] = pd.to_numeric(df["总市值(亿)"], errors="coerce") / 1e8
    return df

