from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from get_data_tushare.config import DATA_ROOT

EXTERNAL_DIR = Path(__file__).resolve().parents[2] / "刘丰硕的代码/2025年11月潘哥数据（全）"
OUT_DIR = Path(__file__).resolve().parent / "output"

PRICE_COLS = ["open", "high", "low", "close", "pre_close"]
BASIC_COLS = ["pct_chg", "vol", "amount", "turnover_rate"]

def list_external_files() -> List[Path]:
    return sorted([p for p in EXTERNAL_DIR.glob("*.xlsx")])

def date_from_filename(fp: Path) -> str:
    m = re.search(r"(20\d{6})", fp.stem)
    if m:
        return m.group(1)
    return ""

def read_external(fp: Path) -> pd.DataFrame:
    df = pd.read_excel(fp)
    cols = {str(c): str(c) for c in df.columns}
    def get(*names: str) -> str | None:
        for n in names:
            if n in cols:
                return n
        return None
    c_code2 = get("code2", "ts_code")
    c_code = get("代码", "code")
    c_name = get("name2", "名称")
    c_date = get("trade_date", "日期")
    c_open = get("open", "开盘")
    c_high = get("high", "最高")
    c_low = get("low", "最低")
    c_close = get("close", "收盘", "收盘价")
    c_vol = get("vol", "成交量")
    c_amount = get("amount", "成交额")
    c_pct = get("pct_chg", "涨跌幅", "zhangdiefu2")
    c_turn = get("turnover_rate", "换手率%", "换手率")
    c_total_mv_bil = get("总市值(亿)")
    c_total_score = get("总分")
    df2 = pd.DataFrame()
    if c_code2 is not None:
        base = df[c_code2].astype(str).str.strip()
        has_suffix = base.str.contains(r"\.")
        is_bjs = "bjs" in fp.stem.lower()
        suffix = base.str[0].map(lambda x: ".SH" if x == "6" else (".SZ" if not is_bjs else ".BJ"))
        df2["ts_code"] = base.where(has_suffix, base + suffix)
    elif c_code is not None:
        base = df[c_code].astype(str).str.strip()
        is_bjs = "bjs" in fp.stem.lower()
        has_suffix = base.str.contains(r"\.")
        suffix = base.str[0].map(lambda x: ".SH" if x == "6" else (".SZ" if not is_bjs else ".BJ"))
        df2["ts_code"] = base.where(has_suffix, base + suffix)
    elif c_name is not None:
        df2["ts_code"] = df[c_name].astype(str)
    else:
        df2["ts_code"] = ""
    if c_date is not None:
        s = df[c_date]
        if pd.api.types.is_datetime64_any_dtype(s):
            df2["trade_date"] = s.dt.strftime("%Y%m%d")
        else:
            df2["trade_date"] = pd.to_datetime(s.astype(str).str.slice(0, 10), errors="coerce").dt.strftime("%Y%m%d")
    else:
        d = date_from_filename(fp)
        df2["trade_date"] = d
    if c_open is not None:
        df2["open"] = pd.to_numeric(df[c_open], errors="coerce")
    if c_high is not None:
        df2["high"] = pd.to_numeric(df[c_high], errors="coerce")
    if c_low is not None:
        df2["low"] = pd.to_numeric(df[c_low], errors="coerce")
    if c_close is not None:
        df2["close"] = pd.to_numeric(df[c_close], errors="coerce")
    if c_vol is not None:
        df2["vol"] = pd.to_numeric(df[c_vol], errors="coerce")
    if c_amount is not None:
        df2["amount"] = pd.to_numeric(df[c_amount], errors="coerce")
    if c_pct is not None:
        df2["pct_chg"] = pd.to_numeric(df[c_pct], errors="coerce")
    if c_turn is not None:
        df2["turnover_rate"] = pd.to_numeric(df[c_turn], errors="coerce")
    if c_total_mv_bil is not None:
    if c_total_score is not None:
        df2["total_score"] = pd.to_numeric(df[c_total_score], errors="coerce")
        df2["total_mv_billion_ext"] = pd.to_numeric(df[c_total_mv_bil], errors="coerce")
    df2["ts_code"] = df2["ts_code"].astype(str).str.strip()
    df2["trade_date"] = df2["trade_date"].astype(str).str.strip()
    return df2

def read_internal_daily(date_str: str) -> pd.DataFrame:
    fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"daily_{date_str}.parquet"
    df = pd.read_parquet(fp)
    return df.astype({"ts_code": "string", "trade_date": "string"})

def read_internal_daily_basic(date_str: str) -> pd.DataFrame:
    fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"daily_basic_{date_str}.parquet"
    df = pd.read_parquet(fp)
    df = df.astype({"ts_code": "string", "trade_date": "string"})
    # 仅保留需要对比的列并重命名为 *_int
    keep = {}
    if "turnover_rate" in df.columns:
        keep["turnover_rate_int"] = pd.to_numeric(df["turnover_rate"], errors="coerce")
    if "total_mv" in df.columns:
        # 转为亿元：原单位万元 → 除以10000
        keep["total_mv_billion_int"] = pd.to_numeric(df["total_mv"], errors="coerce") / 10000.0
    out = pd.DataFrame({"ts_code": df["ts_code"], "trade_date": df["trade_date"], **keep})
    return out

def merge_and_diff(ext: pd.DataFrame, internal: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    keys = ["ts_code", "trade_date"]
    merged = pd.merge(ext, internal, on=keys, suffixes=("_ext", "_int"))
    diffs: Dict[str, float] = {}
    for col in PRICE_COLS + BASIC_COLS:
        c_ext = f"{col}_ext"
        c_int = f"{col}_int"
        if c_ext in merged.columns and c_int in merged.columns:
            d = (pd.to_numeric(merged[c_ext], errors="coerce") - pd.to_numeric(merged[c_int], errors="coerce")).abs()
            merged[f"diff_{col}"] = d
            diffs[f"{col}_mean_abs_diff"] = float(d.mean(skipna=True)) if len(d) else None
            diffs[f"{col}_median_abs_diff"] = float(d.median(skipna=True)) if len(d) else None
    # daily_basic 对比
    if "turnover_rate" in ext.columns and "turnover_rate_int" in merged.columns:
        d = (pd.to_numeric(merged["turnover_rate"], errors="coerce") - pd.to_numeric(merged["turnover_rate_int"], errors="coerce")).abs()
        merged["diff_turnover_rate"] = d
        diffs["turnover_rate_mean_abs_diff"] = float(d.mean(skipna=True)) if len(d) else None
        diffs["turnover_rate_median_abs_diff"] = float(d.median(skipna=True)) if len(d) else None
    if "total_mv_billion_ext" in merged.columns and "total_mv_billion_int" in merged.columns:
        d = (pd.to_numeric(merged["total_mv_billion_ext"], errors="coerce") - pd.to_numeric(merged["total_mv_billion_int"], errors="coerce")).abs()
        merged["diff_total_mv_billion"] = d
        diffs["total_mv_billion_mean_abs_diff"] = float(d.mean(skipna=True)) if len(d) else None
        diffs["total_mv_billion_median_abs_diff"] = float(d.median(skipna=True)) if len(d) else None
    return merged, diffs

def run() -> Dict[str, Dict[str, float]]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = list_external_files()
    summary: Dict[str, Dict[str, float]] = {}
    for fp in files:
        date_str = date_from_filename(fp)
        if not date_str:
            continue
        ext = read_external(fp)
        internal = read_internal_daily(date_str)
        # 合并 daily_basic
        db = read_internal_daily_basic(date_str)
        ext = pd.merge(ext, db, on=["ts_code", "trade_date"], how="left")
        merged, diffs = merge_and_diff(ext, internal)
        out_csv = OUT_DIR / f"merged_{date_str}.csv"
        merged.to_csv(out_csv, index=False, encoding="utf-8")
        summary[date_str] = diffs
    df_sum = pd.DataFrame(summary).T
    df_sum.to_csv(OUT_DIR / "summary_diffs.csv", encoding="utf-8")
    # 输出报告
    lines = []
    lines.append("# 直接映射字段差异报告（2025-11）")
    lines.append("")
    lines.append("## 字段列表（无需计算）")
    lines.append("- `open`, `high`, `low`, `close`（daily）")
    lines.append("- `pct_chg`, `vol`（daily）")
    lines.append("- `turnover_rate`（daily_basic）")
    lines.append("- `total_mv`（daily_basic，转换为亿元比较）")
    lines.append("")
    lines.append("## 差异汇总（均值/中位绝对差）")
    lines.append(df_sum.to_string())
    (OUT_DIR / "direct_mapping_diff_report.md").write_text("\n".join(lines), encoding="utf-8")
    return summary

if __name__ == "__main__":
    run()
