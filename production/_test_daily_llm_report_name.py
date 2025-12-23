from pathlib import Path

import pandas as pd

from get_data_tushare.config import DATA_ROOT
from production.daily_llm_report import _build_industry_concept_mapping


def test_industry_concept_mapping_contains_name():
    """
    验证 _build_industry_concept_mapping 会为映射结果补充股票名称列，
    以便后续 LLM 表格中可以同时看到代码与名称。
    """
    # 选一个已存在的交易日
    date_str = "20251218"
    year = date_str[:4]
    daily_dir = DATA_ROOT / "raw" / "daily" / year
    sb_path = daily_dir / f"stock_basic_{date_str}.parquet"

    if not sb_path.exists():
        # 数据环境不完整时直接跳过
        return

    sb = pd.read_parquet(sb_path)
    assert "ts_code" in sb.columns

    sample_codes = sb["ts_code"].astype(str).head(5).tolist()
    mapping = _build_industry_concept_mapping(date_str, sample_codes)

    assert "name" in mapping.columns
    # 至少应该有部分名称非空
    assert mapping["name"].notna().any()

