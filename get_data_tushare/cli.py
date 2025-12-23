#!/usr/bin/env python3
"""
日线数据获取命令行工具。

使用示例:
    # ========== 历史回补 ==========
    # 从 2020 年至今回补基础日线数据（daily）
    python -m get_data_tushare.cli backfill --start 20200101
    
    # 指定时间段回补
    python -m get_data_tushare.cli backfill --start 20230101 --end 20231130
    
    # 回补指定接口（可多次使用 --api）
    python -m get_data_tushare.cli backfill --start 20240101 --api daily_basic --api adj_factor
    
    # 回补所有支持的股票日频接口
    python -m get_data_tushare.cli backfill --start 20240101 --all
    
    # ========== 每日更新 ==========
    # 更新昨日基础日线数据（daily）
    python -m get_data_tushare.cli update
    
    # 更新指定日期
    python -m get_data_tushare.cli update --date 20251217
    
    # 更新指定接口（可多次使用 --api）
    python -m get_data_tushare.cli update --api daily_basic --api moneyflow
    
    # 更新所有股票日频接口
    python -m get_data_tushare.cli update --all
    
    # ========== 行业概念数据更新 ==========
    # 更新中信行业指数维表（耗时：~30秒-1分钟）
    python -m get_data_tushare.cli update --ci-dim
    
    # 更新原始行业概念接口快照（耗时：3-5分钟，~1200次API调用）⭐ 推荐先执行
    python -m get_data_tushare.cli update --industry-raw
    
    # 更新股票-行业-概念聚合面板（耗时：<1秒，从快照构建，0次API调用）
    python -m get_data_tushare.cli update --industry-panel
    
    # 一次性更新所有行业概念数据（耗时：3-6分钟，已优化！）
    python -m get_data_tushare.cli update --extras-all
    
    # 区间回补行业概念数据（按交易日逐日更新）
    python -m get_data_tushare.cli update --start 20251101 --end 20251218 --industry-raw
    python -m get_data_tushare.cli update --start 20251101 --end 20251218 --industry-panel
    python -m get_data_tushare.cli update --start 20251101 --end 20251218 --extras-all
    
    # ========== 配置信息 ==========
    # 查看配置和已下载数据统计
    python -m get_data_tushare.cli info

注意:
    1. 运行前请确保已设置环境变量 TUSHARE_TOKEN
    2. --extras-all 已优化：从 20 分钟降至 3-6 分钟（API 调用减少 80%）
    3. 进度信息格式如 [ci-index-dim]、[industry-raw]、[panel-from-snapshot] 等
    4. industry-panel 依赖 industry-raw 快照，建议先运行 --industry-raw
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from .fetcher_daily import DailyFetcher, SUPPORTED_STOCK_DAILY_APIS
from .utils import get_yesterday


def setup_logging(verbose: bool = False) -> None:
    """配置日志输出。"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_backfill(args: argparse.Namespace) -> int:
    """执行历史数据回补。"""
    fetcher = DailyFetcher()
    
    end_date = args.end or get_yesterday()
    
    print(f"=" * 60)
    print(f"历史数据回补")
    print(f"时间范围: {args.start} - {end_date}")
    print(f"跳过已存在: {'是' if not args.force else '否'}")
    print(f"=" * 60)
    
    def progress(current: int, total: int, date_str: str) -> None:
        pct = current / total * 100
        print(f"[{current:4d}/{total:4d}] ({pct:5.1f}%) 处理: {date_str}")
    
    try:
        if args.api or getattr(args, "all", False):
            apis = list(args.api or [])
            if getattr(args, "all", False):
                apis = list(SUPPORTED_STOCK_DAILY_APIS)
            all_failed = 0
            for api_name in apis:
                print(f"\n接口: {api_name}")
                stats = fetcher.run_initialization_for_api(
                    api_name=api_name,
                    start_date=args.start,
                    end_date=end_date,
                    skip_existing=not args.force,
                    progress_callback=progress,
                )
                print(f"  总交易日: {stats['total']}")
                print(f"  成功下载: {stats['success']}")
                print(f"  跳过已有: {stats['skipped']}")
                print(f"  下载失败: {stats['failed']}")
                all_failed += stats["failed"]
            print(f"\n" + "=" * 60)
            print("回补完成！")
            print(f"=" * 60)
            return 0 if all_failed == 0 else 1
        else:
            stats = fetcher.run_initialization(
                start_date=args.start,
                end_date=end_date,
                skip_existing=not args.force,
                progress_callback=progress,
            )
            print(f"\n" + "=" * 60)
            print(f"回补完成！")
            print(f"  总交易日: {stats['total']}")
            print(f"  成功下载: {stats['success']}")
            print(f"  跳过已有: {stats['skipped']}")
            print(f"  下载失败: {stats['failed']}")
            print(f"=" * 60)
            return 0 if stats["failed"] == 0 else 1
        
    except KeyboardInterrupt:
        print("\n用户中断")
        return 130
    except Exception as e:
        logging.exception(f"回补失败: {e}")
        return 1


def cmd_update(args: argparse.Namespace) -> int:
    """执行每日更新。"""
    fetcher = DailyFetcher()
    
    # 检查是否使用区间模式
    if hasattr(args, 'start') and args.start:
        # 区间模式：获取交易日列表并逐日处理
        end_date = getattr(args, 'end', None) or get_yesterday()
        trade_dates = fetcher.fetch_trade_calendar(args.start, end_date)
        
        if not trade_dates:
            print(f"时间区间 {args.start} - {end_date} 内没有交易日")
            return 1
        
        print(f"=" * 60)
        print(f"区间更新")
        print(f"时间范围: {args.start} - {end_date}")
        print(f"交易日数: {len(trade_dates)}")
        print(f"跳过已存在: {'是' if not getattr(args, 'force', False) else '否'}")
        print(f"=" * 60)
        
        total_success = 0
        total_failed = 0
        total_skipped = 0
        
        try:
            for idx, date_str in enumerate(trade_dates, 1):
                pct = idx / len(trade_dates) * 100
                print(f"\n[{idx:4d}/{len(trade_dates):4d}] ({pct:5.1f}%) 处理: {date_str}")
                
                date_success = True
                
                # 处理标准 API
                if args.api or getattr(args, "all", False):
                    apis = list(args.api or [])
                    if getattr(args, "all", False):
                        apis = list(SUPPORTED_STOCK_DAILY_APIS)
                    for api_name in apis:
                        ok = fetcher.run_daily_update_for_api(api_name, date_str)
                        if ok:
                            print(f"  {api_name}: 成功")
                        else:
                            print(f"  {api_name}: 失败")
                            date_success = False
                
                # 处理行业概念相关数据
                if getattr(args, "extras_all", False) or getattr(args, "ci_dim", False):
                    try:
                        p = fetcher.save_ci_index_dim_to_raw(date_str, overwrite=getattr(args, "extras_force", False))
                        print(f"  ci_index_dim: 成功")
                    except Exception as e:
                        print(f"  ci_index_dim: 失败 ({e})")
                        date_success = False
                
                if getattr(args, "extras_all", False) or getattr(args, "industry_panel", False):
                    try:
                        p = fetcher.save_industry_concept_panel_to_raw(date_str, overwrite=getattr(args, "extras_force", False))
                        print(f"  industry_concept_panel: 成功")
                    except Exception as e:
                        print(f"  industry_concept_panel: 失败 ({e})")
                        date_success = False
                
                if getattr(args, "extras_all", False) or getattr(args, "industry_raw", False):
                    try:
                        paths = fetcher.save_raw_industry_concept(date_str, overwrite=getattr(args, "extras_force", False))
                        print(f"  industry_raw: 成功 ({', '.join(sorted(paths.keys()))})")
                    except Exception as e:
                        print(f"  industry_raw: 失败 ({e})")
                        date_success = False
                
                if date_success:
                    total_success += 1
                else:
                    total_failed += 1
            
            print(f"\n" + "=" * 60)
            print(f"区间更新完成！")
            print(f"  总交易日: {len(trade_dates)}")
            print(f"  成功更新: {total_success}")
            print(f"  更新失败: {total_failed}")
            print(f"=" * 60)
            
            return 0 if total_failed == 0 else 1
            
        except KeyboardInterrupt:
            print("\n用户中断")
            return 130
        except Exception as e:
            logging.exception(f"区间更新失败: {e}")
            return 1
    
    # 单日模式（原有逻辑）
    date_str = args.date or get_yesterday()
    
    print(f"每日更新: {date_str}")
    
    try:
        if args.api or getattr(args, "all", False) or getattr(args, "extras_all", False) or getattr(args, "ci_dim", False) or getattr(args, "industry_panel", False) or getattr(args, "industry_raw", False):
            apis = list(args.api or [])
            if getattr(args, "all", False):
                apis = list(SUPPORTED_STOCK_DAILY_APIS)
            all_success = True
            for api_name in apis:
                ok = fetcher.run_daily_update_for_api(api_name, date_str)
                print(f"{api_name}: {'成功' if ok else '失败'}")
                all_success = all_success and ok
            if getattr(args, "extras_all", False) or getattr(args, "ci_dim", False):
                try:
                    p = fetcher.save_ci_index_dim_to_raw(date_str, overwrite=getattr(args, "extras_force", False))
                    print(f"ci_index_dim: 成功 ({p})")
                except Exception as e:
                    print(f"ci_index_dim: 失败 ({e})")
                    all_success = False
            if getattr(args, "extras_all", False) or getattr(args, "industry_panel", False):
                try:
                    p = fetcher.save_industry_concept_panel_to_raw(date_str, overwrite=getattr(args, "extras_force", False))
                    print(f"industry_concept_panel: 成功 ({p})")
                except Exception as e:
                    print(f"industry_concept_panel: 失败 ({e})")
                    all_success = False
            if getattr(args, "extras_all", False) or getattr(args, "industry_raw", False):
                try:
                    paths = fetcher.save_raw_industry_concept(date_str, overwrite=getattr(args, "extras_force", False))
                    print(f"industry_raw: 成功 ({', '.join(sorted(paths.keys()))})")
                except Exception as e:
                    print(f"industry_raw: 失败 ({e})")
                    all_success = False
            return 0 if all_success else 1
        else:
            success = fetcher.run_daily_update(date_str)
            if success:
                print("更新成功！")
                return 0
            else:
                print("更新失败")
                return 1
            
    except Exception as e:
        logging.exception(f"更新失败: {e}")
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """显示配置信息。"""
    from .config import (
        DATA_ROOT,
        RAW_DAILY_DIR,
        PROJECT_ROOT,
        API_CALL_INTERVAL,
    )
    
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"数据根目录: {DATA_ROOT}")
    print(f"日线数据目录: {RAW_DAILY_DIR}")
    print(f"API 调用间隔: {API_CALL_INTERVAL}s")
    
    # 检查 Token
    try:
        from .config import get_tushare_token
        token = get_tushare_token()
        print(f"Tushare Token: {token[:8]}...{token[-4:]} (已配置)")
    except ValueError as e:
        print(f"Tushare Token: 未配置 ({e})")
    
    # 统计已下载文件
    if RAW_DAILY_DIR.exists():
        parquet_files = list(RAW_DAILY_DIR.rglob("*.parquet"))
        print(f"已下载文件数: {len(parquet_files)}")
        
        if parquet_files:
            dates = sorted([f.stem for f in parquet_files])
            print(f"数据范围: {dates[0]} - {dates[-1]}")
    else:
        print(f"数据目录不存在")
    
    return 0


def main() -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="Tushare 日线数据获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # backfill 子命令
    backfill_parser = subparsers.add_parser(
        "backfill",
        help="历史数据回补",
        description="从指定日期开始回补历史数据",
    )
    backfill_parser.add_argument(
        "--start", "-s",
        required=True,
        help="开始日期 (YYYYMMDD)",
    )
    backfill_parser.add_argument(
        "--end", "-e",
        default=None,
        help="结束日期 (YYYYMMDD)，默认昨日",
    )
    backfill_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="强制重新下载（不跳过已存在文件）",
    )
    backfill_parser.add_argument(
        "--api",
        action="append",
        choices=SUPPORTED_STOCK_DAILY_APIS,
        help="指定回补的接口，可多次使用（默认仅 daily）",
    )
    backfill_parser.add_argument(
        "--all",
        action="store_true",
        help="回补所有支持接口（默认仅 daily）",
    )
    backfill_parser.set_defaults(func=cmd_backfill)
    
    # update 子命令
    update_parser = subparsers.add_parser(
        "update",
        help="每日增量更新",
        description="获取指定日期（默认昨日）的全市场数据",
    )
    update_parser.add_argument(
        "--date", "-d",
        default=None,
        help="交易日期 (YYYYMMDD)，默认昨日（与 --start/--end 互斥）",
    )
    update_parser.add_argument(
        "--start", "-s",
        default=None,
        help="开始日期 (YYYYMMDD)，用于区间更新",
    )
    update_parser.add_argument(
        "--end", "-e",
        default=None,
        help="结束日期 (YYYYMMDD)，默认昨日，用于区间更新",
    )
    update_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="强制重新下载（不跳过已存在文件），仅区间模式有效",
    )
    update_parser.add_argument(
        "--api",
        action="append",
        choices=SUPPORTED_STOCK_DAILY_APIS,
        help="指定更新的接口，可多次使用（默认仅 daily）",
    )
    update_parser.add_argument(
        "--all",
        action="store_true",
        help="更新所有支持接口（默认仅 daily）",
    )
    update_parser.add_argument(
        "--extras-all",
        action="store_true",
        help="更新行业与概念相关的所有额外数据（维表、面板、原始接口快照）",
    )
    update_parser.add_argument(
        "--extras-force",
        action="store_true",
        help="强制覆盖已存在的行业/概念文件（默认跳过已存在文件）",
    )
    update_parser.add_argument(
        "--ci-dim",
        action="store_true",
        help="更新中信行业指数维表（dim_ci_index）",
    )
    update_parser.add_argument(
        "--industry-panel",
        action="store_true",
        help="更新股票-交易日的行业与概念聚合面板（industry_concept_panel）",
    )
    update_parser.add_argument(
        "--industry-raw",
        action="store_true",
        help="更新原始行业与概念相关接口快照（index_classify/ths_index/dc_index 等）",
    )
    update_parser.set_defaults(func=cmd_update)
    
    # info 子命令
    info_parser = subparsers.add_parser(
        "info",
        help="显示配置信息",
    )
    info_parser.set_defaults(func=cmd_info)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    setup_logging(args.verbose)
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
