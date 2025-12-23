"""
每日执行的主脚本，串联 Stage 1-4。

当前重点实现 Step 1（Tushare 数据加载 + 模型打分 + Top 列表固化）。
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from production.config import TOP_N
from production.utils.data_fetcher import fetch_daily_data
from production.utils.scorer import (
    calculate_scores,
    get_top_n,
    save_full_scores,
    save_merged_with_excel,
    save_top_list_json,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Daily Production Pipeline (Step1: Tushare Scoring)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="目标交易日，格式 YYYYMMDD；缺省为今天。",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=TOP_N,
        help=f"输出 Top N 股票，默认与配置 TOP_N 一致（当前为 {TOP_N}）。",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    print("==== Daily Production Pipeline (Step1: Scoring) ====")

    # Stage 1: Data Ingestion
    date_str, df_tushare, df_excel = fetch_daily_data(args.date)

    # Stage 2: Scoring
    df_scores = calculate_scores(df_tushare)
    full_csv_path = save_full_scores(date_str, df_scores)

    df_top = get_top_n(df_scores, n=args.top_n)
    top_json_path = save_top_list_json(date_str, df_top)

    merged_path = save_merged_with_excel(date_str, df_scores, df_excel)

    print("\n==== Step1 Summary ====")
    print(f"日期: {date_str}")
    print(f"全量评分表: {full_csv_path}")
    print(f"Top{args.top_n} JSON: {top_json_path}")
    if merged_path is not None:
        print(f"预测分数 + Excel 真值合并: {merged_path}")
    else:
        print("预测分数 + Excel 真值合并: 未生成（可能缺少 Excel 或 total_score 列）。")

    print("Step1 完成，后续 Stage 3/4 将在后面迭代中接入。")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
