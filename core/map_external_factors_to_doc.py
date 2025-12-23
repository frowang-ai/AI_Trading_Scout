from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List
import pandas as pd

EXTERNAL_CSV = Path("刘丰硕的代码/测试数据xlsx版/20251106_data_sma_feature_color.csv")
OVERVIEW_JSON = Path("docs/fetch_data_from_api/generated/apis_overview.json")
OUT_MD = Path("docs/fetch_data_from_api/generated/external_factor_mapping.md")

def read_csv_cols(path: Path) -> List[str]:
    for enc in ["utf-8", "utf-8-sig", "gb18030", "gbk"]:
        try:
            df = pd.read_csv(path, nrows=1, encoding=enc)
            return list(map(str, df.columns.tolist()))
        except Exception:
            continue
    raise RuntimeError("Failed to read CSV with known encodings")

def load_overview(path: Path) -> Dict[str, Dict]:
    return json.loads(path.read_text(encoding="utf-8"))

def build_official_index(overview: Dict[str, Dict]) -> Dict[str, set]:
    idx: Dict[str, set] = {}
    for api, info in overview.items():
        cols = set(info.get("official_columns", []))
        idx[api] = cols
    return idx

def map_external(col: str, official_idx: Dict[str, set]) -> Dict[str, object]:
    c = col.strip()
    cl = c.lower()
    # direct hits across apis
    for api, cols in official_idx.items():
        if c in cols or cl in {s.lower() for s in cols}:
            return {"external": c, "match_type": "exact", "api": api, "fields": [c], "notes": ""}
    # family/synonym mappings
    fams: List[Dict[str, object]] = []
    def add(api: str, fields: List[str], notes: str):
        fams.append({"external": c, "match_type": "family", "api": api, "fields": fields, "notes": notes})
    # Chinese synonyms
    if "涨跌幅" in c or "zhangdiefu" in cl:
        add("daily", ["pct_chg"], "中文同义：涨跌幅→pct_chg")
    if "换手率" in c:
        add("daily_basic", ["turnover_rate"], "中文同义：换手率→turnover_rate")
    if "成交量" in c or cl == "volume_consec2":
        add("daily", ["vol"], "中文同义：成交量→vol；consec为衍生")
    if "总市值" in c:
        add("daily_basic", ["total_mv"], "中文同义：总市值→total_mv")
    if "量比" in c:
        add("daily_basic", ["volume_ratio"], "中文同义：量比→volume_ratio")
    if c in {"lower", "bands_lower"}:
        add("stk_factor", ["boll_lower"], "BOLL→bands_lower 对应 boll_lower")
    if c in {"middle", "bands_middle"}:
        add("stk_factor", ["boll_mid"], "BOLL→bands_middle 对应 boll_mid")
    if c in {"upper", "bands_upper"}:
        add("stk_factor", ["boll_upper"], "BOLL→bands_upper 对应 boll_upper")
    if c in {"dif", "dif_dem"}:
        add("stk_factor", ["macd_dif"], "MACD分量：dif→macd_dif")
    if c in {"dem", "dif_dem"}:
        add("stk_factor", ["macd_dea"], "MACD分量：dem(DEA)→macd_dea")
    if c in {"histgram", "macd_signal", "macd_consec", "macdcons_consec"}:
        add("stk_factor", ["macd"], "MACD主值；signal/consec为衍生")
    if c in {"k_kdj", "slowk"}:
        add("stk_factor", ["kdj_k"], "KDJ：k_kdj/slowk→kdj_k")
    if c in {"slowkdj_signal", "slowkdj_consec"}:
        add("stk_factor", ["kdj_k", "kdj_d", "kdj_j"], "KDJ信号/连日由k/d/j衍生")
    if c in {"RSI", "rsi", "rsi_consec"}:
        add("stk_factor", ["rsi_6", "rsi_12", "rsi_24"], "RSI族：rsi为聚合；*_consec为衍生")
    if c in {"CCI_-90", "CCI_90", "cci_-90", "cci_90"} or "cci_upper" in cl or "cci_lower" in cl:
        add("stk_factor", ["cci"], "CCI阈值衍生；原始字段 cci")
    if c in {"OBV", "obv", "obv_consec"}:
        # obv_* 在 pro 版本
        add("stk_factor_pro", ["obv_bfq", "obv_qfq", "obv_hfq"], "OBV族在stk_factor_pro")
    if c in {"ADX", "pdi_adx", "dmiadx_consec"}:
        add("stk_factor_pro", ["dmi_adx_bfq", "dmi_adx_qfq", "dmi_adx_hfq"], "ADX族在stk_factor_pro")
    if c in {"PLUS_DI", "pdi_ndi", "pdi_ndi"}:
        add("stk_factor_pro", ["dmi_pdi_bfq", "dmi_mdi_bfq"], "DI族在stk_factor_pro（PDI/MDI）")
    if c in {"bands_lower_consec", "bands_middle_consec", "bands_upper_consec"}:
        add("stk_factor", ["boll_lower", "boll_mid", "boll_upper"], "BOLL连日为衍生")
    if c in {"lst_close", "close"}:
        add("daily", ["close"], "收盘价")
    if c in {"code2"}:
        add("daily", ["ts_code"], "代码同义：code→ts_code")
    if c in {"name2"}:
        add("daily", [], "名称非API字段")
    if c in {"jump"}:
        add("daily", [], "跳空为衍生逻辑，不是官方字段")
    if c in {"dma", "dma_consec"}:
        add("stk_factor_pro", [], "DMA不在官方字段列表（可能为自定义）")
    if fams:
        # return first family result; also include alternatives
        fams[0]["alternatives"] = fams[1:]
        return fams[0]
    return {"external": c, "match_type": "not_found", "api": "", "fields": [], "notes": ""}

def render_md(mappings: List[Dict[str, object]]) -> str:
    lines = []
    lines.append("# 外部CSV因子与官方API字段对照")
    lines.append("")
    lines.append("| 外部列 | 匹配类型 | API | 官方字段 | 备注 |")
    lines.append("|--------|----------|-----|----------|------|")
    for m in mappings:
        fields = ", ".join(m["fields"]) if m["fields"] else ""
        lines.append(f"| {m['external']} | {m['match_type']} | {m['api']} | {fields} | {m.get('notes','')} |")
        # include alternatives if any
        for alt in m.get("alternatives", []):
            fields_alt = ", ".join(alt["fields"]) if alt["fields"] else ""
            lines.append(f"| ↳ | family | {alt['api']} | {fields_alt} | {alt.get('notes','')} |")
    return "\n".join(lines)

def main():
    cols = read_csv_cols(EXTERNAL_CSV)
    overview = load_overview(OVERVIEW_JSON)
    official_idx = build_official_index(overview)
    mappings = [map_external(c, official_idx) for c in cols]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(mappings), encoding="utf-8")
    print(OUT_MD)

if __name__ == "__main__":
    main()
