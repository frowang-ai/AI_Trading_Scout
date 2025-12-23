import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from get_data_tushare.client import TushareClient
from get_data_tushare.utils import get_today


def main():
    client = TushareClient()
    today = get_today()

    ci = client.query("ci_daily", trade_date=today)[["ts_code"]].drop_duplicates()
    rows = []
    for code in ci["ts_code"].tolist():
        lvl = None
        name = None
        df3 = client.query("ci_index_member", l3_code=code)
        if df3 is not None and not df3.empty:
            lvl = "L3"
            name = df3.iloc[0]["l3_name"]
        else:
            df2 = client.query("ci_index_member", l2_code=code)
            if df2 is not None and not df2.empty:
                lvl = "L2"
                name = df2.iloc[0]["l2_name"]
            else:
                df1 = client.query("ci_index_member", l1_code=code)
                if df1 is not None and not df1.empty:
                    lvl = "L1"
                    name = df1.iloc[0]["l1_name"]
        rows.append({"as_of_date": today, "ts_code": code, "level": lvl, "name": name})

    dim = pd.DataFrame(rows)
    print("dim_ci_index", dim.shape)
    print(dim.head(10))
    print(dim.isna().sum())


if __name__ == "__main__":
    main()
