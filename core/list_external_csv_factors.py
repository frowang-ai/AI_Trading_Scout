from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd

def read_csv_with_fallback(path: Path) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "gb18030", "gbk"]
    last_err = None
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_err = e
            continue
    raise last_err if last_err else RuntimeError("failed to read csv")

def classify_columns(cols: list[str]) -> dict[str, list[str]]:
    ids = []
    base = []
    factors = []
    others = []
    for c in cols:
        lc = c.lower()
        if any(k in lc for k in ["ts_code", "code", "code2", "name", "name2", "trade_date", "date", "time"]):
            ids.append(c)
        elif any(k in lc for k in ["open", "high", "low", "close", "pre_close", "vol", "amount", "pct_chg", "change"]):
            base.append(c)
        elif any(k in lc for k in [
            "macd", "kdj", "rsi", "cci", "boll", "bands", "obv", "dma", "dif", "dem", "adx", "plus_di",
            "volume_ratio", "turnover", "beta", "volatile", "consec", "signal", "sma", "ema", "ma_", "vr", "wr",
        ]):
            factors.append(c)
        else:
            others.append(c)
    return {"ids": ids, "base": base, "factors": factors, "others": others}

def write_markdown(cols: list[str], groups: dict[str, list[str]], out_path: Path) -> None:
    lines = []
    lines.append("# 外部CSV因子清单（20251106_data_sma_feature_color.csv）")
    lines.append("")
    lines.append("## 总览")
    lines.append(f"- 列总数：{len(cols)}")
    lines.append(f"- 标识列：{len(groups['ids'])}")
    lines.append(f"- 基础行情列：{len(groups['base'])}")
    lines.append(f"- 因子列：{len(groups['factors'])}")
    lines.append(f"- 其他列：{len(groups['others'])}")
    lines.append("")
    lines.append("## 明细表")
    lines.append("| 列名 | 分类 |")
    lines.append("|------|------|")
    for c in cols:
        cat = (
            "标识" if c in groups["ids"] else
            "基础行情" if c in groups["base"] else
            "因子" if c in groups["factors"] else
            "其他"
        )
        lines.append(f"| {c} | {cat} |")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")

def main():
    # default location discovered by glob
    csv_path = Path("刘丰硕的代码/测试数据xlsx版/20251106_data_sma_feature_color.csv")
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])
    df = read_csv_with_fallback(csv_path)
    cols = list(map(str, df.columns.tolist()))
    groups = classify_columns(cols)
    out_path = Path("docs/fetch_data_from_api/generated/external_factors_20251106.md")
    write_markdown(cols, groups, out_path)
    print(out_path)

if __name__ == "__main__":
    main()
