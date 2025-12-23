from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from get_data_tushare.config import DATA_ROOT

EXTERNAL_DIR = Path(__file__).resolve().parents[2] / "刘丰硕的代码/2025年11月潘哥数据（全）"
OUT_DIR = Path(__file__).resolve().parent / "output/factors"

def list_external_files() -> List[Path]:
    return sorted([p for p in EXTERNAL_DIR.glob("*.xlsx")])

def date_from_filename(fp: Path) -> str:
    m = re.search(r"(20\d{6})", fp.stem)
    return m.group(1) if m else ""

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
    c_dif = get("dif")
    c_dem = get("dem")
    c_macd = get("histgram")
    c_k = get("k_kdj", "slowk")
    c_rsi = get("rsi", "RSI")
    c_lower = get("bands_lower", "lower")
    c_mid = get("bands_middle", "middle")
    c_upper = get("bands_upper", "upper")
    c_cci90 = get("cci_90", "CCI_90")
    c_cci_90 = get("cci_-90", "CCI_-90")
    c_adx = get("ADX")
    c_pdi = get("PLUS_DI")
    c_obv = get("OBV", "obv")
    c_dma = get("dma")
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
        df2["trade_date"] = date_from_filename(fp)
    def assign(num_col: str | None, out_name: str):
        if num_col is not None:
            df2[out_name] = pd.to_numeric(df[num_col], errors="coerce")
    assign(c_dif, "dif_ext")
    assign(c_dem, "dem_ext")
    assign(c_macd, "macd_bar_ext")
    assign(c_k, "kdj_k_ext")
    assign(c_rsi, "rsi_ext")
    assign(c_lower, "boll_lower_ext")
    assign(c_mid, "boll_mid_ext")
    assign(c_upper, "boll_upper_ext")
    assign(c_adx, "adx_ext")
    assign(c_pdi, "pdi_ext")
    assign(c_obv, "obv_ext")
    assign(c_dma, "dma_ext")
    df2["ts_code"] = df2["ts_code"].astype(str).str.strip()
    df2["trade_date"] = df2["trade_date"].astype(str).str.strip()
    return df2

def read_internal_stk_factor(date_str: str) -> pd.DataFrame:
    fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"stk_factor_{date_str}.parquet"
    df = pd.read_parquet(fp)
    keep = {}
    if "macd_dif" in df.columns:
        keep["macd_dif_int"] = pd.to_numeric(df["macd_dif"], errors="coerce")
    if "macd_dea" in df.columns:
        keep["macd_dea_int"] = pd.to_numeric(df["macd_dea"], errors="coerce")
    if "macd" in df.columns:
        keep["macd_bar_int"] = pd.to_numeric(df["macd"], errors="coerce")
    if "kdj_k" in df.columns:
        keep["kdj_k_int"] = pd.to_numeric(df["kdj_k"], errors="coerce")
    if "rsi_6" in df.columns:
        keep["rsi_6_int"] = pd.to_numeric(df["rsi_6"], errors="coerce")
    if "rsi_12" in df.columns:
        keep["rsi_12_int"] = pd.to_numeric(df["rsi_12"], errors="coerce")
    if "rsi_24" in df.columns:
        keep["rsi_24_int"] = pd.to_numeric(df["rsi_24"], errors="coerce")
    if "boll_lower" in df.columns:
        keep["boll_lower_int"] = pd.to_numeric(df["boll_lower"], errors="coerce")
    if "boll_mid" in df.columns:
        keep["boll_mid_int"] = pd.to_numeric(df["boll_mid"], errors="coerce")
    if "boll_upper" in df.columns:
        keep["boll_upper_int"] = pd.to_numeric(df["boll_upper"], errors="coerce")
    if "cci" in df.columns:
        keep["cci_int"] = pd.to_numeric(df["cci"], errors="coerce")
    return pd.DataFrame({"ts_code": df["ts_code"].astype(str), "trade_date": df["trade_date"].astype(str), **keep})

def read_internal_stk_factor_pro(date_str: str) -> pd.DataFrame:
    fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"stk_factor_pro_{date_str}.parquet"
    df = pd.read_parquet(fp)
    keep = {}
    for c in ["dmi_adx_bfq", "dmi_adx_qfq", "dmi_adx_hfq"]:
        if c in df.columns:
            keep["dmi_adx_qfq_int"] = pd.to_numeric(df[c], errors="coerce")
            break
    for c in ["dmi_pdi_bfq", "dmi_pdi_qfq", "dmi_pdi_hfq"]:
        if c in df.columns:
            keep["dmi_pdi_bfq_int"] = pd.to_numeric(df[c], errors="coerce")
            break
    for c in ["dmi_mdi_bfq", "dmi_mdi_qfq", "dmi_mdi_hfq"]:
        if c in df.columns:
            keep["dmi_mdi_bfq_int"] = pd.to_numeric(df[c], errors="coerce")
            break
    for c in ["obv_qfq", "obv_bfq", "obv_hfq"]:
        if c in df.columns:
            keep["obv_qfq_int"] = pd.to_numeric(df[c], errors="coerce")
            break
    for c in ["dfma_dif_qfq", "dfma_dif_bfq", "dfma_dif_hfq"]:
        if c in df.columns:
            keep["dfma_dif_qfq_int"] = pd.to_numeric(df[c], errors="coerce")
            break
    return pd.DataFrame({"ts_code": df["ts_code"].astype(str), "trade_date": df["trade_date"].astype(str), **keep})

def merge_and_diff(ext: pd.DataFrame, stf: pd.DataFrame, stp: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    keys = ["ts_code", "trade_date"]
    mid = pd.merge(ext, stf, on=keys, how="left")
    merged = pd.merge(mid, stp, on=keys, how="left")
    diffs: Dict[str, float] = {}
    def diff_pair(ext_col: str, int_col: str, out: str):
        if ext_col in merged.columns and int_col in merged.columns:
            d = (pd.to_numeric(merged[ext_col], errors="coerce") - pd.to_numeric(merged[int_col], errors="coerce")).abs()
            merged[out] = d
            diffs[f"{out}_mean"] = float(d.mean(skipna=True)) if len(d) else None
            diffs[f"{out}_median"] = float(d.median(skipna=True)) if len(d) else None
    diff_pair("dif_ext", "macd_dif_int", "diff_macd_dif")
    diff_pair("dem_ext", "macd_dea_int", "diff_macd_dea")
    diff_pair("macd_bar_ext", "macd_bar_int", "diff_macd_bar")
    diff_pair("kdj_k_ext", "kdj_k_int", "diff_kdj_k")
    diff_pair("rsi_ext", "rsi_6_int", "diff_rsi_6")
    diff_pair("rsi_ext", "rsi_12_int", "diff_rsi_12")
    diff_pair("rsi_ext", "rsi_24_int", "diff_rsi_24")
    diff_pair("boll_lower_ext", "boll_lower_int", "diff_boll_lower")
    diff_pair("boll_mid_ext", "boll_mid_int", "diff_boll_mid")
    diff_pair("boll_upper_ext", "boll_upper_int", "diff_boll_upper")
    diff_pair("adx_ext", "dmi_adx_qfq_int", "diff_adx")
    diff_pair("pdi_ext", "dmi_pdi_bfq_int", "diff_pdi")
    diff_pair("obv_ext", "obv_qfq_int", "diff_obv")
    diff_pair("dma_ext", "dfma_dif_qfq_int", "diff_dma_dfma")
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
        stf = read_internal_stk_factor(date_str)
        stp = read_internal_stk_factor_pro(date_str)
        merged, diffs = merge_and_diff(ext, stf, stp)
        (OUT_DIR / f"merged_factors_{date_str}.csv").write_text(merged.to_csv(index=False), encoding="utf-8")
        usable_cols = [
            "ts_code","trade_date",
            "macd_dif_int","dif_ext","diff_macd_dif",
            "macd_dea_int","dem_ext","diff_macd_dea",
            "macd_bar_int","macd_bar_ext","diff_macd_bar",
            "kdj_k_int","kdj_k_ext","diff_kdj_k",
            "rsi_6_int","rsi_ext","diff_rsi_6",
            "boll_lower_int","boll_lower_ext","diff_boll_lower",
            "boll_mid_int","boll_mid_ext","diff_boll_mid",
            "boll_upper_int","boll_upper_ext","diff_boll_upper",
            "dmi_pdi_bfq_int","pdi_ext","diff_pdi",
            "dfma_dif_qfq_int","dma_ext","diff_dma_dfma",
        ]
        usable = merged[[c for c in usable_cols if c in merged.columns]]
        (OUT_DIR / f"merged_usable_{date_str}.csv").write_text(usable.to_csv(index=False), encoding="utf-8")
        summary[date_str] = diffs
    df_sum = pd.DataFrame(summary).T
    (OUT_DIR / "summary_factors.csv").write_text(df_sum.to_csv(), encoding="utf-8")
    lines = []
    lines.append("# 技术指标差异报告（2025-11）")
    lines.append("")
    lines.append("对比指标：MACD(dif, dea, bar)、KDJ(K)、RSI(6/12/24)、BOLL(lower/mid/upper)、DMI(ADX/PDI)、OBV、DMA≈DFMA")
    lines.append("")
    lines.append(df_sum.to_string())
    (OUT_DIR / "factors_diff_report.md").write_text("\n".join(lines), encoding="utf-8")
    usable_note = []
    usable_note.append("# 可用指标逐日导出说明")
    usable_note.append("")
    usable_note.append("已输出逐日可用指标对照：merged_usable_YYYYMMDD.csv（不含 OBV）")
    usable_note.append("包含：MACD(dif, dea, bar)、KDJ(K)、RSI(6)、BOLL(lower/mid/upper)、DMI(PDI)、DMA≈DFMA 与外部列及差异")
    (OUT_DIR / "usable_factors_report.md").write_text("\n".join(usable_note), encoding="utf-8")
    return summary

if __name__ == "__main__":
    run()
