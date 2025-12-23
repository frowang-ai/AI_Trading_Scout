"""
Tushare 数据获取模块配置。

本模块定义了 Tushare API Token 的加载逻辑、数据存储路径等全局常量。
遵循《工程实践规范》，使用 pathlib 进行路径定位。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

# ==============================================================================
# 路径配置（基于 __file__ 定位，跨平台稳定）
# ==============================================================================

# 当前模块所在目录: get_data_tushare/
_CURRENT_DIR: Final[Path] = Path(__file__).parent.resolve()

# 项目根目录: AI_Trading_Scout/
PROJECT_ROOT: Final[Path] = _CURRENT_DIR.parent.resolve()

# 数据存储根目录: AI_Trading_Scout/data/
DATA_ROOT: Final[Path] = PROJECT_ROOT / "data"

# Raw Layer 日线数据目录: data/raw/daily/
RAW_DAILY_DIR: Final[Path] = DATA_ROOT / "raw" / "daily"

# ==============================================================================
# 加载 .env 文件（如果存在）
# ==============================================================================

_ENV_FILE: Final[Path] = PROJECT_ROOT / ".env"

if _ENV_FILE.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_ENV_FILE, override=False)  # 不覆盖已有环境变量
    except ImportError:
        pass  # python-dotenv 未安装时静默跳过

# ==============================================================================
# Tushare API 配置
# ==============================================================================

def get_tushare_token() -> str:
    """
    获取 Tushare API Token。
    
    优先级:
        1. 环境变量 TUSHARE_TOKEN（已设置的优先）
        2. 项目根目录下 .env 文件中的 TUSHARE_TOKEN
    
    Returns:
        Tushare API Token 字符串
    
    Raises:
        ValueError: Token 未配置时抛出
    """
    token = os.environ.get("TUSHARE_TOKEN", "").strip()
    if not token:
        raise ValueError(
            "Tushare Token 未配置。请设置环境变量 TUSHARE_TOKEN，"
            "或在项目根目录创建 .env 文件并写入 TUSHARE_TOKEN=your_token"
        )
    return token


# ==============================================================================
# API 限流配置
# ==============================================================================

# 每次 API 调用后的休眠时间（秒），用于限流
# 根据积分等级调整：2000分约200次/分钟 → 0.3秒/次
API_CALL_INTERVAL: Final[float] = 0.35

# API 调用失败后的最大重试次数
MAX_RETRY_ATTEMPTS: Final[int] = 3

# 重试时的初始等待时间（秒），采用指数退避
RETRY_INITIAL_WAIT: Final[float] = 1.0

# ==============================================================================
# 数据格式配置
# ==============================================================================

# Parquet 压缩方式
PARQUET_COMPRESSION: Final[str] = "snappy"

# 日期格式
DATE_FORMAT: Final[str] = "%Y%m%d"

# ==============================================================================
# 交易所配置
# ==============================================================================

# 默认使用上交所日历（沪深两市交易日相同）
DEFAULT_EXCHANGE: Final[str] = "SSE"
