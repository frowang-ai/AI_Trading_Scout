from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

import pandas as pd
import requests


ROLL_LIST_URL = "https://m.cls.cn/v1/roll/get_roll_list"
DEFAULT_APP = "CailianpressWap"
DEFAULT_SV = "8.4.4"
DEFAULT_RN = 20
REQUEST_TIMEOUT_SECONDS = 15


def sha1_encrypt(input_string: str) -> str:
    sha1 = hashlib.sha1()
    sha1.update(input_string.encode("utf-8"))
    return sha1.hexdigest()


def md5_encrypt(input_string: str) -> str:
    md5 = hashlib.md5()
    md5.update(input_string.encode("utf-8"))
    return md5.hexdigest()


def get_sign(params: dict[str, Any]) -> str:
    sorted_params = sorted(params.items(), key=lambda item: item[0])
    param_str = "&".join([f"{key}={value}" for key, value in sorted_params])
    return md5_encrypt(sha1_encrypt(param_str))


def normalize_stock_code(code: str) -> str:
    normalized = str(code).replace("sz", "").replace("sh", "")
    if normalized.startswith(("0", "3")):
        return f"{normalized}.SZ"
    if normalized.startswith("6"):
        return f"{normalized}.SH"
    return normalized


def _parse_time_to_timestamp(value: str) -> int:
    try:
        return int(datetime.strptime(value, "%Y-%m-%d %H:%M:%S").timestamp())
    except ValueError as exc:
        raise ValueError(f"时间格式必须是 YYYY-MM-DD HH:MM:SS：{value}") from exc


def _request_roll_page(session: requests.Session, last_time: int, category: str | None = None) -> pd.DataFrame:
    params: dict[str, Any] = {
        "refresh_type": "1",
        "rn": str(DEFAULT_RN),
        "last_time": last_time,
        "app": DEFAULT_APP,
        "sv": DEFAULT_SV,
    }
    if category:
        params["category"] = category

    params["sign"] = get_sign(params)

    try:
        response = session.get(ROLL_LIST_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data_json = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"请求财联社电报接口失败：{exc}") from exc
    except ValueError as exc:
        raise RuntimeError("财联社电报接口返回内容不是合法 JSON") from exc

    roll_data = data_json.get("data", {}).get("roll_data", [])
    if not roll_data:
        return pd.DataFrame()
    return pd.DataFrame(roll_data)


def _stock_names(stock_list: list[dict[str, Any]]) -> str:
    return ",".join([item.get("name", "") for item in stock_list if item.get("name")])


def _stock_codes(stock_list: list[dict[str, Any]]) -> str:
    return ",".join(
        [normalize_stock_code(item.get("StockID", "")) for item in stock_list if item.get("StockID")]
    )


def normalize_roll_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df.empty:
        return pd.DataFrame(columns=["标题", "内容", "发布时间", "引用来源", "股票名称", "股票代码", "md5"])

    required_columns = ["title", "content", "ctime", "assocArticleUrl", "stock_list", "sort_score"]
    missing_columns = [column for column in required_columns if column not in raw_df.columns]
    if missing_columns:
        raise ValueError(f"财联社接口返回字段缺失：{missing_columns}")

    df = raw_df.copy()
    if "is_ad" in df.columns:
        df = df[df["is_ad"] == 0]

    df = df.drop_duplicates(subset=["content"])
    df = df[required_columns]
    df["stock_list"] = df["stock_list"].apply(lambda value: value if isinstance(value, list) else [])
    df["股票名称"] = df["stock_list"].apply(_stock_names)
    df["股票代码"] = df["stock_list"].apply(_stock_codes)
    df["md5"] = df["content"].fillna("").apply(md5_encrypt)
    df["ctime"] = pd.to_datetime(df["ctime"], unit="s", utc=True).dt.tz_convert("Asia/Shanghai")

    df = df[["title", "content", "ctime", "assocArticleUrl", "股票名称", "股票代码", "md5"]]
    df.columns = ["标题", "内容", "发布时间", "引用来源", "股票名称", "股票代码", "md5"]
    df["发布时间"] = pd.to_datetime(df["发布时间"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df.sort_values(["发布时间"], inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df


def fetch_cls_telegraph(start_time: str, end_time: str, category: str | None = None) -> pd.DataFrame:
    """Fetch CLS telegraph items between start_time and end_time.

    Times must use ``YYYY-MM-DD HH:MM:SS``. The upstream endpoint pages backward
    from ``end_time`` by `sort_score`; this function keeps fetching until the
    oldest page item is older than ``start_time``.
    """
    start_timestamp = _parse_time_to_timestamp(start_time)
    end_timestamp = _parse_time_to_timestamp(end_time)
    if end_timestamp <= start_timestamp:
        raise ValueError(f"end_time 必须晚于 start_time：start={start_time}, end={end_time}")

    session = requests.Session()
    temp_df = _request_roll_page(session, end_timestamp, category=category)
    if temp_df.empty:
        raise RuntimeError(f"财联社电报接口在截止时间附近未返回数据：{end_time}")

    frames = [temp_df]
    next_time = int(temp_df["sort_score"].values[-1])

    while next_time > start_timestamp:
        print(f"采集到的时间点={datetime.fromtimestamp(next_time)}")
        temp_df = _request_roll_page(session, next_time, category=category)
        if temp_df.empty:
            raise RuntimeError(f"财联社电报翻页返回空数据，last_time={next_time}")
        frames.append(temp_df)
        next_time = int(temp_df["sort_score"].values[-1])

    raw_df = pd.concat(frames, ignore_index=True)
    normalized = normalize_roll_data(raw_df)
    return normalized[normalized["发布时间"] >= start_time].reset_index(drop=True)


class ClsTelegraphFetcher:
    """Compatibility wrapper around the CLS telegraph fetch function."""

    sha1_encrypt = staticmethod(sha1_encrypt)
    md5_encrypt = staticmethod(md5_encrypt)
    get_sign = staticmethod(get_sign)
    modify_code = staticmethod(normalize_stock_code)
    stock_telegraph_cls = staticmethod(fetch_cls_telegraph)


class cls(ClsTelegraphFetcher):
    """Backward-compatible alias for the original `cls2.py` class name."""
