#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用于验证 LLM 配置结构与环境变量加载行为的最小测试脚本。
"""

from LLMClient_v2 import llm_config


def _test_llm_config_basic():
    """
    基本结构检查：
    - CURRENT_API 一定在 LLM_CONFIG 中
    - 每个配置至少包含 api_url 与 api_key 字段（值允许为 None，具体由 .env 决定）
    """
    assert llm_config.CURRENT_API in llm_config.LLM_CONFIG

    for name, cfg in llm_config.LLM_CONFIG.items():
        assert isinstance(cfg, dict), f"配置 {name} 不是字典类型"
        assert "api_url" in cfg, f"配置 {name} 缺少 api_url 字段"
        assert "api_key" in cfg, f"配置 {name} 缺少 api_key 字段"


if __name__ == "__main__":
    _test_llm_config_basic()
    print("LLM 配置结构检查通过。")

