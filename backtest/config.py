from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Data Paths
SCORE_DATA_DIR = PROJECT_ROOT / "刘丰硕的代码/测试数据xlsx版"
MARKET_DATA_DIR = PROJECT_ROOT / "data/raw/daily/2025"
OUTPUT_DIR = PROJECT_ROOT / "backtest/output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Wide Table Path
WIDE_TABLE_PATH = OUTPUT_DIR / "wide_table.parquet"

# Default holding days for backtest (1-10 days)
DEFAULT_HOLD_DAYS = list(range(1, 11))
