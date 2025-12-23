from pathlib import Path
import sys
from typing import List, Optional

import numpy as np
import pandas as pd

# 以项目根目录（AI_Trading_Scout）为基准
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# 复用全局 Tushare 配置中的 DATA_ROOT，避免路径配置漂移
from get_data_tushare.config import DATA_ROOT  # type: ignore

# 外部 Excel 数据目录（保持与历史脚本语义一致）
EXTERNAL_DIR_NOV = PROJECT_ROOT / "刘丰硕的代码" / "2025年11月潘哥数据（全）"
EXTERNAL_DIR_DEC = PROJECT_ROOT / "刘丰硕的代码" / "12月数据（12.8更新"


def list_dates_from_dir(directory: Path) -> List[str]:
    """从目录中提取所有交易日期（排除 BJS 文件）。"""
    dates = set()
    if not directory.exists():
        return []
    for fp in directory.glob("*.xlsx"):
        if "bjs" in fp.stem.lower():
            continue
        parts = fp.stem.split("_")
        if parts and parts[0].startswith("2025"):
            dates.add(parts[0])
    return sorted(list(dates))


def get_available_dates(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[str]:
    """获取指定范围内的所有可用交易日（来自外部 Excel 目录）。"""
    dates_nov = list_dates_from_dir(EXTERNAL_DIR_NOV)
    dates_dec = list_dates_from_dir(EXTERNAL_DIR_DEC)
    all_dates = sorted(list(set(dates_nov + dates_dec)))

    if start_date:
        all_dates = [d for d in all_dates if d >= start_date]
    if end_date:
        all_dates = [d for d in all_dates if d <= end_date]

    return all_dates


def load_excel_data(date_str: str) -> pd.DataFrame:
    """加载单日 Excel 数据，并标准化为包含 ts_code / trade_date / total_score 的 DataFrame。"""
    ext_fp: Optional[Path] = None
    for directory in [EXTERNAL_DIR_NOV, EXTERNAL_DIR_DEC]:
        if not directory.exists():
            continue
        for fp in directory.glob(f"{date_str}*.xlsx"):
            if "bjs" not in fp.stem.lower():
                ext_fp = fp
                break
        if ext_fp:
            break

    if not ext_fp:
        return pd.DataFrame()

    try:
        df_ext = pd.read_excel(ext_fp)
    except Exception as e:  # pragma: no cover - 仅打印错误信息
        print(f"  Error reading {ext_fp.name}: {e}")
        return pd.DataFrame()

    cols_map = {str(c): str(c) for c in df_ext.columns}

    def get_col(*names: str) -> Optional[str]:
        for n in names:
            if n in cols_map:
                return n
        return None

    c_code = get_col("code2", "ts_code", "代码", "code")
    c_date = get_col("trade_date", "日期")
    c_score = get_col("总分", "total_score")

    if not c_code or not c_score:
        return pd.DataFrame()

    # ts_code 处理
    base = df_ext[c_code].astype(str).str.strip()
    if not base.str.contains(r"\.").any():
        is_bjs = "bjs" in ext_fp.stem.lower()
        suffix = base.str[0].map(lambda x: ".SH" if x == "6" else (".SZ" if not is_bjs else ".BJ"))
        df_ext["ts_code"] = base + suffix
    else:
        df_ext["ts_code"] = base

    # trade_date 固定为文件日期
    df_ext["trade_date"] = date_str

    # total_score 数值化
    df_ext["total_score"] = pd.to_numeric(df_ext[c_score], errors="coerce")

    # 丢弃不必要列
    cols_to_drop = [
        "Unnamed: 0",
        c_code,
        "代码",
        "code",
        "code2",
        "名称",
        "name",
        "name2",
        c_date,
        "日期",
        c_score,
        "总分" if c_score != "总分" else None,
        "lst_close",
        "长期",
        "短期",
    ]
    cols_to_drop = [c for c in cols_to_drop if c and c in df_ext.columns]
    df_clean = df_ext.drop(columns=cols_to_drop, errors="ignore")

    return df_clean


def _read_parquet_safe(name: str, date_str: str) -> pd.DataFrame:
    fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"{name}_{date_str}.parquet"
    if fp.exists():
        return pd.read_parquet(fp)
    return pd.DataFrame()


def load_tushare_data(date_str: str) -> pd.DataFrame:
    """加载单日 Tushare 宽表特征。"""
    df_daily = _read_parquet_safe("daily", date_str)
    if df_daily.empty:
        return pd.DataFrame()

    df_basic = _read_parquet_safe("daily_basic", date_str)
    df_factor = _read_parquet_safe("stk_factor", date_str)
    df_pro = _read_parquet_safe("stk_factor_pro", date_str)

    df_features = df_daily.copy()
    for df_other in [df_basic, df_factor, df_pro]:
        if not df_other.empty:
            df_other = df_other.copy()
            df_other["ts_code"] = df_other["ts_code"].astype(str)
            # 避免重复列
            cols_to_use = df_other.columns.difference(df_features.columns).tolist()
            if "ts_code" not in cols_to_use:
                cols_to_use.append("ts_code")
            if "trade_date" in df_other.columns and "trade_date" not in cols_to_use:
                cols_to_use.append("trade_date")

            df_features = pd.merge(
                df_features,
                df_other[cols_to_use],
                on=["ts_code", "trade_date"],
                how="left",
            )

    return df_features


def load_dataset(source_type: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    加载指定日期范围的数据集。

    source_type: 'excel_only' | 'tushare_only' | 'merged'
    """
    dates = get_available_dates(start_date, end_date)
    print(f"Found {len(dates)} trading days from {start_date} to {end_date}")

    all_data: List[pd.DataFrame] = []
    for date_str in dates:
        print(f"  Loading {date_str}...", end=" ")

        if source_type == "excel_only":
            df = load_excel_data(date_str)
        elif source_type == "tushare_only":
            # Tushare-only 训练仍然需要 Excel 提供目标 total_score
            df_excel = load_excel_data(date_str)
            if df_excel.empty:
                print("✖ Excel data missing (target)")
                continue
            df_tushare = load_tushare_data(date_str)
            if df_tushare.empty:
                print("✖ Tushare data missing")
                continue
            df = pd.merge(
                df_excel[["ts_code", "trade_date", "total_score"]],
                df_tushare,
                on=["ts_code", "trade_date"],
                how="inner",
            )
        elif source_type == "merged":
            # 预留：Excel 特征 + Tushare 特征
            df = pd.DataFrame()
        else:
            raise ValueError(f"Unknown source_type: {source_type}")

        if not df.empty:
            print(f"✔ {len(df)} rows")
            all_data.append(df)
        else:
            print("✖ Failed or Empty")

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)

