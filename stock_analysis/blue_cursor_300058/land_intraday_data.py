#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persist 300058.SZ intraday minute data and derived daily features.

The script is intentionally resumable. Each run fetches only a small number of
uncompleted date segments from Tushare `stk_mins`, appends them to local parquet,
and recalculates daily intraday features from the local cache.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import tushare as ts

CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from get_data_tushare.config import get_tushare_token

TS_CODE = "300058.SZ"
FREQ = "1min"
DEFAULT_START = "2023-01-01"
DEFAULT_END = dt.date.today().strftime("%Y-%m-%d")
DEFAULT_SEGMENT_DAYS = 30
DEFAULT_MAX_API_CALLS = 2
API_SLEEP_SECONDS = 0.45

DATA_DIR = CURRENT_DIR / "data"
RAW_PARQUET = DATA_DIR / "300058_mins_1min.parquet"
RAW_CSV = DATA_DIR / "300058_mins_1min.csv"
FEATURE_CSV = DATA_DIR / "300058_intraday_features.csv"
MANIFEST_JSON = DATA_DIR / "300058_mins_1min_manifest.json"

LEGACY_CACHE = CURRENT_DIR / "_test_mins_cache.parquet"


@dataclass(frozen=True)
class Segment:
    start_date: dt.date
    end_date: dt.date

    @property
    def key(self) -> str:
        return f"{self.start_date.isoformat()}__{self.end_date.isoformat()}"

    @property
    def api_start(self) -> str:
        return f"{self.start_date.isoformat()} 09:00:00"

    @property
    def api_end(self) -> str:
        return f"{self.end_date.isoformat()} 20:00:00"


def parse_date(value: str) -> dt.date:
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date, expected YYYY-MM-DD: {value}") from exc


def build_segments(start: dt.date, end: dt.date, segment_days: int) -> list[Segment]:
    if start > end:
        raise ValueError(f"start date must be <= end date: {start} > {end}")
    if segment_days <= 0:
        raise ValueError("segment_days must be positive")

    segments: list[Segment] = []
    cursor = start
    while cursor <= end:
        seg_end = min(cursor + dt.timedelta(days=segment_days), end)
        segments.append(Segment(cursor, seg_end))
        cursor = seg_end + dt.timedelta(days=1)
    return segments


def read_manifest() -> dict[str, Any]:
    if not MANIFEST_JSON.exists():
        return {"completed_segments": [], "failed_segments": [], "runs": []}
    try:
        return json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"completed_segments": [], "failed_segments": [], "runs": []}
    except Exception as exc:
        raise RuntimeError(f"Failed to read manifest: {MANIFEST_JSON}; reason: {exc}") from exc


def write_manifest(manifest: dict[str, Any]) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST_JSON.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to write manifest: {MANIFEST_JSON}; reason: {exc}") from exc


def load_existing_minutes() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in (RAW_PARQUET, LEGACY_CACHE):
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
        except Exception as exc:
            raise RuntimeError(f"Failed to read parquet: {path}; reason: {exc}") from exc
        if not df.empty:
            frames.append(df)

    if not frames:
        return pd.DataFrame()
    return clean_minutes(pd.concat(frames, ignore_index=True))


def clean_minutes(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    required = {"ts_code", "trade_time", "open", "high", "low", "close", "vol", "amount"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"minute data missing required columns: {missing}")

    out = df.copy()
    out["trade_time"] = pd.to_datetime(out["trade_time"], errors="coerce")
    out = out[out["trade_time"].notna()].copy()
    out = out[out["ts_code"].astype(str) == TS_CODE].copy()
    out = out.drop_duplicates(subset=["ts_code", "trade_time"])
    out = out.sort_values("trade_time").reset_index(drop=True)
    out["trade_date"] = out["trade_time"].dt.strftime("%Y%m%d")
    out["minute_seq"] = out.groupby("trade_date").cumcount()
    return out


def fetch_segment(pro: Any, segment: Segment) -> pd.DataFrame:
    df = pro.stk_mins(
        ts_code=TS_CODE,
        freq=FREQ,
        start_date=segment.api_start,
        end_date=segment.api_end,
    )
    if df is None or df.empty:
        return pd.DataFrame()
    return clean_minutes(df)


def append_and_save(existing: pd.DataFrame, new_frames: list[pd.DataFrame], write_csv: bool) -> pd.DataFrame:
    frames = [existing] if existing is not None and not existing.empty else []
    frames.extend([df for df in new_frames if df is not None and not df.empty])
    if not frames:
        return pd.DataFrame()

    combined = clean_minutes(pd.concat(frames, ignore_index=True))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        combined.to_parquet(RAW_PARQUET, index=False)
        if write_csv:
            combined.to_csv(RAW_CSV, index=False, encoding="utf-8-sig")
    except Exception as exc:
        raise RuntimeError(f"Failed to save minute data under {DATA_DIR}; reason: {exc}") from exc
    return combined


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0 or pd.isna(denominator):
        return np.nan
    return numerator / denominator


def calculate_intraday_features(mins: pd.DataFrame) -> pd.DataFrame:
    output_columns = [
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "n_bars",
        "first_5m_ret",
        "first_15m_ret",
        "first_15m_vwap_dev",
        "morning_fade",
        "vol_30m_ratio",
        "pm_reclaim",
        "peak_frac",
        "speed_ratio",
        "path_corr",
        "peak_time",
    ]
    if mins is None or mins.empty:
        return pd.DataFrame(columns=output_columns)

    rows: list[dict[str, Any]] = []
    for trade_date, day_raw in mins.groupby("trade_date", sort=True):
        day = day_raw.sort_values("trade_time").reset_index(drop=True)
        n_bars = len(day)
        if n_bars < 30:
            continue

        open_p = float(day.iloc[0]["open"])
        close_p = float(day.iloc[-1]["close"])
        high_p = float(day["high"].max())
        low_p = float(day["low"].min())
        total_vol = float(day["vol"].sum())

        peak_idx = int(day["high"].idxmax())
        peak_min = int(day.iloc[peak_idx]["minute_seq"])
        total_min = max(n_bars - 1, 1)

        up_pct = safe_ratio(high_p - open_p, open_p) * 100
        down_pct = safe_ratio(high_p - close_p, high_p) * 100
        up_speed = safe_ratio(up_pct, max(peak_min, 1))
        down_speed = safe_ratio(down_pct, max(total_min - peak_min, 1))
        speed_ratio = safe_ratio(up_speed, down_speed) if down_speed and down_speed > 0 else np.nan

        first_5m_ret = np.nan
        if n_bars >= 5:
            first_5m_ret = safe_ratio(float(day.iloc[4]["close"]), open_p) - 1

        first_15m_ret = np.nan
        first_15m_vwap_dev = np.nan
        if n_bars >= 15:
            first_15 = day.iloc[:15]
            first_15m_ret = safe_ratio(float(day.iloc[14]["close"]), open_p) - 1
            first_15m_amount = float(first_15["amount"].sum())
            first_15m_vol = float(first_15["vol"].sum())
            first_15m_vwap = safe_ratio(first_15m_amount, first_15m_vol * 100)
            first_15m_vwap_dev = (safe_ratio(float(day.iloc[14]["close"]), first_15m_vwap) - 1) * 100

        morning_high = float(day.iloc[:30]["high"].max())
        vol_30m_ratio = safe_ratio(float(day.iloc[:30]["vol"].sum()), total_vol)

        morning_fade = np.nan
        if n_bars > 120:
            morning_fade = safe_ratio(float(day.iloc[120]["close"]), morning_high) - 1

        pm_reclaim = np.nan
        if n_bars > 180:
            pm_reclaim = safe_ratio(close_p, float(day.iloc[180]["close"])) - 1

        ret_path = (day["close"].astype(float) / open_p - 1).diff().dropna()
        path_corr = ret_path.autocorr(lag=1) if len(ret_path) > 10 else np.nan

        rows.append(
            {
                "trade_date": trade_date,
                "open": round(open_p, 4),
                "high": round(high_p, 4),
                "low": round(low_p, 4),
                "close": round(close_p, 4),
                "n_bars": n_bars,
                "first_5m_ret": round(first_5m_ret, 6) if pd.notna(first_5m_ret) else np.nan,
                "first_15m_ret": round(first_15m_ret, 6) if pd.notna(first_15m_ret) else np.nan,
                "first_15m_vwap_dev": round(first_15m_vwap_dev, 6) if pd.notna(first_15m_vwap_dev) else np.nan,
                "morning_fade": round(morning_fade, 6) if pd.notna(morning_fade) else np.nan,
                "vol_30m_ratio": round(vol_30m_ratio, 6) if pd.notna(vol_30m_ratio) else np.nan,
                "pm_reclaim": round(pm_reclaim, 6) if pd.notna(pm_reclaim) else np.nan,
                "peak_frac": round(safe_ratio(peak_min, total_min), 6),
                "speed_ratio": round(speed_ratio, 6) if pd.notna(speed_ratio) else np.nan,
                "path_corr": round(path_corr, 6) if pd.notna(path_corr) else np.nan,
                "peak_time": str(day.iloc[peak_idx]["trade_time"]),
            }
        )

    return pd.DataFrame(rows, columns=output_columns)


def save_features(features: pd.DataFrame) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        features.to_csv(FEATURE_CSV, index=False, encoding="utf-8-sig")
    except Exception as exc:
        raise RuntimeError(f"Failed to save feature CSV: {FEATURE_CSV}; reason: {exc}") from exc


def run(args: argparse.Namespace) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    start = args.start
    end = args.end
    segments = build_segments(start, end, args.segment_days)
    manifest = read_manifest()
    completed = set(manifest.get("completed_segments", []))
    pending = [seg for seg in segments if seg.key not in completed]

    existing = load_existing_minutes()
    print(f"[local] existing minute rows: {len(existing)}")
    print(f"[plan] total segments: {len(segments)}, completed: {len(completed)}, pending: {len(pending)}")

    fetched_frames: list[pd.DataFrame] = []
    run_log: dict[str, Any] = {
        "run_at": dt.datetime.now().isoformat(timespec="seconds"),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "segment_days": args.segment_days,
        "max_api_calls": args.max_api_calls,
        "fetched_segments": [],
        "failed_segments": [],
    }

    if pending and args.max_api_calls > 0:
        token = get_tushare_token()
        pro = ts.pro_api(token)
        for seg in pending[: args.max_api_calls]:
            print(f"[fetch] {seg.api_start} -> {seg.api_end}")
            try:
                df = fetch_segment(pro, seg)
                if df.empty:
                    raise ValueError("Tushare returned 0 rows for this segment")
                fetched_frames.append(df)
                completed.add(seg.key)
                run_log["fetched_segments"].append({"segment": seg.key, "rows": int(len(df))})
                print(f"        rows={len(df)}")
            except Exception as exc:
                message = str(exc)
                run_log["failed_segments"].append({"segment": seg.key, "error": message})
                print(f"        failed={message}")
                break
            time.sleep(args.sleep_seconds)

    combined = append_and_save(existing, fetched_frames, args.write_csv)
    features = calculate_intraday_features(combined)
    save_features(features)

    manifest["completed_segments"] = sorted(completed)
    manifest["failed_segments"] = run_log["failed_segments"]
    manifest.setdefault("runs", []).append(run_log)
    manifest["raw_parquet"] = str(RAW_PARQUET)
    manifest["raw_csv"] = str(RAW_CSV) if args.write_csv else None
    manifest["feature_csv"] = str(FEATURE_CSV)
    manifest["rows"] = int(len(combined))
    manifest["feature_rows"] = int(len(features))
    manifest["min_trade_time"] = str(combined["trade_time"].min()) if not combined.empty else None
    manifest["max_trade_time"] = str(combined["trade_time"].max()) if not combined.empty else None
    write_manifest(manifest)

    if combined.empty:
        print("[saved] no minute rows available; raw parquet was not created or updated")
    else:
        print(f"[saved] raw parquet: {RAW_PARQUET} rows={len(combined)}")
    if args.write_csv:
        print(f"[saved] raw csv: {RAW_CSV}")
    print(f"[saved] features: {FEATURE_CSV} rows={len(features)}")
    print(f"[saved] manifest: {MANIFEST_JSON}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=parse_date, default=parse_date(DEFAULT_START))
    parser.add_argument("--end", type=parse_date, default=parse_date(DEFAULT_END))
    parser.add_argument("--segment-days", type=int, default=DEFAULT_SEGMENT_DAYS)
    parser.add_argument("--max-api-calls", type=int, default=DEFAULT_MAX_API_CALLS)
    parser.add_argument("--sleep-seconds", type=float, default=API_SLEEP_SECONDS)
    parser.add_argument("--write-csv", action="store_true", help="Also write raw minute CSV.")
    return parser


def main() -> None:
    parser = build_parser()
    run(parser.parse_args())


if __name__ == "__main__":
    main()
