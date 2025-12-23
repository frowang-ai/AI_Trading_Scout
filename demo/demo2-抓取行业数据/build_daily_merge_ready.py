import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from get_data_tushare.client import TushareClient
from get_data_tushare.utils import get_today


def _filter_membership_today(df: pd.DataFrame, today: str) -> pd.DataFrame:
    if df.empty:
        return df
    x = df.copy()
    for c in ["in_date", "out_date"]:
        if c in x.columns:
            x[c] = x[c].fillna("")
    x["in_ok"] = (x["in_date"] == "") | (x["in_date"] <= today)
    x["out_ok"] = (x["out_date"] == "") | (x["out_date"] >= today)
    return x[x["in_ok"] & x["out_ok"]]


def main():
    client = TushareClient()
    today = get_today()

    sb = client.query("stock_basic", exchange="", list_status="L", fields="ts_code,symbol,name,area,industry,list_date")
    base = client.query("bak_basic", trade_date=today)[["trade_date", "ts_code", "name", "industry", "area"]]

    ts_list = sb["ts_code"].tolist()

    sw_l3 = client.query("index_classify", level="L3", src="SW2021")[["index_code", "industry_name"]]
    sw_rows = []
    for l3_code, l3_name in sw_l3.to_records(index=False):
        df = client.query("index_member_all", l3_code=l3_code, is_new="Y")
        if df is None or df.empty:
            continue
        df = _filter_membership_today(df, today)
        if df.empty:
            continue
        for _, r in df.iterrows():
            sw_rows.append(
                {
                    "ts_code": r["ts_code"],
                    "sw_l1_code": r["l1_code"],
                    "sw_l1_name": r["l1_name"],
                    "sw_l2_code": r["l2_code"],
                    "sw_l2_name": r["l2_name"],
                    "sw_l3_code": r["l3_code"],
                    "sw_l3_name": r["l3_name"],
                }
            )
    sw_map = pd.DataFrame(sw_rows).drop_duplicates(subset=["ts_code"])

    ci_map = pd.DataFrame(columns=["ts_code", "ci_l1_code", "ci_l1_name", "ci_l2_code", "ci_l2_name", "ci_l3_code", "ci_l3_name"])

    dc_idx = client.query("dc_index", trade_date=today)[["ts_code", "name"]]
    dc_member = client.query("dc_member", trade_date=today)[["trade_date", "ts_code", "con_code", "name"]]
    dc_name_map = dc_idx.set_index("ts_code")["name"].to_dict()
    dc_group = dc_member.groupby("con_code").agg(
        dc_board_codes=("ts_code", lambda s: ",".join(sorted(set(s)))),
        dc_board_names=("ts_code", lambda s: ",".join(sorted({dc_name_map.get(x, "") for x in s}))),
    )
    dc_group = dc_group.rename_axis("ts_code").reset_index()

    ths_idx = client.query("ths_index", type="N")[["ts_code", "name"]]
    ths_name_map = ths_idx.set_index("ts_code")["name"].to_dict()
    ths_rows = []
    for b_code, b_name in ths_idx.to_records(index=False):
        df = client.query("ths_member", ts_code=b_code)
        if df is None or df.empty:
            continue
        for _, r in df.iterrows():
            ths_rows.append(
                {
                    "ts_code": r["con_code"],
                    "ths_board_codes": b_code,
                    "ths_board_names": b_name,
                }
            )
    if ths_rows:
        ths_df = pd.DataFrame(ths_rows)
        ths_group = ths_df.groupby("ts_code").agg(
            ths_board_codes=("ths_board_codes", lambda s: ",".join(sorted(set(s)))),
            ths_board_names=("ths_board_names", lambda s: ",".join(sorted(set(s)))),
        ).reset_index()
    else:
        ths_group = pd.DataFrame(columns=["ts_code", "ths_board_codes", "ths_board_names"])

    out = base.merge(sw_map, on="ts_code", how="left").merge(ci_map, on="ts_code", how="left").merge(dc_group, on="ts_code", how="left").merge(ths_group, on="ts_code", how="left")
    print("merge_ready", out.shape)
    print(out.head(10))
    print(out.isna().sum())


if __name__ == "__main__":
    main()
