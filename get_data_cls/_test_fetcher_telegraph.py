from datetime import datetime, timedelta

from fetcher_telegraph import fetch_cls_telegraph, get_sign, normalize_stock_code


def _assert_offline_helpers() -> None:
    sign = get_sign(
        {
            "refresh_type": "1",
            "rn": "20",
            "last_time": 1739203200,
            "app": "CailianpressWap",
            "sv": "8.4.4",
        }
    )
    assert len(sign) == 32
    assert normalize_stock_code("sz300634") == "300634.SZ"
    assert normalize_stock_code("sh600519") == "600519.SH"


def main() -> None:
    _assert_offline_helpers()

    end_dt = datetime.now().replace(microsecond=0)
    start_dt = end_dt - timedelta(hours=2)
    start_time = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    df = fetch_cls_telegraph(start_time, end_time)
    print(f"probe window: {start_time} -> {end_time}")
    print(f"rows: {len(df)}")
    print(df.head(10).to_string(index=False))

    if df.empty:
        raise RuntimeError("探针窗口内没有抓到财联社电报数据")


if __name__ == "__main__":
    main()
