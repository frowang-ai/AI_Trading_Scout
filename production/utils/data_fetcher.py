"""
封装 Stage 1: 数据获取

职责：
- 根据指定日期（默认今天）加载当日 Tushare 宽表特征
- 尝试加载对应的 Excel “真值总分”（若存在）
- 在核心接口数据缺失时尽早失败并给出清晰错误信息
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

import pandas as pd

from get_data_tushare.config import DATA_ROOT

from production.config import DATE_FORMAT, PROJECT_ROOT


current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()

# 复用 demo1 中 Excel 位置约定（仅作为临时模块使用）
EXCEL_DIR_ROOT = PROJECT_ROOT / "刘丰硕的代码"


def _resolve_target_date(date_str: str | None = None) -> str:
    """将可选日期字符串解析为标准交易日期格式 YYYYMMDD。"""
    if date_str:
        date_str = date_str.strip()
        # 简单格式校验：长度必须为 8 且能被解析
        try:
            datetime.strptime(date_str, DATE_FORMAT)
        except ValueError as exc:
            raise ValueError(f"无效的日期格式: {date_str}，期望格式为 YYYYMMDD") from exc
        return date_str

    today = datetime.today()
    return today.strftime(DATE_FORMAT)


def _read_parquet_safe(name: str, date_str: str) -> pd.DataFrame:
    """
    从标准路径读取单日 Parquet 文件，如果不存在则返回空 DataFrame。

    约定路径：DATA_ROOT / 'raw' / 'daily' / 年份 / f'{name}_{date_str}.parquet'
    """
    fp = DATA_ROOT / "raw" / "daily" / date_str[:4] / f"{name}_{date_str}.parquet"
    if fp.exists():
        return pd.read_parquet(fp)
    return pd.DataFrame()


def load_tushare_features(date_str: str) -> pd.DataFrame:
    """
    加载单日 Tushare 宽表特征。

    若基础 daily 数据缺失，则直接报错终止；
    其他扩展表（daily_basic / stk_factor / stk_factor_pro）缺失则给出提示。
    """
    df_daily = _read_parquet_safe("daily", date_str)
    if df_daily.empty:
        raise FileNotFoundError(
            f"Tushare daily 数据缺失，无法继续运行：{date_str}，"
            f"预期路径前缀为 {DATA_ROOT / 'raw' / 'daily' / date_str[:4]}"
        )

    df_basic = _read_parquet_safe("daily_basic", date_str)
    df_factor = _read_parquet_safe("stk_factor", date_str)
    df_pro = _read_parquet_safe("stk_factor_pro", date_str)

    missing_parts = []
    if df_basic.empty:
        missing_parts.append("daily_basic")
    if df_factor.empty:
        missing_parts.append("stk_factor")
    if df_pro.empty:
        missing_parts.append("stk_factor_pro")
    if missing_parts:
        print(
            f"[警告] 部分 Tushare 扩展特征缺失（{date_str}）："
            + ", ".join(missing_parts)
        )

    df_features = df_daily.copy()
    for df_other in [df_basic, df_factor, df_pro]:
        if not df_other.empty:
            df_other = df_other.copy()
            if "ts_code" not in df_other.columns:
                continue
            df_other["ts_code"] = df_other["ts_code"].astype(str)

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


def _try_load_excel_truth(date_str: str) -> pd.DataFrame:
    """
    尝试加载当日 Excel 真值总分数据。

    若未找到对应 Excel 文件，则返回空 DataFrame，并打印提示；
    这不会阻止主流程运行。
    """
    # 为了兼容现有 demo1，遍历 Excel 根目录下的所有 xlsx 文件
    if not EXCEL_DIR_ROOT.exists():
        print(f"[提示] Excel 根目录不存在，跳过真值总分加载：{EXCEL_DIR_ROOT}")
        return pd.DataFrame()

    candidates = list(EXCEL_DIR_ROOT.rglob(f"{date_str}*.xlsx"))
    if not candidates:
        print(f"[提示] 未找到 {date_str} 对应的 Excel 真值文件，跳过合并。")
        return pd.DataFrame()

    excel_path = candidates[0]
    try:
        df_ext = pd.read_excel(excel_path)
    except Exception as exc:
        print(f"[警告] 读取 Excel 失败：{excel_path}，原因：{exc}")
        return pd.DataFrame()

    cols_map = {str(c): str(c) for c in df_ext.columns}

    def get_col(*names: str) -> str | None:
        for n in names:
            if n in cols_map:
                return n
        return None

    c_code = get_col("code2", "ts_code", "代码", "code")
    c_date = get_col("trade_date", "日期")
    c_score = get_col("总分", "total_score")

    if not c_code or not c_score:
        print(f"[警告] Excel 中缺失代码或总分列，文件：{excel_path.name}")
        return pd.DataFrame()

    base = df_ext[c_code].astype(str).str.strip()
    if not base.str.contains(r"\.").any():
        is_bjs = "bjs" in excel_path.stem.lower()
        suffix = base.str[0].map(
            lambda x: ".SH" if x == "6" else (".SZ" if not is_bjs else ".BJ")
        )
        df_ext["ts_code"] = base + suffix
    else:
        df_ext["ts_code"] = base

    df_ext["trade_date"] = date_str
    df_ext["total_score"] = pd.to_numeric(df_ext[c_score], errors="coerce")

    # 精简为后续合并所需的最小列
    keep_columns = ["ts_code", "trade_date", "total_score"]
    for col in (c_date,):
        if col and col in df_ext.columns and col not in keep_columns:
            keep_columns.append(col)

    return df_ext[keep_columns].copy()


def fetch_daily_data(
    date_str: str | None = None,
) -> Tuple[str, pd.DataFrame, pd.DataFrame]:
    """
    Step 1 入口：按指定日期加载当日所需数据。

    Args:
        date_str: 可选，形如 "YYYYMMDD" 的日期字符串；为 None 时使用“今天”。

    Returns:
        (resolved_date, df_tushare_features, df_excel_truth)

    Raises:
        FileNotFoundError: 当 Tushare daily 数据缺失时。
        ValueError: 日期格式非法时。
    """
    resolved_date = _resolve_target_date(date_str)
    print(f"[Step1] 目标交易日：{resolved_date}")

    df_tushare = load_tushare_features(resolved_date)
    print(
        f"[Step1] 已加载 Tushare 特征：{len(df_tushare)} 行，{len(df_tushare.columns)} 列"
    )

    df_excel = _try_load_excel_truth(resolved_date)
    if not df_excel.empty:
        print(f"[Step1] 已加载 Excel 真值总分：{len(df_excel)} 行")

    return resolved_date, df_tushare, df_excel
