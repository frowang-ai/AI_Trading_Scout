import datetime
from typing import List, Optional

import pandas as pd

from .tushare_utils import get_pro, fetch_daily, fetch_daily_basic, fetch_index_daily, merge_daily_with_basic, fetch_stock_basic
from .indicators import compute_all_features, consecutive_count
from . import config_core as cfg


def build_features_for_date(trade_date: str, ts_codes: Optional[List[str]] = None, history_days: Optional[int] = None) -> pd.DataFrame:
    pro = get_pro()
    stock_basic = fetch_stock_basic(pro=pro)
    end_date = trade_date
    hd = history_days or cfg.HISTORY_DAYS
    start_date = (datetime.datetime.strptime(trade_date, "%Y%m%d") - datetime.timedelta(days=hd)).strftime("%Y%m%d")
    daily = fetch_daily(pro=pro, ts_codes=ts_codes, start_date=start_date, end_date=end_date)
    basic = fetch_daily_basic(pro=pro, ts_codes=ts_codes, start_date=start_date, end_date=end_date)
    index_daily = fetch_index_daily(pro=pro, start_date=start_date, end_date=end_date)
    merged = merge_daily_with_basic(daily, basic)
    merged = merged.merge(stock_basic[["ts_code", "name", "industry"]], on="ts_code", how="left")
    merged.rename(columns={"name": "名称", "industry": "行业"}, inplace=True)
    idx = index_daily[["trade_date", "pct_chg"]].rename(columns={"pct_chg": "mkt_ret"})
    merged = merged.merge(idx, on="trade_date", how="left")
    merged["ret"] = merged["涨跌幅"]

    def _beta_corr(g: pd.DataFrame, win: int = 60) -> pd.DataFrame:
        r = g["ret"].astype(float)
        m = g["mkt_ret"].astype(float)
        cov = r.rolling(win).cov(m)
        var_m = m.rolling(win).var()
        beta = cov / var_m.replace(0, pd.NA)
        corr = r.rolling(win).corr(m)
        g["BETA"] = beta
        g["相关性"] = corr
        g["BETA_consec"] = consecutive_count((beta.fillna(0)) >= 1)
        return g

    merged = merged.groupby("ts_code", group_keys=False).apply(_beta_corr)
    features = compute_all_features(merged)
    out = features[features["trade_date"] == trade_date].copy()
    out.rename(columns={"ts_code": "代码"}, inplace=True)
    return out


def export_features_csv(trade_date: str, ts_codes: Optional[List[str]] = None, output_path: Optional[str] = None) -> str:
    df = build_features_for_date(trade_date, ts_codes)
    fname = output_path or f"{trade_date}_data_sma_feature_color.csv"
    df.to_csv(fname, index=False, encoding="utf-8")
    return fname

