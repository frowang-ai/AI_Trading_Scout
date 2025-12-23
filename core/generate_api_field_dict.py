from __future__ import annotations
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from get_data_tushare.config import DATA_ROOT

DOC_PATH = Path("docs/tushare_api_docs/tushare_all_apis_combined.md").resolve()
OUTPUT_DIR = Path("docs/fetch_data_from_api/generated").resolve()

SUPPORTED_APIS = [
    "daily",
    "daily_basic",
    "adj_factor",
    "stk_limit",
    "moneyflow",
    "stk_factor",
    "stk_factor_pro",
    "stk_nineturn",
    "stk_auction",
]

def read_doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8", errors="ignore")

def extract_official_fields(doc: str, api_name: str) -> List[str]:
    m = re.search(rf"\*\*接口\*\*\s*:\s*`{re.escape(api_name)}`", doc)
    if not m:
        m = re.search(rf"接口\s*:\s*`{re.escape(api_name)}`", doc)
    if not m:
        return []
    start = m.end()
    section = doc[start:]
    # Find "输出参数" section
    m_out = re.search(r"##\s*输出参数", section)
    if not m_out:
        return []
    out_section = section[m_out.end():]
    # Find the markdown table rows (lines starting with '|')
    lines = []
    for line in out_section.splitlines():
        if line.strip().startswith("|"):
            lines.append(line.strip())
        else:
            # stop when table ends and a non-table content appears after at least header
            if lines:
                break
    if not lines:
        return []
    # Parse table header to locate the column index for field name
    # Assume first column is field name.
    fields: List[str] = []
    for i, line in enumerate(lines):
        # skip header and separator lines
        if i <= 1:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if cols:
            fields.append(cols[0])
    return fields

def list_local_files_for_api(api_name: str) -> List[Path]:
    base = DATA_ROOT / "raw" / "daily"
    files: List[Path] = []
    if not base.exists():
        return files
    for ydir in sorted(p for p in base.iterdir() if p.is_dir()):
        files.extend(sorted(ydir.glob(f"{api_name}_*.parquet")))
    return files

def infer_local_columns(files: List[Path], sample_limit: int = 20) -> List[str]:
    cols = set()
    for i, fp in enumerate(files[:sample_limit]):
        try:
            df = pd.read_parquet(fp)
        except Exception:
            continue
        for c in df.columns:
            cols.add(c)
    return sorted(cols)

def api_overview(files: List[Path]) -> Dict[str, object]:
    if not files:
        return {"total_days": 0}
    total_records = 0
    days: List[str] = []
    for fp in files:
        try:
            df = pd.read_parquet(fp, columns=["trade_date"])
        except Exception:
            df = pd.DataFrame({"trade_date": []})
        day = fp.stem.split("_")[-1]
        days.append(day)
        total_records += len(df)
    days_sorted = sorted(days)
    return {
        "total_days": len(files),
        "first_day": days_sorted[0],
        "last_day": days_sorted[-1],
        "total_records": int(total_records),
    }

def write_markdown(api_name: str, local_cols: List[str], official_cols: List[str], overview: Dict[str, object]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUTPUT_DIR / f"{api_name}_fields_vs_official.md"
    intersect = sorted(set(local_cols) & set(official_cols))
    local_only = sorted(set(local_cols) - set(official_cols))
    official_only = sorted(set(official_cols) - set(local_cols))
    content = []
    content.append(f"# {api_name} 字段对照与概览")
    content.append("")
    content.append(f"- 覆盖天数: {overview.get('total_days', 0)}")
    content.append(f"- 首日: {overview.get('first_day', '')}")
    content.append(f"- 末日: {overview.get('last_day', '')}")
    content.append(f"- 总记录数: {overview.get('total_records', 0)}")
    content.append("")
    content.append("## 本地字段")
    content.append("`" + ", ".join(local_cols) + "`")
    content.append("")
    content.append("## 官方字段（来自 combined.md）")
    content.append("`" + ", ".join(official_cols) + "`")
    content.append("")
    content.append("## 一致字段")
    content.append("`" + ", ".join(intersect) + "`")
    content.append("")
    content.append("## 仅本地存在")
    content.append("`" + (", ".join(local_only) if local_only else "") + "`")
    content.append("")
    content.append("## 仅官方文档存在")
    content.append("`" + (", ".join(official_only) if official_only else "") + "`")
    md_path.write_text("\n".join(content), encoding="utf-8")
    return md_path

def write_overview_json(summaries: Dict[str, Dict[str, object]]) -> Path:
    out = OUTPUT_DIR / "apis_overview.json"
    out.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

def main():
    doc = read_doc_text()
    summaries: Dict[str, Dict[str, object]] = {}
    for api in SUPPORTED_APIS:
        files = list_local_files_for_api(api)
        local_cols = infer_local_columns(files)
        official_cols = extract_official_fields(doc, api)
        ov = api_overview(files)
        summaries[api] = {"overview": ov, "local_columns": local_cols, "official_columns": official_cols}
        write_markdown(api, local_cols, official_cols, ov)
    write_overview_json(summaries)

if __name__ == "__main__":
    main()
