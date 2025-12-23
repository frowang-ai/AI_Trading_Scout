#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM 配置管理

提供 LLM API 配置管理功能，支持多供应商路由。
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# 使用 pathlib + __file__ 定位项目根目录，并显式加载根目录下的 .env
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()
env_path = project_root / ".env"

if env_path.exists():
    load_dotenv(env_path)


# 针对不同 API 的配置
LLM_CONFIG = {
    "yunwu_robust_gemini": {
        "provider": "yunwu",
        "api_url": "https://yunwu.ai/v1",
        "api_key": os.getenv("YUNWU_ROBUST_GEMINI_API_KEY"),
        # 默认模型，可在阶段路由中被覆盖
        "default_model": "gemini-2.5-pro",
        "temperature": 0.7,
        "max_retries": 5,
        "retry_base_delay": 1,
    },
    "yunwu_robust_gpt": {
        "provider": "yunwu",
        "api_url": "https://yunwu.ai/v1",
        "api_key": os.getenv("YUNWU_ROBUST_GPT_API_KEY"),
        "default_model": "gpt-4o-2024-08-06",
        "temperature": 0.7,
        "max_retries": 5,
        "retry_base_delay": 1,
    },
}

# 默认 API 配置
CURRENT_API = "yunwu_robust_gpt"

# 阶段到 API 的路由配置（可选，用于特定任务场景）
# 这里为“每日报告生成”预留了两个阶段：
# - daily_report_gemini：使用 yunwu_robust_gemini / gemini-3-pro-preview
# - daily_report_gpt   ：使用 yunwu_robust_gpt    / gpt-5.1
LLM_STAGE_ROUTING = {
    "daily_report_gemini": {
        "api": "yunwu_robust_gemini",
        "model": "gemini-3-pro-preview",
        "temperature": 0.7,
    },
    "daily_report_gpt": {
        "api": "yunwu_robust_gpt",
        "model": "gpt-5.1",
        "temperature": 0.7,
    },
}


def get_api_config(api_name: str | None = None) -> dict:
    """
    获取 API 配置。

    Args:
        api_name: API 名称，如果为 None 则使用当前默认 API。

    Returns:
        API 配置字典。
    """
    api = api_name or CURRENT_API
    if api not in LLM_CONFIG:
        raise ValueError(f"未知的 API 名称: {api}，可用的 API: {list(LLM_CONFIG.keys())}")
    return LLM_CONFIG[api]


def get_route_for_stage(stage_name: str, default: str | None = None) -> dict:
    """
    根据阶段名称返回一份解析后的路由信息：
    {"api_name": str, "model": Optional[str], "temperature": Optional[float]}

    - 若阶段未配置或非法，api_name 回退到 default 或 CURRENT_API
    - model/temperature 仅在阶段配置为 dict 且提供时返回
    """
    base_default = default or CURRENT_API
    route = LLM_STAGE_ROUTING.get(stage_name)

    # 未配置：回退
    if route is None:
        return {"api_name": base_default, "model": None, "temperature": None}

    # 简写：字符串表示 API 名称
    if isinstance(route, str):
        api_name = route if route in LLM_CONFIG else base_default
        return {"api_name": api_name, "model": None, "temperature": None}

    # 展开：字典
    if isinstance(route, dict):
        api_name = route.get("api", base_default)
        if api_name not in LLM_CONFIG:
            print(f"警告: 阶段 {stage_name} 配置的 API '{api_name}' 不存在，回退到 {base_default}")
            api_name = base_default
        return {
            "api_name": api_name,
            "model": route.get("model"),
            "temperature": route.get("temperature"),
        }

    # 其他类型：回退
    print(f"警告: 阶段 {stage_name} 的路由配置类型不支持（{type(route)}），回退到 {base_default}")
    return {"api_name": base_default, "model": None, "temperature": None}


def list_available_apis() -> list[str]:
    """
    列出所有可用的 API。

    Returns:
        可用 API 名称列表。
    """
    return list(LLM_CONFIG.keys())


def list_available_providers() -> list[str]:
    """
    列出所有可用的供应商。

    Returns:
        可用供应商列表。
    """
    providers: set[str] = set()
    for config in LLM_CONFIG.values():
        providers.add(config.get("provider", "unknown"))
    return sorted(list(providers))

