"""Build a 100-symbol SSE watchlist from the latest local market-cap snapshot."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.resolve()
DAILY_ROOT = PROJECT_ROOT / "data" / "raw" / "daily"
DEFAULT_SYMBOLS_PATH = CURRENT_DIR / "symbols.txt"
DEFAULT_OUTPUT_DIR = CURRENT_DIR / "watchlists"
BLUE_CURSOR = "300058.SZ"
SH_A_PREFIXES = ("600", "601", "603", "605", "688", "689")
SZ_A_PREFIXES = ("000", "001", "002", "003", "300", "301")


def is_sh_sz_a_share(ts_code: str) -> bool:
    value = str(ts_code).upper()
    if value.endswith(".SH"):
        return value.split(".", 1)[0].startswith(SH_A_PREFIXES)
    if value.endswith(".SZ"):
        return value.split(".", 1)[0].startswith(SZ_A_PREFIXES)
    return False


def portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.name


def discover_latest_snapshot(root: Path, prefix: str) -> Path:
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d{{8}})\.parquet$")
    candidates: list[tuple[str, Path]] = []
    for path in root.rglob(f"{prefix}_*.parquet"):
        match = pattern.match(path.name)
        if match:
            candidates.append((match.group(1), path.resolve()))
    if not candidates:
        raise FileNotFoundError(f"未找到 {prefix}_YYYYMMDD.parquet: {root}")
    return max(candidates, key=lambda item: item[0])[1]


def build_watchlist(daily_basic: pd.DataFrame, top_n: int = 99) -> pd.DataFrame:
    required = {"ts_code", "trade_date", "total_mv", "name", "list_date"}
    missing = required - set(daily_basic.columns)
    if missing:
        raise ValueError(f"daily_basic 缺少字段: {sorted(missing)}")
    if top_n <= 0:
        raise ValueError("top_n 必须大于 0")

    frame = daily_basic.loc[
        daily_basic["ts_code"].astype(str).map(is_sh_sz_a_share),
        ["ts_code", "trade_date", "total_mv", "name", "list_date"],
    ].copy()
    frame["ts_code"] = frame["ts_code"].astype(str).str.upper()
    frame["trade_date"] = frame["trade_date"].astype(str)
    if frame["trade_date"].nunique() != 1:
        raise ValueError("daily_basic 必须是单一交易日截面")
    frame["total_mv"] = pd.to_numeric(frame["total_mv"], errors="coerce")
    frame["list_date"] = pd.to_datetime(
        frame["list_date"].astype("string"), format="%Y%m%d", errors="coerce"
    )
    trade_date = pd.Timestamp(datetime.strptime(frame["trade_date"].iloc[0], "%Y%m%d"))
    listing_cutoff = trade_date - pd.DateOffset(months=3)
    frame = frame.dropna(subset=["total_mv", "list_date"])
    frame = frame.sort_values(
        ["total_mv", "ts_code"], ascending=[False, True], kind="stable"
    ).drop_duplicates("ts_code", keep="first")
    frame["market_cap_rank_all_sh_sz_a"] = range(1, len(frame) + 1)
    frame["listing_age_eligible"] = frame["list_date"].le(listing_cutoff)
    excluded_under_3m = frame.loc[~frame["listing_age_eligible"]].copy()
    frame = frame.loc[frame["listing_age_eligible"]].copy()
    if len(frame) < top_n:
        raise ValueError(f"沪深有效股票只有 {len(frame)} 只，无法选择前 {top_n} 只")
    if BLUE_CURSOR not in set(frame["ts_code"]):
        raise ValueError(f"最新截面中找不到蓝色光标: {BLUE_CURSOR}")

    frame["market_cap_rank"] = range(1, len(frame) + 1)
    top = frame.head(top_n).copy()
    top["selection_type"] = "top_total_mv"
    if BLUE_CURSOR in set(top["ts_code"]):
        selected = top
        selected.loc[selected["ts_code"] == BLUE_CURSOR, "selection_type"] = (
            "top_total_mv_and_blue_cursor"
        )
    else:
        blue = frame.loc[frame["ts_code"] == BLUE_CURSOR].copy()
        blue["selection_type"] = "forced_blue_cursor"
        selected = pd.concat([top, blue], ignore_index=True)
    selected = selected.reset_index(drop=True)
    selected.insert(0, "selected_order", range(1, len(selected) + 1))
    selected["total_mv_cny_100m"] = selected["total_mv"] / 10_000
    selected["list_date"] = selected["list_date"].dt.strftime("%Y%m%d")
    selected["listing_age_months_min"] = 3
    selected["listing_cutoff_date"] = listing_cutoff.strftime("%Y%m%d")
    selected.attrs["excluded_under_3m_count"] = len(excluded_under_3m)
    selected.attrs["excluded_under_3m_top"] = excluded_under_3m.head(20)[
        ["ts_code", "name", "list_date", "total_mv", "market_cap_rank_all_sh_sz_a"]
    ].assign(list_date=lambda value: value["list_date"].dt.strftime("%Y%m%d")).to_dict(
        orient="records"
    )
    expected_count = top_n if BLUE_CURSOR in set(top["ts_code"]) else top_n + 1
    if len(selected) != expected_count or not selected["ts_code"].is_unique:
        raise RuntimeError("筛选结果数量或唯一性异常")
    return selected


def write_watchlist_outputs(
    selected: pd.DataFrame,
    *,
    output_dir: Path,
    symbols_path: Path,
    source_path: Path,
    names_source_path: Path | None,
) -> dict[str, Path]:
    output_dir = output_dir.resolve()
    symbols_path = symbols_path.resolve()
    trade_date = str(selected["trade_date"].iloc[0])
    output_dir.mkdir(parents=True, exist_ok=True)
    symbols_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"market_cap_top99_plus_blue_cursor_{trade_date}.csv"
    metadata_path = output_dir / f"market_cap_top99_plus_blue_cursor_{trade_date}.json"
    versioned_symbols_path = (
        output_dir / f"symbols_market_cap_top99_plus_blue_cursor_{trade_date}.txt"
    )

    symbols_text = (
        f"# 沪深A股上市满3个月后按 total_mv 取前99只 + 蓝色光标；市值截面 {trade_date}\n"
        f"# source={portable_path(source_path)}\n"
        + "\n".join(selected["ts_code"].astype(str))
        + "\n"
    )
    symbols_path.write_text(symbols_text, encoding="utf-8")
    versioned_symbols_path.write_text(symbols_text, encoding="utf-8")
    selected.to_csv(csv_path, index=False, encoding="utf-8-sig")
    metadata: dict[str, Any] = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "selection": "沪深A股先剔除上市不足3个月，再按total_mv降序取前99只，加蓝色光标300058.SZ",
        "listing_age_rule": "list_date <= trade_date - 3 calendar months",
        "listing_cutoff_date": str(selected["listing_cutoff_date"].iloc[0]),
        "market_cap_field": "Tushare daily_basic.total_mv",
        "market_cap_unit_source": "万元",
        "trade_date": trade_date,
        "source_path": portable_path(source_path),
        "names_source_path": portable_path(names_source_path) if names_source_path else None,
        "selected_count": len(selected),
        "missing_name_count": int(selected["name"].isna().sum())
        if "name" in selected.columns
        else None,
        "blue_cursor_market_cap_rank": int(
            selected.loc[selected["ts_code"] == BLUE_CURSOR, "market_cap_rank"].iloc[0]
        ),
        "blue_cursor_market_cap_rank_all_sh_sz_a": int(
            selected.loc[
                selected["ts_code"] == BLUE_CURSOR, "market_cap_rank_all_sh_sz_a"
            ].iloc[0]
        ),
        "blue_cursor_forced": bool(
            selected.loc[selected["ts_code"] == BLUE_CURSOR, "selection_type"].iloc[0]
            == "forced_blue_cursor"
        ),
        "top99_cutoff_total_mv_cny_100m": float(
            selected.loc[selected["selection_type"] == "top_total_mv", "total_mv_cny_100m"].iloc[-1]
        ),
        "excluded_under_3m_count": int(selected.attrs.get("excluded_under_3m_count", 0)),
        "excluded_under_3m_top": selected.attrs.get("excluded_under_3m_top", []),
        "symbols_path": portable_path(symbols_path),
        "versioned_symbols_path": portable_path(versioned_symbols_path),
        "csv_path": portable_path(csv_path),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "symbols": symbols_path,
        "versioned_symbols": versioned_symbols_path,
        "csv": csv_path,
        "metadata": metadata_path,
    }


def resolve_module_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (CURRENT_DIR / path).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="生成沪深总市值前99只加蓝色光标的100股股票池")
    parser.add_argument("--daily-root", help="默认 data/raw/daily")
    parser.add_argument("--symbols-output", default="symbols.txt")
    parser.add_argument("--report-dir", default="watchlists")
    args = parser.parse_args()

    daily_root = (
        Path(args.daily_root).resolve() if args.daily_root else DAILY_ROOT
    )
    source_path = discover_latest_snapshot(daily_root, "daily_basic")
    names_source_path = discover_latest_snapshot(daily_root, "stock_basic")
    daily_basic = pd.read_parquet(
        source_path, columns=["ts_code", "trade_date", "total_mv"]
    )
    stock_basic = pd.read_parquet(
        names_source_path, columns=["ts_code", "name", "list_date"]
    ).drop_duplicates("ts_code", keep="last")
    source = daily_basic.merge(stock_basic, on="ts_code", how="inner", validate="one_to_one")
    selected = build_watchlist(source, top_n=99)
    paths = write_watchlist_outputs(
        selected,
        output_dir=resolve_module_path(args.report_dir),
        symbols_path=resolve_module_path(args.symbols_output),
        source_path=source_path,
        names_source_path=names_source_path,
    )
    summary = {
        "source": str(source_path),
        "trade_date": str(selected["trade_date"].iloc[0]),
        "selected_count": len(selected),
        "blue_cursor_rank": int(
            selected.loc[selected["ts_code"] == BLUE_CURSOR, "market_cap_rank"].iloc[0]
        ),
        "blue_cursor_rank_all_sh_sz_a": int(
            selected.loc[
                selected["ts_code"] == BLUE_CURSOR, "market_cap_rank_all_sh_sz_a"
            ].iloc[0]
        ),
        "outputs": {name: str(path) for name, path in paths.items()},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
