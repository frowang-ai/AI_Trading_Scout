#!/usr/bin/env python3
"""Offline contract tests for the Eastmoney web client."""

from __future__ import annotations

import math
from typing import Any

from realtime_alert.eastmoney import EastmoneyClient, to_secid


class FakeResponse:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeSession:
    def __init__(self, payloads: list[dict[str, Any]]):
        self.payloads = iter(payloads)
        self.headers: dict[str, str] = {}

    def get(self, *_args: Any, **_kwargs: Any) -> FakeResponse:
        return FakeResponse(next(self.payloads))


def envelope(data: dict[str, Any]) -> dict[str, Any]:
    return {"rc": 0, "data": data}


def test_symbol_conversion() -> None:
    assert to_secid("300058.SZ") == "0.300058"
    assert to_secid("sz300058") == "0.300058"
    assert to_secid("600519.SH") == "1.600519"


def test_quote_explicitly_marks_missing_order_book() -> None:
    client = EastmoneyClient(session=FakeSession([envelope({"f57": "300058", "f58": "蓝色光标", "f43": 15.72})]))
    quote = client.quote("300058.SZ")
    assert quote["price"] == 15.72
    assert quote["order_book_available"] is False
    assert quote["bids"] == []
    assert quote["asks"] == []


def test_quote_parses_five_levels() -> None:
    data: dict[str, Any] = {"f57": "300058", "f58": "蓝色光标", "f43": 15.72}
    for index, (price_key, volume_key) in enumerate(
        (("f19", "f20"), ("f17", "f18"), ("f15", "f16"), ("f13", "f14"), ("f11", "f12")), start=1
    ):
        data[price_key], data[volume_key] = 15.72 - index / 100, index * 100
    for index, (price_key, volume_key) in enumerate(
        (("f39", "f40"), ("f37", "f38"), ("f35", "f36"), ("f33", "f34"), ("f31", "f32")), start=1
    ):
        data[price_key], data[volume_key] = 15.72 + index / 100, index * 200
    quote = EastmoneyClient(session=FakeSession([envelope(data)])).quote("300058")
    assert quote["order_book_available"] is True
    assert quote["bids"][0]["level"] == 1
    assert math.isclose(quote["bids"][0]["price"], 15.71)
    assert quote["bids"][0]["volume_lots"] == 100
    assert quote["asks"][4]["level"] == 5
    assert math.isclose(quote["asks"][4]["price"], 15.77)
    assert quote["asks"][4]["volume_lots"] == 1000


def test_minute_and_trade_parsing() -> None:
    session = FakeSession(
        [
            envelope({"trends": ["2026-08-13 09:31,16.10,16.12,16.36,16.08,195037,316060640.00,16.152"]}),
            envelope({"details": ["11:29:03,15.73,113,15,1"]}),
        ]
    )
    client = EastmoneyClient(session=session)
    minute = client.intraday_minutes("300058")[0]
    trade = client.recent_trades("300058", 1)[0]
    assert minute["close"] == 16.12
    assert minute["volume_lots"] == 195037
    assert trade["trade_count"] == 15
    assert trade["estimated_amount_cny"] == 177_749.0


def main() -> None:
    test_symbol_conversion()
    test_quote_explicitly_marks_missing_order_book()
    test_quote_parses_five_levels()
    test_minute_and_trade_parsing()
    print("4 tests passed")


if __name__ == "__main__":
    main()
