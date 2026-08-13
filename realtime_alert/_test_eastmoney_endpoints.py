#!/usr/bin/env python3
"""Lightweight probe for Eastmoney quote endpoints used by realtime_alert.

Only prints response metadata and a handful of rows.  It does not persist market
data, so it is safe to run while discovering the upstream response contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


CURRENT_DIR = Path(__file__).parent.resolve()
REPORT_PATH = CURRENT_DIR / "_test_eastmoney_endpoints.json"
BASE_URL = "https://push2.eastmoney.com/api/qt/stock"
SECID = "0.300058"
UT = "fa5fd1943c7b386f172d6893dbfba10b"
HEADERS = {
    "Referer": "https://quote.eastmoney.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"
    ),
}


def request_json(path: str, params: dict[str, str | int]) -> dict[str, Any]:
    response = requests.get(
        f"{BASE_URL}/{path}",
        params=params,
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def summarize(payload: dict[str, Any], sample_key: str | None = None) -> dict[str, Any]:
    data = payload.get("data")
    result: dict[str, Any] = {
        "rc": payload.get("rc"),
        "rt": payload.get("rt"),
        "message": payload.get("message"),
        "data_type": type(data).__name__,
    }
    if isinstance(data, dict):
        result["data_keys"] = sorted(data)
        if sample_key:
            rows = data.get(sample_key)
            result["row_count"] = len(rows) if isinstance(rows, list) else None
            result["sample"] = rows[:3] if isinstance(rows, list) else rows
        else:
            result["sample"] = data
    return result


def main() -> None:
    quote = request_json(
        "get",
        {
            "secid": SECID,
            "ut": UT,
            "invt": 2,
            "fltt": 1,
            "wbp2u": "|0|0|0|web",
            "dect": 1,
            "fields": (
                "f57,f58,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f60,f86,"
                "f19,f20,f17,f18,f15,f16,f13,f14,f11,f12,"
                "f31,f32,f33,f34,f35,f36,f37,f38,f39,f40"
            ),
        },
    )
    trends = request_json(
        "trends2/get",
        {
            "secid": SECID,
            "ndays": 1,
            "iscr": 0,
            "iscca": 0,
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
        },
    )
    details = request_json(
        "details/get",
        {
            "secid": SECID,
            "pos": -20,
            "iscca": 1,
            "invt": 2,
            "fields1": "f1,f2,f3,f4,f5",
            "fields2": "f51,f52,f53,f54,f55",
        },
    )

    report = {
        "quote": summarize(quote),
        "trends": summarize(trends, "trends"),
        "details": summarize(details, "details"),
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"report={REPORT_PATH}")


if __name__ == "__main__":
    main()
