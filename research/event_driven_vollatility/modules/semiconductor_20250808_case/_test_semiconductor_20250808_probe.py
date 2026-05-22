from __future__ import annotations

from pathlib import Path

import pandas as pd


CURRENT_DIR = Path(__file__).parent.resolve()
RESEARCH_DIR = CURRENT_DIR.parents[1].resolve()
PROJECT_ROOT = CURRENT_DIR.parents[3].resolve()
OUTPUT_DIR = CURRENT_DIR / "outputs"

CLS_PARQUET = PROJECT_ROOT / "data" / "processed" / "cls_telegraph" / "cls_telegraph_2014_20260521.parquet"
DAILY_DIR = PROJECT_ROOT / "data" / "raw" / "daily" / "2025"

CASE_START = "2025-08-08"
CASE_END = "2025-10-10"
PRE_START = "2025-07-25"

NEWS_KEYWORDS = [
    "半导体",
    "芯片",
    "集成电路",
    "晶圆",
    "封测",
    "光刻",
    "存储",
    "国产替代",
    "中芯国际",
    "寒武纪",
    "北方华创",
    "海光信息",
    "华虹",
    "兆易创新",
    "韦尔股份",
    "中微公司",
]

INDUSTRY_KEYWORDS = ["半导体", "芯片", "集成电路"]


def require_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")


def contains_any(series: pd.Series, keywords: list[str]) -> pd.Series:
    text = series.fillna("").astype(str)
    mask = pd.Series(False, index=series.index)
    for keyword in keywords:
        mask = mask | text.str.contains(keyword, regex=False, na=False)
    return mask


def load_news() -> pd.DataFrame:
    require_path(CLS_PARQUET)
    df = pd.read_parquet(CLS_PARQUET, columns=["title", "content", "publish_time", "stock_name", "stock_code"])
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    start = pd.Timestamp(PRE_START)
    end = pd.Timestamp(CASE_END) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df = df[(df["publish_time"] >= start) & (df["publish_time"] <= end)].copy()
    combined_text = (
        df["title"].fillna("")
        + " "
        + df["content"].fillna("")
        + " "
        + df["stock_name"].fillna("")
        + " "
        + df["stock_code"].fillna("")
    )
    df["is_semiconductor_news"] = contains_any(combined_text, NEWS_KEYWORDS)
    df["date"] = df["publish_time"].dt.strftime("%Y-%m-%d")
    return df


def latest_stock_basic() -> pd.DataFrame:
    paths = sorted(DAILY_DIR.glob("stock_basic_*.parquet"))
    if not paths:
        raise FileNotFoundError(f"未找到 stock_basic Parquet：{DAILY_DIR}")
    df = pd.read_parquet(paths[-1])
    text = df[["name", "industry"]].fillna("").astype(str).agg(" ".join, axis=1)
    df["is_semiconductor_stock"] = contains_any(text, INDUSTRY_KEYWORDS)
    return df


def find_local_board_candidates() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for pattern in [
        "ths_index_*.parquet",
        "dc_index_*.parquet",
        "index_classify_L*.parquet",
        "ci_index_dim_*.parquet",
    ]:
        paths = sorted(DAILY_DIR.glob(pattern))
        if not paths:
            continue
        path = paths[-1]
        df = pd.read_parquet(path)
        text_columns = [
            column
            for column in df.columns
            if df[column].dtype == "object" or str(df[column].dtype).startswith("string")
        ]
        if not text_columns:
            continue
        text = df[text_columns].fillna("").astype(str).agg(" ".join, axis=1)
        hits = df[contains_any(text, NEWS_KEYWORDS)]
        for _, row in hits.head(100).iterrows():
            rows.append(
                {
                    "source_file": path.name,
                    "code": row.get("ts_code", row.get("index_code", "")),
                    "name": row.get("name", row.get("industry_name", "")),
                    "matched_text": " ".join([str(row.get(column, "")) for column in text_columns]),
                }
            )
    return pd.DataFrame(rows)


def find_local_etf_candidates(stock_basic: pd.DataFrame) -> pd.DataFrame:
    # 本地 stock_basic 是股票列表，不含 ETF；这里显式输出诊断，后续可用 Tushare etf_basic/fund_daily 补。
    text = stock_basic[["ts_code", "name", "industry"]].fillna("").astype(str).agg(" ".join, axis=1)
    hits = stock_basic[contains_any(text, ["ETF", "半导体ETF", "芯片ETF"])]
    return hits[["ts_code", "name", "industry"]].copy()


def iter_trade_dates() -> list[str]:
    paths = sorted(DAILY_DIR.glob("daily_*.parquet"))
    dates: list[str] = []
    start = pd.Timestamp(PRE_START)
    end = pd.Timestamp(CASE_END)
    for path in paths:
        date_text = path.stem.replace("daily_", "")
        date = pd.to_datetime(date_text, format="%Y%m%d", errors="coerce")
        if pd.notna(date) and start <= date <= end:
            dates.append(date_text)
    return dates


def load_daily_panel(stock_pool: set[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for trade_date in iter_trade_dates():
        path = DAILY_DIR / f"daily_{trade_date}.parquet"
        df = pd.read_parquet(path, columns=["ts_code", "trade_date", "close", "pct_chg", "amount"])
        df["is_semiconductor_stock"] = df["ts_code"].isin(stock_pool)
        frames.append(df)
    if not frames:
        raise RuntimeError(f"未找到 {PRE_START} 到 {CASE_END} 的 daily 数据")
    return pd.concat(frames, ignore_index=True)


def build_news_daily(news: pd.DataFrame) -> pd.DataFrame:
    all_daily = news.groupby("date").size().rename("all_news_count")
    semi_daily = news[news["is_semiconductor_news"]].groupby("date").size().rename("semiconductor_news_count")
    daily = pd.concat([all_daily, semi_daily], axis=1).fillna(0).reset_index()
    daily["semiconductor_news_share"] = daily["semiconductor_news_count"] / daily["all_news_count"]
    return daily


def build_basket_daily(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for trade_date, group in panel.groupby("trade_date"):
        semi = group[group["is_semiconductor_stock"]]
        market = group
        rows.append(
            {
                "trade_date": trade_date,
                "semiconductor_stock_count": len(semi),
                "market_stock_count": len(market),
                "semi_equal_weight_pct_chg": semi["pct_chg"].mean(),
                "market_equal_weight_pct_chg": market["pct_chg"].mean(),
                "semi_amount": semi["amount"].sum(),
                "market_amount": market["amount"].sum(),
            }
        )
    daily = pd.DataFrame(rows).sort_values("trade_date").reset_index(drop=True)
    daily["semi_cum_return"] = (1 + daily["semi_equal_weight_pct_chg"].fillna(0) / 100).cumprod() - 1
    daily["market_cum_return"] = (1 + daily["market_equal_weight_pct_chg"].fillna(0) / 100).cumprod() - 1
    daily["semi_excess_cum_return"] = daily["semi_cum_return"] - daily["market_cum_return"]
    daily["semi_amount_share"] = daily["semi_amount"] / daily["market_amount"]
    return daily


def build_top_stocks(panel: pd.DataFrame, stock_basic: pd.DataFrame) -> pd.DataFrame:
    case_panel = panel[
        (panel["trade_date"] >= CASE_START.replace("-", ""))
        & (panel["trade_date"] <= CASE_END.replace("-", ""))
        & panel["is_semiconductor_stock"]
    ].copy()
    returns = (
        case_panel.groupby("ts_code")["pct_chg"]
        .apply(lambda value: (1 + value.fillna(0) / 100).prod() - 1)
        .rename("case_cum_return")
        .reset_index()
    )
    meta = stock_basic[["ts_code", "name", "industry"]]
    return returns.merge(meta, on="ts_code", how="left").sort_values("case_cum_return", ascending=False)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    news = load_news()
    stock_basic = latest_stock_basic()
    semiconductor_stocks = set(stock_basic.loc[stock_basic["is_semiconductor_stock"], "ts_code"].astype(str))
    panel = load_daily_panel(semiconductor_stocks)

    news_daily = build_news_daily(news)
    basket_daily = build_basket_daily(panel)
    top_stocks = build_top_stocks(panel, stock_basic)
    board_candidates = find_local_board_candidates()
    etf_candidates = find_local_etf_candidates(stock_basic)

    case_basket = basket_daily[
        (basket_daily["trade_date"] >= CASE_START.replace("-", ""))
        & (basket_daily["trade_date"] <= CASE_END.replace("-", ""))
    ]
    summary = pd.DataFrame(
        [
            {
                "case_start": CASE_START,
                "case_end": CASE_END,
                "pre_start": PRE_START,
                "news_rows": len(news),
                "semiconductor_news_rows": int(news["is_semiconductor_news"].sum()),
                "semiconductor_stock_count": len(semiconductor_stocks),
                "trade_days": len(case_basket),
                "case_semi_cum_return": case_basket["semi_cum_return"].iloc[-1] if not case_basket.empty else pd.NA,
                "case_market_cum_return": case_basket["market_cum_return"].iloc[-1] if not case_basket.empty else pd.NA,
                "case_semi_excess_cum_return": case_basket["semi_excess_cum_return"].iloc[-1] if not case_basket.empty else pd.NA,
            }
        ]
    )

    news_daily.to_csv(OUTPUT_DIR / "_test_semiconductor_news_daily.csv", index=False, encoding="utf-8-sig")
    basket_daily.to_csv(OUTPUT_DIR / "_test_semiconductor_basket_daily.csv", index=False, encoding="utf-8-sig")
    top_stocks.to_csv(OUTPUT_DIR / "_test_semiconductor_top_stocks.csv", index=False, encoding="utf-8-sig")
    board_candidates.to_csv(
        OUTPUT_DIR / "_test_semiconductor_local_board_candidates.csv",
        index=False,
        encoding="utf-8-sig",
    )
    etf_candidates.to_csv(
        OUTPUT_DIR / "_test_semiconductor_local_etf_candidates.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary.to_csv(OUTPUT_DIR / "_test_semiconductor_case_summary.csv", index=False, encoding="utf-8-sig")

    print(summary.to_string(index=False))
    print("\nnews daily around event:")
    print(news_daily[(news_daily["date"] >= "2025-08-01") & (news_daily["date"] <= "2025-08-15")].to_string(index=False))
    print("\ntop semiconductor stocks:")
    print(top_stocks.head(20).to_string(index=False))
    print("\nlocal board candidates:")
    print(board_candidates.head(20).to_string(index=False))
    print("\nlocal ETF candidates in stock_basic:")
    print(etf_candidates.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
