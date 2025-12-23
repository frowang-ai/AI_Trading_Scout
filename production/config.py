"""
生产环境配置
"""
from pathlib import Path

# 基准目录（遵循工程实践规范）
current_dir = Path(__file__).parent.resolve()
PROJECT_ROOT = current_dir.parent.resolve()

# 路径配置
HISTORY_DIR = current_dir / "history"
TEMPLATES_DIR = current_dir / "templates"
OUTPUT_DIR = PROJECT_ROOT / "production_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 模型配置：Demo1 中基于 Tushare 逆向拟合的 XGBoost 模型
DEMO_MODEL_PATH = (
    PROJECT_ROOT
    / "demo"
    / "demo1-逆向总分"
    / "output_full"
    / "xgboost_model_nov.pkl"
)
MODEL_PATH = DEMO_MODEL_PATH

# 策略配置
TOP_N = 50
DATE_FORMAT = "%Y%m%d"

# LLM 配置占位符（后续在 llm_analyst 中具体使用）
LLM_ROUTE_GEMINI = "yunwu_robust_gemini"  # 使用 gemini-3-pro-preview
LLM_ROUTE_GPT = "yunwu_robust_gpt"        # 使用 gpt-5.1
