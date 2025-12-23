"""
每日 LLM 投顾报告 CLI 入口

用法示例：
    uv run python -m production.daily_llm_report --date 20251218

前置条件：
    - 已经运行过 Step1 打分流程，生成对应的
        production_output/scores_full_YYYYMMDD.csv
        production/history/top_YYYYMMDD.json
    - 可选：history 目录下存在更早两天的 top_*.json，用于 3 日持仓窗口统计
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from production.config import OUTPUT_DIR
from get_data_tushare.config import DATA_ROOT
from production.utils.llm_analyst import generate_daily_reports_via_llm


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate daily LLM investment reports based on Top list history."
    )
    parser.add_argument(
        "--date",
        type=str,
        required=True,
        help="目标交易日，格式 YYYYMMDD，例如 20251218。",
    )
    parser.add_argument(
        "--history-window",
        type=int,
        default=3,
        help="用于统计 days_on_top 的最近交易日窗口大小（含当日），默认 3。",
    )
    return parser.parse_args()


def _load_top_df(history_dir: Path, date_str: str) -> pd.DataFrame:
    path = history_dir / f"top_{date_str}.json"
    if not path.exists():
        raise FileNotFoundError(f"未找到 Top 列表文件：{path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    return pd.DataFrame(items)


def _load_full_scores(date_str: str) -> pd.DataFrame:
    """
    加载当日全量评分表，用于为 Top 列表补充完整的特征信息。
    """
    csv_path = OUTPUT_DIR / f"scores_full_{date_str}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"未找到全量评分表文件：{csv_path}")
    return pd.read_csv(csv_path)


def _find_recent_history_dates(history_dir: Path, current_date: str, max_days: int) -> List[str]:
    """
    从 history 目录中查找早于 current_date 的 top_*.json 文件，按日期从近到远排序，截取前 max_days-1 个。
    """
    prefix = "top_"
    suffix = ".json"
    candidates: List[str] = []
    for fp in history_dir.glob("top_*.json"):
        name = fp.name
        if not (name.startswith(prefix) and name.endswith(suffix)):
            continue
        date_part = name[len(prefix) : -len(suffix)]
        if len(date_part) != 8 or not date_part.isdigit():
            continue
        if date_part < current_date:
            candidates.append(date_part)

    candidates.sort(reverse=True)
    # history-window 包含当天，因此这里只取 max_days-1 个
    return candidates[: max_days - 1]


def _build_industry_concept_mapping(date_str: str, ts_codes: List[str]) -> pd.DataFrame:
    """
    基于每日行业/概念原始快照，为指定股票集合构造统一的行业/概念描述。

    - 行业：整合交易所行业 + 申万 L1/L2/L3 + 中信 L1/L2/L3
    - 概念：整合同花顺板块 + 东财概念
    """
    year = date_str[:4]
    daily_dir = DATA_ROOT / "raw" / "daily" / year
    codes_set = set(ts_codes)
    if not codes_set:
        # 无标的时直接返回空映射，避免后续 merge 类型冲突
        return pd.DataFrame(columns=["ts_code", "name", "industry", "concepts"])

    def _read_parquet(name: str) -> pd.DataFrame:
        fp = daily_dir / name
        if not fp.exists():
            return pd.DataFrame()
        return pd.read_parquet(fp)

    # 1) 交易所行业（Tushare stock_basic.industry）+ 股票名称
    sb = _read_parquet(f"stock_basic_{date_str}.parquet")
    sb_ind = pd.DataFrame(columns=["ts_code", "base_industry", "name"])
    if not sb.empty and "ts_code" in sb.columns:
        sb = sb[sb["ts_code"].isin(codes_set)]
        cols = ["ts_code"]
        if "industry" in sb.columns:
            cols.append("industry")
        if "name" in sb.columns:
            cols.append("name")
        sb_ind = sb[cols].copy()
        if "industry" in sb_ind.columns:
            sb_ind = sb_ind.rename(columns={"industry": "base_industry"})

    # 2) 申万行业（index_member_all）
    sw = _read_parquet(f"index_member_all_{date_str}.parquet")
    sw_ind = pd.DataFrame(columns=["ts_code", "sw_path"])
    if not sw.empty and "ts_code" in sw.columns:
        sw = sw[sw["ts_code"].isin(codes_set)].copy()
        if {"l1_name", "l2_name", "l3_name"}.issubset(sw.columns):
            sw["sw_path"] = (
                sw["l1_name"].fillna("")
                + "/"
                + sw["l2_name"].fillna("")
                + "/"
                + sw["l3_name"].fillna("")
            )
            sw_ind = (
                sw.groupby("ts_code")["sw_path"]
                .agg(lambda s: " | ".join(sorted({x for x in s if x})))
                .reset_index()
            )

    # 3) 中信行业（ci_index_member）
    ci = _read_parquet(f"ci_index_member_{date_str}.parquet")
    ci_ind = pd.DataFrame(columns=["ts_code", "ci_path"])
    if not ci.empty and "ts_code" in ci.columns:
        ci = ci[ci["ts_code"].isin(codes_set)].copy()
        if {"l1_name", "l2_name", "l3_name"}.issubset(ci.columns):
            ci["ci_path"] = (
                ci["l1_name"].fillna("")
                + "/"
                + ci["l2_name"].fillna("")
                + "/"
                + ci["l3_name"].fillna("")
            )
            ci_ind = (
                ci.groupby("ts_code")["ci_path"]
                .agg(lambda s: " | ".join(sorted({x for x in s if x})))
                .reset_index()
            )

    # 4) 东财概念（dc_index + dc_member）
    dc_idx = _read_parquet(f"dc_index_{date_str}.parquet")
    dc_member = _read_parquet(f"dc_member_{date_str}.parquet")
    dc_con = pd.DataFrame(columns=["ts_code", "dc_concepts"])
    if not dc_idx.empty and not dc_member.empty:
        if {"ts_code", "name"}.issubset(dc_idx.columns) and {"ts_code", "con_code"}.issubset(
            dc_member.columns
        ):
            dc_idx_map = dc_idx.set_index("ts_code")["name"].to_dict()
            df = dc_member.copy()
            df = df[df["con_code"].isin(codes_set)]
            df["concept_name"] = df["ts_code"].map(dc_idx_map).fillna("")
            df = df[df["concept_name"] != ""]
            if not df.empty:
                dc_con = (
                    df.groupby("con_code")["concept_name"]
                    .agg(lambda s: "、".join(sorted({x for x in s if x})))
                    .reset_index()
                    .rename(columns={"con_code": "ts_code", "concept_name": "dc_concepts"})
                )

    # 5) 同花顺板块（ths_index + ths_member）
    ths_idx = _read_parquet(f"ths_index_{date_str}.parquet")
    ths_member = _read_parquet(f"ths_member_{date_str}.parquet")
    ths_con = pd.DataFrame(columns=["ts_code", "ths_concepts"])
    if not ths_idx.empty and not ths_member.empty:
        if {"ts_code", "name"}.issubset(ths_idx.columns) and {
            "ts_code",
            "con_code",
        }.issubset(ths_member.columns):
            ths_idx_map = ths_idx.set_index("ts_code")["name"].to_dict()
            df = ths_member.copy()
            df = df[df["con_code"].isin(codes_set)]
            df["concept_name"] = df["ts_code"].map(ths_idx_map).fillna("")
            df = df[df["concept_name"] != ""]
            if not df.empty:
                ths_con = (
                    df.groupby("con_code")["concept_name"]
                    .agg(lambda s: "、".join(sorted({x for x in s if x})))
                    .reset_index()
                    .rename(columns={"con_code": "ts_code", "concept_name": "ths_concepts"})
                )

    # 汇总并构造统一字段
    base = pd.DataFrame({"ts_code": list(codes_set)})
    base = base.merge(sb_ind, on="ts_code", how="left")
    base = base.merge(sw_ind, on="ts_code", how="left")
    base = base.merge(ci_ind, on="ts_code", how="left")
    base = base.merge(dc_con, on="ts_code", how="left")
    base = base.merge(ths_con, on="ts_code", how="left")

    def _combine_industry(row: pd.Series) -> str:
        parts: List[str] = []
        if isinstance(row.get("base_industry"), str) and row["base_industry"]:
            parts.append(f"交易所行业: {row['base_industry']}")
        if isinstance(row.get("sw_path"), str) and row["sw_path"]:
            parts.append(f"申万行业: {row['sw_path']}")
        if isinstance(row.get("ci_path"), str) and row["ci_path"]:
            parts.append(f"中信行业: {row['ci_path']}")
        return "；".join(parts)

    def _combine_concepts(row: pd.Series) -> str:
        parts: List[str] = []
        if isinstance(row.get("ths_concepts"), str) and row["ths_concepts"]:
            parts.append(f"同花顺板块: {row['ths_concepts']}")
        if isinstance(row.get("dc_concepts"), str) and row["dc_concepts"]:
            parts.append(f"东财概念: {row['dc_concepts']}")
        return "；".join(parts)

    base["industry"] = base.apply(_combine_industry, axis=1)
    base["concepts"] = base.apply(_combine_concepts, axis=1)

    # 返回时同时携带股票名称，方便后续传递给 LLM
    cols = ["ts_code", "industry", "concepts"]
    if "name" in base.columns:
        cols.insert(1, "name")
    return base[cols]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args()

    date_str = args.date.strip()
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError(f"无效的日期格式：{date_str}，期望 YYYYMMDD。")

    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
    except ValueError as exc:
        raise ValueError(f"无法解析日期：{date_str}，期望 YYYYMMDD。") from exc

    current_date_human = dt.strftime("%Y-%m-%d")

    # 基准路径
    current_dir = Path(__file__).parent.resolve()
    project_root = current_dir.parent.resolve()
    history_dir = project_root / "production" / "history"

    print("==== Daily LLM Report Generator ====")
    print(f"[Info] 目标交易日: {date_str} ({current_date_human})")
    print(f"[Info] History 目录: {history_dir}")

    # 加载当日 Top 列表（仅包含 ts_code / trade_date / 评分等）
    top_shallow = _load_top_df(history_dir, date_str)
    if top_shallow.empty:
        raise RuntimeError(f"当日 Top 列表为空：{date_str}")

    # 加载全量评分表，并在其中筛选出 TopN 对应的完整因子行
    full_scores = _load_full_scores(date_str)

    # 对齐 trade_date 类型，避免 int/str 冲突
    if "trade_date" in full_scores.columns:
        full_scores["trade_date"] = full_scores["trade_date"].astype(str)
    if "trade_date" in top_shallow.columns:
        top_shallow["trade_date"] = top_shallow["trade_date"].astype(str)

    if "trade_date" in full_scores.columns and "trade_date" in top_shallow.columns:
        current_top = pd.merge(
            top_shallow[["ts_code", "trade_date"]],
            full_scores,
            on=["ts_code", "trade_date"],
            how="left",
        )
    else:
        current_top = pd.merge(
            top_shallow[["ts_code"]],
            full_scores,
            on="ts_code",
            how="left",
        )

    # 保持 Top 排序：若存在 rank 列则按 rank 升序
    if "rank" in current_top.columns:
        current_top = current_top.sort_values("rank").reset_index(drop=True)

    # 为当日 Top 补充统一的行业 / 概念描述
    ind_con_map = _build_industry_concept_mapping(date_str, current_top["ts_code"].astype(str).tolist())
    current_top = current_top.merge(ind_con_map, on="ts_code", how="left")

    # 加载最近若干天的历史 Top 列表
    history_dates = _find_recent_history_dates(
        history_dir=history_dir,
        current_date=date_str,
        max_days=args.history_window,
    )
    history_tops: List[pd.DataFrame] = []
    for d in history_dates:
        try:
            df_hist_shallow = _load_top_df(history_dir, d)
        except FileNotFoundError:
            continue
        if df_hist_shallow.empty:
            continue
        # 为 history 也补充完整特征（仅需 ts_code / trade_date / score / rank 即可，这里直接使用浅表即可）
        history_tops.append(df_hist_shallow)

    print(f"[Info] 使用的历史 Top 日期: {history_dates}")

    # 调用 LLM 生成多版本报告
    reports = generate_daily_reports_via_llm(
        current_top=current_top,
        history_tops=history_tops,
        current_date=current_date_human,
    )

    # 保存报告到文件
    report_dir = OUTPUT_DIR / "llm_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    for stage_name, content in reports.items():
        suffix = stage_name.replace("daily_report_", "")
        out_path = report_dir / f"daily_report_{date_str}_{suffix}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"[OK] {stage_name} 报告已保存到: {out_path}")

    print("==== LLM Daily Report Generation Completed ====")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
