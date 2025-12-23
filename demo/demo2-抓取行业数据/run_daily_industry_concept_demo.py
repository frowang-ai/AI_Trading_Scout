import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from get_data_tushare.client import TushareClient
from get_data_tushare.utils import get_today


def main():
    try:
        client = TushareClient()
    except Exception as e:
        print(e)
        return

    today = get_today()

    sb = client.query("stock_basic", exchange="", list_status="L", fields="ts_code,symbol,name,area,industry,list_date")
    print("stock_basic", sb.shape)
    print(sb.head(5))

    bb = client.query("bak_basic", trade_date=today)
    print("bak_basic", bb.shape)
    print(bb.head(5))

    sw_l1 = client.query("index_classify", level="L1", src="SW2021")
    print("index_classify_L1", sw_l1.shape)
    print(sw_l1.head(5))

    ima = client.query("index_member_all", ts_code="000001.SZ")
    print("index_member_all_ts_code", ima.shape)
    print(ima.head(5))

    ci = client.query("ci_index_member", ts_code="000001.SZ")
    print("ci_index_member_ts_code", ci.shape)
    print(ci.head(5))

    ths_idx = client.query("ths_index", type="N")
    print("ths_index_N", ths_idx.shape)
    print(ths_idx.head(5))
    ths_ts = None
    if not ths_idx.empty and "ts_code" in ths_idx.columns:
        ths_ts = ths_idx.iloc[0]["ts_code"]
    ths_mem = client.query("ths_member", ts_code=ths_ts) if ths_ts else pd.DataFrame()
    print("ths_member", ths_mem.shape)
    print(ths_mem.head(5))

    dc_idx = client.query("dc_index", trade_date=today)
    print("dc_index", dc_idx.shape)
    print(dc_idx.head(5))
    dc_ts = None
    if not dc_idx.empty and "ts_code" in dc_idx.columns:
        dc_ts = dc_idx.iloc[0]["ts_code"]
    dc_mem = client.query("dc_member", trade_date=today, ts_code=dc_ts) if dc_ts else pd.DataFrame()
    print("dc_member", dc_mem.shape)
    print(dc_mem.head(5))


if __name__ == "__main__":
    main()
