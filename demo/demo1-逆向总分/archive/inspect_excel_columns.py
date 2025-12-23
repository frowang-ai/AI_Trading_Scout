from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd

def main():
    fp = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("刘丰硕的代码/2025年11月潘哥数据（全）/20251106_data_sma_feature_color.xlsx")
    df = pd.read_excel(fp)
    print(list(map(str, df.columns.tolist())))
    print(df.head(3).to_string(index=False))

if __name__ == "__main__":
    main()
