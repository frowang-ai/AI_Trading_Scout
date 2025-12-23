"""
日线行情数据获取器。

本模块提供 DailyFetcher 类，负责：
- 交易日历管理
- 全市场日线数据的按日获取（Cross-Sectional Fetching）
- 历史数据回补（Initialization）
- 每日增量更新（Daily Update）

遵循 SOLID 原则：
- SRP: 专注于日线数据获取与存储
- OCP: 通过组合 TushareClient 实现扩展
- DIP: 依赖抽象（client 接口），而非具体实现
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import pandas as pd

from .client import TushareClient, TushareAPIError
from .config import (
    DEFAULT_EXCHANGE,
    PARQUET_COMPRESSION,
)
from .utils import (
    date_to_str,
    ensure_parent_dir,
    filter_existing_dates,
    filter_existing_dates_for_api,
    get_raw_daily_api_path,
    get_raw_daily_path,
    get_today,
    get_yesterday,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


# 支持的股票日频 API 名称（ts_code + trade_date 主键）
SUPPORTED_STOCK_DAILY_APIS: tuple[str, ...] = (
    "daily",
    "daily_basic",
    "adj_factor",
    "stk_limit",
    "moneyflow",
    "stk_factor",
    "stk_factor_pro",
    "stk_nineturn",
    "stk_auction",
    # cyq_chips 需要 ts_code 维度参数，无法做全市场截面拉取，这里不纳入日频截面批量接口
)


class DailyFetcherError(Exception):
    """日线数据获取异常。"""


class DailyFetcher:
    """
    日线行情数据获取器。
    
    负责从 Tushare 获取全市场日线数据并存储到 Raw Layer。
    
    Attributes:
        client: Tushare API 客户端
        _trade_calendar_cache: 交易日历缓存
    
    Example:
        >>> fetcher = DailyFetcher()
        >>> # 获取单日数据
        >>> df = fetcher.fetch_cross_section("20231130")
        >>> # 历史回补
        >>> fetcher.run_initialization("20230101", "20231130")
        >>> # 每日更新
        >>> fetcher.run_daily_update()
    """
    
    def __init__(self, client: TushareClient | None = None) -> None:
        """
        初始化日线数据获取器。
        
        Args:
            client: Tushare 客户端实例，默认使用单例
        """
        self.client = client or TushareClient()
        self._trade_calendar_cache: dict[str, set[str]] = {}
    
    # =========================================================================
    # 交易日历相关
    # =========================================================================
    
    def fetch_trade_calendar(
        self,
        start_date: str,
        end_date: str,
        exchange: str = DEFAULT_EXCHANGE,
    ) -> list[str]:
        """
        获取指定时间段内的交易日列表。
        
        Args:
            start_date: 开始日期，YYYYMMDD
            end_date: 结束日期，YYYYMMDD
            exchange: 交易所代码，默认 SSE
        
        Returns:
            交易日列表，升序排列
        
        Example:
            >>> fetcher = DailyFetcher()
            >>> dates = fetcher.fetch_trade_calendar("20231101", "20231130")
            >>> print(dates[:3])
            ['20231101', '20231102', '20231103']
        """
        logger.debug(f"获取交易日历: {start_date} - {end_date}")
        
        df = self.client.trade_cal(
            exchange=exchange,
            start_date=start_date,
            end_date=end_date,
            is_open="1",
        )
        
        if df.empty:
            logger.warning(f"交易日历为空: {start_date} - {end_date}")
            return []
        
        # 提取 cal_date 列并排序
        trade_dates = sorted(df["cal_date"].astype(str).tolist())
        logger.info(f"获取到 {len(trade_dates)} 个交易日")
        
        return trade_dates
    
    def is_trade_date(self, date_str: str, exchange: str = DEFAULT_EXCHANGE) -> bool:
        """
        检查指定日期是否为交易日。
        
        Args:
            date_str: 日期字符串，YYYYMMDD
            exchange: 交易所代码
        
        Returns:
            是否为交易日
        """
        # 使用缓存避免重复查询
        cache_key = f"{exchange}_{date_str[:6]}"  # 按月缓存
        
        if cache_key not in self._trade_calendar_cache:
            year_month = date_str[:6]
            start = f"{year_month}01"
            end = f"{year_month}31"
            dates = self.fetch_trade_calendar(start, end, exchange)
            self._trade_calendar_cache[cache_key] = set(dates)
        
        return date_str in self._trade_calendar_cache[cache_key]
    
    # =========================================================================
    # 数据获取
    # =========================================================================
    
    def fetch_cross_section(self, trade_date: str) -> pd.DataFrame:
        """
        获取指定交易日的全市场日线数据（横截面数据）。
        
        Args:
            trade_date: 交易日期，YYYYMMDD
        
        Returns:
            全市场日线数据 DataFrame，包含字段:
            ts_code, trade_date, open, high, low, close, 
            pre_close, change, pct_chg, vol, amount
        
        Raises:
            TushareAPIError: API 调用失败时抛出
        
        Example:
            >>> fetcher = DailyFetcher()
            >>> df = fetcher.fetch_cross_section("20231130")
            >>> print(f"获取到 {len(df)} 只股票的数据")
        """
        date_str = date_to_str(trade_date)
        logger.debug(f"获取日线数据: {date_str}")
        
        df = self.client.daily(trade_date=date_str)
        
        if df.empty:
            logger.warning(f"[{date_str}] 返回数据为空")
        else:
            logger.debug(f"[{date_str}] 获取到 {len(df)} 条记录")
        
        return df
    
    # =========================================================================
    # 数据存储
    # =========================================================================
    
    def save_to_raw(self, df: pd.DataFrame, trade_date: str) -> Path:
        """
        将数据保存到 Raw Layer。
        
        存储路径: data/raw/daily/YYYY/YYYYMMDD.parquet
        
        Args:
            df: 待保存的 DataFrame
            trade_date: 交易日期，YYYYMMDD
        
        Returns:
            保存的文件路径
        
        Raises:
            DailyFetcherError: 数据为空时抛出
        """
        if df.empty:
            raise DailyFetcherError(f"[{trade_date}] 数据为空，拒绝保存空文件")
        
        file_path = get_raw_daily_path(trade_date)
        ensure_parent_dir(file_path)
        
        # 数据类型标准化
        df = self._normalize_dtypes(df)
        
        # 保存为 Parquet
        df.to_parquet(file_path, compression=PARQUET_COMPRESSION, index=False)
        
        logger.info(f"[{trade_date}] 保存成功: {file_path} ({len(df)} 行)")
        return file_path
    
    @staticmethod
    def _normalize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化 DataFrame 数据类型。
        
        Args:
            df: 原始 DataFrame
        
        Returns:
            类型标准化后的 DataFrame
        """
        df = df.copy()
        
        # 字符串类型
        str_cols = ["ts_code", "trade_date"]
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # 浮点类型（显式转换为 float64，确保一致性）
        float_cols = ["open", "high", "low", "close", "pre_close", 
                      "change", "pct_chg", "vol", "amount"]
        for col in float_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
        
        return df
    
    # =========================================================================
    # 批量任务
    # =========================================================================
    
    def fetch_and_save(self, trade_date: str) -> bool:
        """
        获取并保存单日数据（fetch -> validate -> save 流程）。
        
        Args:
            trade_date: 交易日期
        
        Returns:
            是否成功
        """
        try:
            df = self.fetch_cross_section(trade_date)
            if df.empty:
                logger.warning(f"[{trade_date}] 数据为空，跳过")
                return False
            self.save_to_raw(df, trade_date)
            return True
        except TushareAPIError as e:
            logger.error(f"[{trade_date}] API 错误: {e}")
            return False
        except DailyFetcherError as e:
            logger.error(f"[{trade_date}] 保存错误: {e}")
            return False
    
    def run_initialization(
        self,
        start_date: str,
        end_date: str | None = None,
        *,
        skip_existing: bool = True,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, int]:
        """
        历史数据回补。
        
        遍历指定时间段内的所有交易日，获取并存储全市场日线数据。
        支持断点续传（跳过已存在的文件）。
        
        Args:
            start_date: 开始日期，YYYYMMDD
            end_date: 结束日期，YYYYMMDD，默认为昨日
            skip_existing: 是否跳过已存在的文件
            progress_callback: 进度回调函数，参数为 (当前序号, 总数, 日期)
        
        Returns:
            统计信息字典:
                - total: 总交易日数
                - success: 成功数
                - skipped: 跳过数
                - failed: 失败数
        
        Example:
            >>> fetcher = DailyFetcher()
            >>> stats = fetcher.run_initialization("20230101", "20231130")
            >>> print(f"成功: {stats['success']}, 失败: {stats['failed']}")
        """
        end_date = end_date or get_yesterday()
        
        logger.info(f"开始历史数据回补: {start_date} - {end_date}")
        
        # 获取交易日历
        trade_dates = self.fetch_trade_calendar(start_date, end_date)
        
        if not trade_dates:
            logger.warning("交易日列表为空")
            return {"total": 0, "success": 0, "skipped": 0, "failed": 0}
        
        # 断点续传：过滤已存在的日期
        if skip_existing:
            pending_dates = filter_existing_dates(trade_dates)
            skipped_count = len(trade_dates) - len(pending_dates)
            logger.info(f"跳过已存在文件: {skipped_count} 个")
        else:
            pending_dates = list(trade_dates)
            skipped_count = 0
        
        total = len(trade_dates)
        success_count = 0
        failed_count = 0
        
        for i, date_str in enumerate(pending_dates, 1):
            if progress_callback:
                progress_callback(i, len(pending_dates), date_str)
            else:
                logger.info(f"[{i}/{len(pending_dates)}] 处理: {date_str}")
            
            if self.fetch_and_save(date_str):
                success_count += 1
            else:
                failed_count += 1
        
        stats = {
            "total": total,
            "success": success_count,
            "skipped": skipped_count,
            "failed": failed_count,
        }
        
        logger.info(
            f"历史回补完成: 总计 {total} 日, "
            f"成功 {success_count}, 跳过 {skipped_count}, 失败 {failed_count}"
        )
        
        return stats
    
    def run_daily_update(self, trade_date: str | None = None) -> bool:
        """
        每日增量更新。
        
        获取并存储指定日期（默认昨日）的全市场日线数据。
        会自动检查是否为交易日。
        
        Args:
            trade_date: 交易日期，默认为昨日
        
        Returns:
            是否成功（非交易日返回 True）
        
        Example:
            >>> fetcher = DailyFetcher()
            >>> success = fetcher.run_daily_update()
            >>> if success:
            ...     print("更新成功")
        """
        date_str = trade_date or get_yesterday()
        
        logger.info(f"每日更新: {date_str}")
        
        # 检查是否为交易日
        if not self.is_trade_date(date_str):
            logger.info(f"[{date_str}] 非交易日，跳过")
            return True
        
        # 检查文件是否已存在
        file_path = get_raw_daily_path(date_str)
        if file_path.exists() and file_path.stat().st_size > 1024:
            logger.info(f"[{date_str}] 文件已存在，跳过")
            return True
        
        return self.fetch_and_save(date_str)

    def build_ci_index_dim(self, as_of_date: str | None = None) -> pd.DataFrame:
        date_str = date_to_str(as_of_date or get_today())
        print(f"[ci-index-dim] 开始构建中信行业指数维表: {date_str}")
        base = self.client.query("ci_daily", trade_date=date_str)[["ts_code"]].drop_duplicates()
        ci_codes = base["ts_code"].tolist()
        print(f"[ci-index-dim] 共 {len(ci_codes)} 个中信指数代码")
        rows: list[dict[str, str | None]] = []
        for i, code in enumerate(ci_codes, 1):
            lvl = None
            name = None
            df3 = self.client.query("ci_index_member", l3_code=code)
            if df3 is not None and not df3.empty:
                lvl = "L3"
                name = df3.iloc[0]["l3_name"]
            else:
                df2 = self.client.query("ci_index_member", l2_code=code)
                if df2 is not None and not df2.empty:
                    lvl = "L2"
                    name = df2.iloc[0]["l2_name"]
                else:
                    df1 = self.client.query("ci_index_member", l1_code=code)
                    if df1 is not None and not df1.empty:
                        lvl = "L1"
                        name = df1.iloc[0]["l1_name"]
            rows.append({"as_of_date": date_str, "ts_code": code, "level": lvl, "name": name})
            if i % 10 == 0 or i == len(ci_codes):
                print(f"[ci-index-dim] 已处理 {i}/{len(ci_codes)} 个指数")
        print(f"[ci-index-dim] 构建完成，共 {len(rows)} 条记录")
        return pd.DataFrame(rows)

    def save_ci_index_dim_to_raw(self, as_of_date: str | None = None, *, overwrite: bool = False) -> Path:
        """
        保存中信行业指数维表到 Raw Layer。

        Args:
            as_of_date: 截止日期，YYYYMMDD，默认今日
            overwrite: 是否覆盖已存在的文件（默认 False，存在则跳过）

        Returns:
            保存的文件路径（若跳过则返回已存在路径）
        """
        date_str = date_to_str(as_of_date or get_today())
        file_path = get_raw_daily_api_path("ci_index_dim", date_str)
        
        # 先检查文件是否存在，避免不必要的 API 调用
        if file_path.exists() and file_path.stat().st_size > 1024 and not overwrite:
            print(f"[ci-index-dim] 已存在，跳过: {file_path}")
            return file_path
        
        # 文件不存在或需要覆盖，执行构建
        dim = self.build_ci_index_dim(date_str)
        if dim.empty:
            raise DailyFetcherError(f"[{date_str}] ci_index_dim 为空")
        
        ensure_parent_dir(file_path)
        dim.to_parquet(file_path, compression=PARQUET_COMPRESSION, index=False)
        print(f"[ci-index-dim] 已保存: {file_path}")
        return file_path

    def build_industry_concept_panel(self, trade_date: str, max_stocks: int | None = None) -> pd.DataFrame:
        date_str = date_to_str(trade_date)
        print(f"[industry-panel] start {date_str}")
        sb = self.client.query("stock_basic", exchange="", list_status="L", fields="ts_code,symbol,name,area,industry,list_date")
        base = self.client.query("bak_basic", trade_date=date_str)[["trade_date", "ts_code", "name", "industry", "area"]]
        ts_list = sb["ts_code"].tolist()
        if max_stocks is not None:
            ts_list = ts_list[:max_stocks]
        print(f"[industry-panel] stocks {len(ts_list)}")
        sw_l3 = self.client.query("index_classify", level="L3", src="SW2021")[["index_code", "industry_name"]]
        sw_rows: list[dict[str, str]] = []
        print(f"[industry-panel] sw L3 count {len(sw_l3)}")
        for i, (l3_code, _) in enumerate(sw_l3.to_records(index=False), 1):
            df = self.client.query("index_member_all", l3_code=l3_code, is_new="Y")
            if df is None or df.empty:
                continue
            df = df.copy()
            for c in ["in_date", "out_date"]:
                if c in df.columns:
                    df[c] = df[c].fillna("")
            in_ok = (df["in_date"] == "") | (df["in_date"] <= date_str)
            out_ok = (df["out_date"] == "") | (df["out_date"] >= date_str)
            df = df[in_ok & out_ok]
            if df.empty:
                continue
            for _, r in df.iterrows():
                sw_rows.append(
                    {
                        "ts_code": r["ts_code"],
                        "sw_l1_code": r["l1_code"],
                        "sw_l1_name": r["l1_name"],
                        "sw_l2_code": r["l2_code"],
                        "sw_l2_name": r["l2_name"],
                        "sw_l3_code": r["l3_code"],
                        "sw_l3_name": r["l3_name"],
                    }
                )
            if i % 20 == 0:
                print(f"[industry-panel] sw L3 processed {i}/{len(sw_l3)}")
        sw_map = pd.DataFrame(sw_rows).drop_duplicates(subset=["ts_code"])
        print(f"[industry-panel] sw_map {sw_map.shape}")
        ci_rows: list[dict[str, str]] = []
        for j, code in enumerate(ts_list, 1):
            df = self.client.query("ci_index_member", ts_code=code)
            if df is None or df.empty:
                continue
            df = df.copy()
            for c in ["in_date", "out_date"]:
                if c in df.columns:
                    df[c] = df[c].fillna("")
            in_ok = (df["in_date"] == "") | (df["in_date"] <= date_str)
            out_ok = (df["out_date"] == "") | (df["out_date"] >= date_str)
            df = df[in_ok & out_ok]
            if df.empty:
                continue
            r = df.iloc[0]
            ci_rows.append(
                {
                    "ts_code": r["ts_code"],
                    "ci_l1_code": r["l1_code"],
                    "ci_l1_name": r["l1_name"],
                    "ci_l2_code": r["l2_code"],
                    "ci_l2_name": r["l2_name"],
                    "ci_l3_code": r["l3_code"],
                    "ci_l3_name": r["l3_name"],
                }
            )
            if j % 100 == 0:
                print(f"[industry-panel] ci member processed {j}/{len(ts_list)}")
        ci_map = pd.DataFrame(ci_rows).drop_duplicates(subset=["ts_code"])
        print(f"[industry-panel] ci_map {ci_map.shape}")
        dc_idx = self.client.query("dc_index", trade_date=date_str)[["ts_code", "name"]]
        dc_member = self.client.query("dc_member", trade_date=date_str)[["trade_date", "ts_code", "con_code", "name"]]
        dc_name_map = dc_idx.set_index("ts_code")["name"].to_dict()
        dc_group = dc_member.groupby("con_code").agg(
            dc_board_codes=("ts_code", lambda s: ",".join(sorted(set(s)))),
            dc_board_names=("ts_code", lambda s: ",".join(sorted({dc_name_map.get(x, "") for x in s}))),
        )
        dc_group = dc_group.rename_axis("ts_code").reset_index()
        print(f"[industry-panel] dc_group {dc_group.shape}")
        ths_idx = self.client.query("ths_index", type="N")[["ts_code", "name"]]
        ths_name_map = ths_idx.set_index("ts_code")["name"].to_dict()
        ths_rows: list[dict[str, str]] = []
        print(f"[industry-panel] ths_index count {len(ths_idx)}")
        for k, (b_code, b_name) in enumerate(ths_idx.to_records(index=False), 1):
            df = self.client.query("ths_member", ts_code=b_code)
            if df is None or df.empty:
                continue
            for _, r in df.iterrows():
                ths_rows.append(
                    {
                        "ts_code": r["con_code"],
                        "ths_board_codes": b_code,
                        "ths_board_names": b_name,
                    }
                )
            if k % 50 == 0:
                print(f"[industry-panel] ths members processed {k}/{len(ths_idx)}")
        if ths_rows:
            ths_df = pd.DataFrame(ths_rows)
            ths_group = ths_df.groupby("ts_code").agg(
                ths_board_codes=("ths_board_codes", lambda s: ",".join(sorted(set(s)))),
                ths_board_names=("ths_board_names", lambda s: ",".join(sorted(set(s)))),
            ).reset_index()
        else:
            ths_group = pd.DataFrame(columns=["ts_code", "ths_board_codes", "ths_board_names"])
        out = base.merge(sw_map, on="ts_code", how="left").merge(ci_map, on="ts_code", how="left").merge(dc_group, on="ts_code", how="left").merge(ths_group, on="ts_code", how="left")
        print(f"[industry-panel] built {out.shape}")
        return out

    def build_industry_concept_panel_from_snapshots(
        self, trade_date: str, max_stocks: int | None = None
    ) -> pd.DataFrame:
        """
        从本地快照构建 industry_concept_panel（零 API 调用）。
        
        相比 build_industry_concept_panel，本方法从已保存的快照文件读取数据，
        避免重复 API 调用，构建速度快（秒级）。
        
        Args:
            trade_date: 交易日期，YYYYMMDD
            max_stocks: 限制股票数量（用于测试），None 表示全部
        
        Returns:
            股票-日期-行业概念面板 DataFrame
        
        Raises:
            FileNotFoundError: 快照文件不存在时抛出
        """
        date_str = date_to_str(trade_date)
        print(f"[panel-from-snapshot] 从快照构建面板: {date_str}")
        
        def load_snapshot(api_name: str) -> pd.DataFrame:
            """加载快照文件"""
            file_path = get_raw_daily_api_path(api_name, date_str)
            if not file_path.exists():
                raise FileNotFoundError(
                    f"快照文件不存在: {file_path}。"
                    f"请先运行: python -m get_data_tushare.cli update --date {date_str} --industry-raw"
                )
            return pd.read_parquet(file_path)
        
        # 1. 加载基础数据
        print(f"[panel-from-snapshot] 步骤1：加载基础数据...")
        stock_basic = load_snapshot("stock_basic")
        bak_basic = load_snapshot("bak_basic")
        base = bak_basic[["trade_date", "ts_code", "name", "industry", "area"]]
        
        ts_list = stock_basic["ts_code"].tolist()
        if max_stocks is not None:
            ts_list = ts_list[:max_stocks]
        print(f"   ✓ 股票数：{len(ts_list)}")
        
        # 2. 申万行业
        print(f"[panel-from-snapshot] 步骤2：加载申万行业快照...")
        sw_member = load_snapshot("index_member_all")
        sw_member = sw_member.copy()
        for c in ["in_date", "out_date"]:
            if c in sw_member.columns:
                sw_member[c] = sw_member[c].fillna("")
        in_ok = (sw_member["in_date"] == "") | (sw_member["in_date"] <= date_str)
        out_ok = (sw_member["out_date"] == "") | (sw_member["out_date"] >= date_str)
        sw_member = sw_member[in_ok & out_ok]
        
        sw_map = sw_member[[
            "ts_code", "l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"
        ]].rename(columns={
            "l1_code": "sw_l1_code", "l1_name": "sw_l1_name",
            "l2_code": "sw_l2_code", "l2_name": "sw_l2_name",
            "l3_code": "sw_l3_code", "l3_name": "sw_l3_name",
        }).drop_duplicates(subset=["ts_code"])
        print(f"   ✓ 申万映射：{sw_map.shape}")
        
        # 3. 中信行业
        print(f"[panel-from-snapshot] 步骤3：加载中信行业快照...")
        try:
            ci_member = load_snapshot("ci_index_member")
            ci_member = ci_member.copy()
            for c in ["in_date", "out_date"]:
                if c in ci_member.columns:
                    ci_member[c] = ci_member[c].fillna("")
            in_ok = (ci_member["in_date"] == "") | (ci_member["in_date"] <= date_str)
            out_ok = (ci_member["out_date"] == "") | (ci_member["out_date"] >= date_str)
            ci_member = ci_member[in_ok & out_ok]
            
            ci_map = ci_member[[
                "ts_code", "l1_code", "l1_name", "l2_code", "l2_name", "l3_code", "l3_name"
            ]].rename(columns={
                "l1_code": "ci_l1_code", "l1_name": "ci_l1_name",
                "l2_code": "ci_l2_code", "l2_name": "ci_l2_name",
                "l3_code": "ci_l3_code", "l3_name": "ci_l3_name",
            }).drop_duplicates(subset=["ts_code"])
            print(f"   ✓ 中信映射：{ci_map.shape}")
        except FileNotFoundError:
            print(f"   ⚠️  中信成员快照缺失，跳过")
            ci_map = pd.DataFrame(columns=[
                "ts_code", "ci_l1_code", "ci_l1_name",
                "ci_l2_code", "ci_l2_name", "ci_l3_code", "ci_l3_name"
            ])
        
        # 4. 东财概念
        print(f"[panel-from-snapshot] 步骤4：加载东财概念快照...")
        dc_idx = load_snapshot("dc_index")
        dc_member = load_snapshot("dc_member")
        dc_name_map = dc_idx.set_index("ts_code")["name"].to_dict()
        dc_group = dc_member.groupby("con_code").agg(
            dc_board_codes=("ts_code", lambda s: ",".join(sorted(set(s)))),
            dc_board_names=("ts_code", lambda s: ",".join(sorted({dc_name_map.get(x, "") for x in s}))),
        ).rename_axis("ts_code").reset_index()
        print(f"   ✓ 东财映射：{dc_group.shape}")
        
        # 5. 同花顺概念
        print(f"[panel-from-snapshot] 步骤5：加载同花顺概念快照...")
        ths_idx = load_snapshot("ths_index")
        ths_member = load_snapshot("ths_member")
        ths_map = ths_member.merge(
            ths_idx[["ts_code", "name"]], left_on="ts_code", right_on="ts_code", suffixes=("", "_idx")
        )
        ths_group = ths_map.groupby("con_code").agg(
            ths_board_codes=("ts_code", lambda s: ",".join(sorted(set(s)))),
            ths_board_names=("name", lambda s: ",".join(sorted(set(s)))),
        ).rename_axis("ts_code").reset_index()
        print(f"   ✓ 同花顺映射：{ths_group.shape}")
        
        # 6. 合并
        print(f"[panel-from-snapshot] 步骤6：合并所有维度...")
        out = (
            base
            .merge(sw_map, on="ts_code", how="left")
            .merge(ci_map, on="ts_code", how="left")
            .merge(dc_group, on="ts_code", how="left")
            .merge(ths_group, on="ts_code", how="left")
        )
        
        print(f"[panel-from-snapshot] ✅ 构建完成：{out.shape}")
        return out

    def save_industry_concept_panel_to_raw(self, trade_date: str, max_stocks: int | None = None, *, overwrite: bool = False) -> Path:
        """
        保存 industry_concept_panel（从快照构建，零 API 调用）。

        Args:
            trade_date: 交易日期，YYYYMMDD
            max_stocks: 限制股票数量（用于测试），None 表示全部
            overwrite: 是否覆盖已存在的文件（默认 False，存在则跳过）

        Returns:
            保存的文件路径（若跳过则返回已存在路径）

        Note: 本方法依赖 industry_raw 快照，请确保先运行 save_raw_industry_concept.
        """
        date_str = date_to_str(trade_date)
        file_path = get_raw_daily_api_path("industry_concept_panel", date_str)
        
        # 先检查文件是否存在，避免不必要的快照加载
        if file_path.exists() and file_path.stat().st_size > 1024 and not overwrite:
            print(f"[panel-from-snapshot] 已存在，跳过: {file_path}")
            return file_path
        
        # 文件不存在或需要覆盖，从快照构建
        df = self.build_industry_concept_panel_from_snapshots(date_str, max_stocks=max_stocks)
        if df.empty:
            raise DailyFetcherError(f"[{date_str}] industry_concept_panel 为空")
        
        ensure_parent_dir(file_path)
        df.to_parquet(file_path, compression=PARQUET_COMPRESSION, index=False)
        print(f"[panel-from-snapshot] 💾 保存成功: {file_path}")
        return file_path

    def save_raw_industry_concept(self, trade_date: str, *, overwrite: bool = False) -> dict[str, Path]:
        """
        获取并保存原始的行业/概念相关快照数据到 Raw Layer。

        Args:
            trade_date: 交易日期，YYYYMMDD
            overwrite: 是否覆盖已存在的文件（默认 False，存在则跳过）

        Returns:
            名称到文件路径的映射
        """
        date_str = date_to_str(trade_date)
        print(f"[industry-raw] 开始获取原始行业概念数据: {date_str}")
        
        # 预检查：如果不覆盖且所有核心文件都已存在，直接跳过整个流程
        if not overwrite:
            core_files = [
                "stock_basic", "bak_basic", "index_classify_L1", "index_classify_L2",
                "index_classify_L3", "ths_index", "dc_index", "dc_member"
            ]
            all_exist = True
            paths: dict[str, Path] = {}
            for name in core_files:
                p = get_raw_daily_api_path(name, date_str)
                if not p.exists() or p.stat().st_size <= 1024:
                    all_exist = False
                    break
                paths[name] = p
            
            if all_exist:
                # 检查可选文件（可能不存在）
                for name in ["index_member_all", "ci_index_member", "ths_member"]:
                    p = get_raw_daily_api_path(name, date_str)
                    if p.exists() and p.stat().st_size > 1024:
                        paths[name] = p
                
                print(f"[industry-raw] 所有核心文件已存在，跳过 API 调用（共 {len(paths)} 个文件）")
                return paths
        
        # 需要获取数据，继续执行原有逻辑
        paths: dict[str, Path] = {}
        print(f"[industry-raw] 获取 stock_basic...")
        sb = self.client.query("stock_basic", exchange="", list_status="L", fields="ts_code,symbol,name,area,industry,list_date")
        print(f"[industry-raw] 获取 bak_basic...")
        bb = self.client.query("bak_basic", trade_date=date_str)
        print(f"[industry-raw] 获取申万行业分类 L1/L2/L3...")
        sw_l1 = self.client.query("index_classify", level="L1", src="SW2021")
        sw_l2 = self.client.query("index_classify", level="L2", src="SW2021")
        sw_l3 = self.client.query("index_classify", level="L3", src="SW2021")
        sw_mem_rows: list[pd.DataFrame] = []
        sw_l3_codes = sw_l3["index_code"].dropna().astype(str).tolist()
        print(f"[industry-raw] 获取申万 L3 成员，共 {len(sw_l3_codes)} 个行业...")
        for i, code in enumerate(sw_l3_codes, 1):
            df = self.client.query("index_member_all", l3_code=code, is_new="Y")
            if df is not None and not df.empty:
                sw_mem_rows.append(df)
            if i % 20 == 0 or i == len(sw_l3_codes):
                print(f"[industry-raw] 申万成员已处理 {i}/{len(sw_l3_codes)}")
        sw_mem = pd.concat(sw_mem_rows, ignore_index=True) if sw_mem_rows else pd.DataFrame()
        
        # 获取中信行业成员（按指数查询，优化后）
        print(f"[industry-raw] 获取中信行业指数...")
        ci_daily = self.client.query("ci_daily", trade_date=date_str)
        ci_mem_rows: list[pd.DataFrame] = []
        ci_codes = ci_daily["ts_code"].dropna().astype(str).tolist()
        print(f"[industry-raw] 获取中信成员，共 {len(ci_codes)} 个指数...")
        for i, code in enumerate(ci_codes, 1):
            df = self.client.query("ci_index_member", index_code=code)
            if df is not None and not df.empty:
                ci_mem_rows.append(df)
            if i % 50 == 0 or i == len(ci_codes):
                print(f"[industry-raw] 中信成员已处理 {i}/{len(ci_codes)}")
        ci_mem = pd.concat(ci_mem_rows, ignore_index=True) if ci_mem_rows else pd.DataFrame()
        
        print(f"[industry-raw] 获取同花顺概念板块...")
        ths_idx = self.client.query("ths_index", type="N")
        ths_mem_rows: list[pd.DataFrame] = []
        ths_codes = ths_idx["ts_code"].dropna().astype(str).tolist()
        print(f"[industry-raw] 获取同花顺成员，共 {len(ths_codes)} 个板块...")
        for i, code in enumerate(ths_codes, 1):
            df = self.client.query("ths_member", ts_code=code)
            if df is not None and not df.empty:
                ths_mem_rows.append(df)
            if i % 50 == 0 or i == len(ths_codes):
                print(f"[industry-raw] 同花顺成员已处理 {i}/{len(ths_codes)}")
        ths_mem = pd.concat(ths_mem_rows, ignore_index=True) if ths_mem_rows else pd.DataFrame()
        print(f"[industry-raw] 获取东财概念板块...")
        dc_idx = self.client.query("dc_index", trade_date=date_str)
        dc_mem = self.client.query("dc_member", trade_date=date_str)
        print(f"[industry-raw] 开始保存到 parquet 文件...")
        def save_df(name: str, df: pd.DataFrame, *, overwrite: bool = False) -> Path:
            if df is None or df.empty:
                raise DailyFetcherError(f"[{date_str}] {name} 为空")
            p = get_raw_daily_api_path(name, date_str)
            ensure_parent_dir(p)
            if p.exists() and p.stat().st_size > 1024 and not overwrite:
                print(f"[industry-raw]   跳过已存在: {name} -> {p}")
                return p
            df.to_parquet(p, compression=PARQUET_COMPRESSION, index=False)
            print(f"[industry-raw]   ✓ {name}: {len(df)} 行")
            return p
        paths["stock_basic"] = save_df("stock_basic", sb, overwrite=overwrite)
        paths["bak_basic"] = save_df("bak_basic", bb, overwrite=overwrite)
        paths["index_classify_L1"] = save_df("index_classify_L1", sw_l1, overwrite=overwrite)
        paths["index_classify_L2"] = save_df("index_classify_L2", sw_l2, overwrite=overwrite)
        paths["index_classify_L3"] = save_df("index_classify_L3", sw_l3, overwrite=overwrite)
        if not sw_mem.empty:
            paths["index_member_all"] = save_df("index_member_all", sw_mem, overwrite=overwrite)
        if not ci_mem.empty:
            paths["ci_index_member"] = save_df("ci_index_member", ci_mem, overwrite=overwrite)
        paths["ths_index"] = save_df("ths_index", ths_idx, overwrite=overwrite)
        if not ths_mem.empty:
            paths["ths_member"] = save_df("ths_member", ths_mem, overwrite=overwrite)
        paths["dc_index"] = save_df("dc_index", dc_idx, overwrite=overwrite)
        paths["dc_member"] = save_df("dc_member", dc_mem, overwrite=overwrite)
        print(f"[industry-raw] 保存完成，共 {len(paths)} 个文件")
        return paths

    def run_initialization_for_api(
        self,
        api_name: str,
        start_date: str,
        end_date: str | None = None,
        *,
        skip_existing: bool = True,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, int]:
        end_date = end_date or get_yesterday()
        trade_dates = self.fetch_trade_calendar(start_date, end_date)
        if not trade_dates:
            return {"total": 0, "success": 0, "skipped": 0, "failed": 0}
        if skip_existing:
            pending_dates = filter_existing_dates_for_api(api_name, trade_dates)
            skipped_count = len(trade_dates) - len(pending_dates)
        else:
            pending_dates = list(trade_dates)
            skipped_count = 0
        total = len(trade_dates)
        success_count = 0
        failed_count = 0
        for i, date_str in enumerate(pending_dates, 1):
            if progress_callback:
                progress_callback(i, len(pending_dates), date_str)
            try:
                df = fetch_api_cross_section(api_name, date_str, self.client)
                if df.empty:
                    logger.warning(f"[{date_str}] [{api_name}] 数据为空，跳过")
                    failed_count += 1
                    continue
                save_api_to_raw(api_name, df, date_str)
                success_count += 1
            except TushareAPIError as e:
                logger.error(f"[{date_str}] [{api_name}] API 错误: {e}")
                failed_count += 1
            except DailyFetcherError as e:
                logger.error(f"[{date_str}] [{api_name}] 保存错误: {e}")
                failed_count += 1
        return {
            "total": total,
            "success": success_count,
            "skipped": skipped_count,
            "failed": failed_count,
        }

    def run_daily_update_for_api(self, api_name: str, trade_date: str | None = None) -> bool:
        date_str = trade_date or get_yesterday()
        if not self.is_trade_date(date_str):
            return True
        file_path = get_raw_daily_api_path(api_name, date_str)
        if file_path.exists() and file_path.stat().st_size > 1024:
            return True
        try:
            df = fetch_api_cross_section(api_name, date_str, self.client)
            if df.empty:
                logger.warning(f"[{date_str}] [{api_name}] 数据为空，跳过")
                return False
            save_api_to_raw(api_name, df, date_str)
            return True
        except TushareAPIError as e:
            logger.error(f"[{date_str}] [{api_name}] API 错误: {e}")
            return False
        except DailyFetcherError as e:
            logger.error(f"[{date_str}] [{api_name}] 保存错误: {e}")
            return False

# =============================================================================
# 便捷函数
# =============================================================================

def fetch_daily_data(trade_date: str) -> pd.DataFrame:
    """
    便捷函数：获取指定日期的全市场日线数据。
    
    Args:
        trade_date: 交易日期，YYYYMMDD
    
    Returns:
        全市场日线数据 DataFrame
    """
    fetcher = DailyFetcher()
    return fetcher.fetch_cross_section(trade_date)


def run_backfill(start_date: str, end_date: str | None = None) -> dict[str, int]:
    """
    便捷函数：运行历史数据回补。
    
    Args:
        start_date: 开始日期
        end_date: 结束日期，默认昨日
    
    Returns:
        统计信息
    """
    fetcher = DailyFetcher()
    return fetcher.run_initialization(start_date, end_date)


def fetch_api_cross_section(
    api_name: str,
    trade_date: str,
    client: TushareClient | None = None,
) -> pd.DataFrame:
    """
    通用便捷函数：获取指定 API 在某一交易日的全市场截面数据。
    
    Args:
        api_name: Tushare 接口名称，例如 "daily_basic"
        trade_date: 交易日期，YYYYMMDD
        client: 可选 TushareClient 实例
    
    Returns:
        对应 API 的全市场截面数据 DataFrame
    """
    if api_name not in SUPPORTED_STOCK_DAILY_APIS:
        raise ValueError(f"不支持的 stock-daily 接口: {api_name}")
    
    client = client or TushareClient()
    date_str = date_to_str(trade_date)
    
    kwargs: dict[str, object] = {"trade_date": date_str}
    if api_name == "stk_nineturn":
        # 九转指标需要指定日频
        kwargs["freq"] = "daily"
    
    if api_name == "daily":
        df = client.daily(**kwargs)
    elif api_name == "trade_cal":
        # 防御：trade_cal 不属于 stock-daily 层，这里仅显式排除
        raise ValueError("trade_cal 不应通过 fetch_api_cross_section 获取")
    else:
        df = client.query(api_name, **kwargs)
    
    return df


def save_api_to_raw(
    api_name: str,
    df: pd.DataFrame,
    trade_date: str,
) -> Path:
    """
    将任意 stock-daily API 的数据保存到 Raw Layer。
    
    路径格式: data/raw/daily/YYYY/{api_name}_YYYYMMDD.parquet
    """
    if df.empty:
        raise DailyFetcherError(f"[{trade_date}] API={api_name} 数据为空，拒绝保存空文件")
    
    file_path = get_raw_daily_api_path(api_name, trade_date)
    ensure_parent_dir(file_path)
    
    # 对基础行情做类型标准化，其他接口保持原始字段类型
    if api_name == "daily":
        df_to_save = DailyFetcher._normalize_dtypes(df)
    else:
        df_to_save = df
    
    df_to_save.to_parquet(file_path, compression=PARQUET_COMPRESSION, index=False)
    logger.info(f"[{trade_date}] [{api_name}] 保存成功: {file_path} ({len(df_to_save)} 行)")
    return file_path
