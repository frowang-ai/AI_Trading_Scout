"""Small, explicit client for Eastmoney's web quote endpoints.

The endpoints are undocumented web contracts.  Missing fields are therefore
reported as unavailable instead of being filled from another data source.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests


CHINA_TZ = ZoneInfo("Asia/Shanghai")
BASE_URL = "https://push2.eastmoney.com/api/qt/stock"
UT = "fa5fd1943c7b386f172d6893dbfba10b"
QUOTE_FIELDS = (
    "f57,f58,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f60,f86,"
    "f19,f20,f17,f18,f15,f16,f13,f14,f11,f12,"
    "f39,f40,f37,f38,f35,f36,f33,f34,f31,f32"
)
BID_FIELDS = (("f19", "f20"), ("f17", "f18"), ("f15", "f16"), ("f13", "f14"), ("f11", "f12"))
ASK_FIELDS = (("f39", "f40"), ("f37", "f38"), ("f35", "f36"), ("f33", "f34"), ("f31", "f32"))


class EastmoneyError(RuntimeError):
    """Raised when an Eastmoney response cannot satisfy its declared contract."""


def to_secid(symbol: str) -> str:
    """Convert common A-share symbols to Eastmoney's ``market.code`` form."""
    value = symbol.strip().upper()
    if "." in value and value.split(".", 1)[0].isdigit():
        market, code = value.split(".", 1)
        if market in {"0", "1"} and code.isdigit() and len(code) == 6:
            return value
    if value.startswith(("SH", "SZ", "BJ")):
        prefix, code = value[:2], value[2:]
    elif value.endswith((".SH", ".SZ", ".BJ")):
        code, prefix = value.split(".")
    else:
        code = value
        prefix = "SH" if code.startswith(("5", "6", "9")) else "SZ"
    if not (code.isdigit() and len(code) == 6):
        raise ValueError(f"无法识别股票代码: {symbol!r}")
    return f"{1 if prefix == 'SH' else 0}.{code}"


def _float(value: Any) -> float | None:
    if value in (None, "", "-"):
        return None
    return float(value)


def _int(value: Any) -> int | None:
    if value in (None, "", "-"):
        return None
    return int(float(value))


def _levels(data: dict[str, Any], fields: tuple[tuple[str, str], ...]) -> list[dict[str, int | float]]:
    levels: list[dict[str, int | float]] = []
    for level, (price_key, volume_key) in enumerate(fields, start=1):
        price = _float(data.get(price_key))
        volume = _int(data.get(volume_key))
        if price is None or volume is None:
            return []
        levels.append({"level": level, "price": price, "volume_lots": volume})
    return levels


class EastmoneyClient:
    """Read snapshots, one-minute bars and recent transaction aggregates."""

    def __init__(self, timeout: float = 10.0, session: requests.Session | None = None):
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"
                ),
            }
        )

    def _get(self, path: str, params: dict[str, str | int]) -> dict[str, Any]:
        query = {"ut": UT, "_": int(datetime.now().timestamp() * 1000), **params}
        response = self.session.get(f"{BASE_URL}/{path}", params=query, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if payload.get("rc") != 0 or not isinstance(payload.get("data"), dict):
            raise EastmoneyError(
                f"东方财富接口响应无有效 data: path={path}, rc={payload.get('rc')}, "
                f"message={payload.get('message')}"
            )
        return payload["data"]

    def quote(self, symbol: str) -> dict[str, Any]:
        fetched_at = datetime.now(CHINA_TZ)
        data = self._get(
            "get",
            {
                "secid": to_secid(symbol),
                "invt": 2,
                "fltt": 2,
                "wbp2u": "|0|0|0|web",
                "dect": 1,
                "fields": QUOTE_FIELDS,
            },
        )
        bids = _levels(data, BID_FIELDS)
        asks = _levels(data, ASK_FIELDS)
        update_epoch = _int(data.get("f86"))
        source_time = (
            datetime.fromtimestamp(update_epoch, CHINA_TZ).isoformat()
            if update_epoch is not None
            else None
        )
        return {
            "source": "eastmoney_web",
            "secid": to_secid(symbol),
            "code": data.get("f57"),
            "name": data.get("f58"),
            "source_time": source_time,
            "fetched_at": fetched_at.isoformat(),
            "price": _float(data.get("f43")),
            "open": _float(data.get("f46")),
            "high": _float(data.get("f44")),
            "low": _float(data.get("f45")),
            "pre_close": _float(data.get("f60")),
            "volume_lots": _int(data.get("f47")),
            "amount_cny": _float(data.get("f48")),
            "outer_volume_lots": _int(data.get("f49")),
            "volume_ratio": _float(data.get("f50")),
            "limit_up": _float(data.get("f51")),
            "limit_down": _float(data.get("f52")),
            "order_book_available": len(bids) == 5 and len(asks) == 5,
            "bids": bids,
            "asks": asks,
        }

    def intraday_minutes(self, symbol: str) -> list[dict[str, Any]]:
        data = self._get(
            "trends2/get",
            {
                "secid": to_secid(symbol),
                "ndays": 1,
                "iscr": 0,
                "iscca": 0,
                "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
            },
        )
        rows: list[dict[str, Any]] = []
        for raw in data.get("trends", []):
            values = raw.split(",")
            if len(values) != 8:
                raise EastmoneyError(f"分时字段数量异常: {raw!r}")
            rows.append(
                {
                    "trade_time": values[0],
                    "open": float(values[1]),
                    "close": float(values[2]),
                    "high": float(values[3]),
                    "low": float(values[4]),
                    "volume_lots": int(values[5]),
                    "amount_cny": float(values[6]),
                    "average_price": float(values[7]),
                }
            )
        return rows

    def recent_trades(self, symbol: str, limit: int = 20) -> list[dict[str, Any]]:
        if not 1 <= limit <= 10_000:
            raise ValueError("limit 必须在 1 到 10000 之间")
        data = self._get(
            "details/get",
            {
                "secid": to_secid(symbol),
                "pos": -limit,
                "iscca": 1,
                "invt": 2,
                "fltt": 2,
                "fields1": "f1,f2,f3,f4,f5",
                "fields2": "f51,f52,f53,f54,f55",
            },
        )
        rows: list[dict[str, Any]] = []
        for raw in data.get("details", []):
            values = raw.split(",")
            if len(values) < 4:
                raise EastmoneyError(f"分笔字段数量异常: {raw!r}")
            volume_lots = int(values[2])
            price = float(values[1])
            rows.append(
                {
                    "trade_time": values[0],
                    "price": price,
                    "volume_lots": volume_lots,
                    "trade_count": int(values[3]),
                    "side_code": int(values[4]) if len(values) >= 5 else None,
                    "estimated_amount_cny": price * volume_lots * 100,
                }
            )
        return rows
