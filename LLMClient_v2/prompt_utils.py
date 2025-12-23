#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Prompt工具函数

用于处理和填充prompt模板，并包含从LLM响应中提取与修复JSON的工具
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union

# 尝试导入json5和json_repair（优先级：json5 > json_repair > json）
try:
    import json5
    json5_available = True
except ImportError:
    json5_available = False

try:
    from json_repair import repair_json
    json_repair_available = True
except ImportError:
    json_repair_available = False
    # 如果未安装 json_repair，提供一个退化的修复函数（直接返回输入）
    def repair_json(json_str: str) -> str:
        return json_str


def read_prompt_template(template_path: str) -> str:
    """
    读取prompt模板文件

    Args:
        template_path: 模板文件路径

    Returns:
        模板内容
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"读取模板文件失败: {e}")


def fill_prompt_with_document(template: Union[str, Path], document_text: str) -> str:
    """
    使用文档内容填充prompt模板。

    template 可以是模板文件路径或直接的模板字符串：
      - 如果 template 是一个存在的文件路径，则读取文件内容作为模板
      - 否则将 template 当作模板字符串直接使用

    Args:
        template: 模板文件路径或模板字符串
        document_text: 文档内容

    Returns:
        填充后的prompt
    """
    # 如果 template 指向文件则读取，否则当作字符串模板
    if isinstance(template, (str, Path)) and os.path.exists(str(template)):
        try:
            with open(str(template), 'r', encoding='utf-8') as f:
                template_content = f.read()
        except Exception as e:
            raise ValueError(f"读取提示词模板文件失败: {e}")
    else:
        template_content = str(template)

    # 替换{{document}}标记
    prompt = template_content.replace("{{document}}", document_text)
    return prompt


def fill_prompt_with_variables(template: Union[str, Path], variables: Dict[str, Any]) -> str:
    """
    使用变量填充prompt模板
    
    支持两种模式：
    1. 如果template是文件路径，则读取文件内容作为模板
    2. 如果template是字符串，则直接作为模板使用

    Args:
        template: 模板文件路径或模板字符串
        variables: 变量字典

    Returns:
        填充后的prompt
    """
    # 如果 template 指向文件则读取，否则当作字符串模板
    if isinstance(template, (str, Path)) and os.path.exists(str(template)):
        template_content = read_prompt_template(str(template))
    else:
        template_content = str(template)

    prompt = template_content
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        prompt = prompt.replace(placeholder, str(value))

    return prompt


# ---------------------------------------------------------------------
# 模板目录加载与缓存支持
# ---------------------------------------------------------------------

PROMPT_ROOT = Path(__file__).resolve().parent.parent / "resources" / "prompts"
PROMPT_CACHE: Dict[str, str] = {}


def get_prompt_template_path(name: str) -> Path:
    """
    根据模板名称返回Markdown模板路径（默认位于 resources/prompts ）
    """
    candidate = PROMPT_ROOT / f"{name}.md"
    if not candidate.exists():
        raise FileNotFoundError(f"未找到名为 '{name}' 的prompt模板: {candidate}")
    return candidate


def load_prompt_template(name: str, use_cache: bool = True) -> str:
    """
    读取并缓存命名模板
    """
    if use_cache and name in PROMPT_CACHE:
        return PROMPT_CACHE[name]

    template_path = get_prompt_template_path(name)
    content = read_prompt_template(str(template_path))

    if use_cache:
        PROMPT_CACHE[name] = content

    return content


def render_prompt_template(name: str, variables: Dict[str, Any], *, use_cache: bool = True) -> str:
    """
    使用变量渲染命名模板

    Args:
        name: 模板名称（不含扩展名）
        variables: 替换占位符所需的变量
        use_cache: 是否启用缓存
    """
    template = load_prompt_template(name, use_cache=use_cache)
    return fill_prompt_with_variables(template, variables)


def extract_json_from_response(response: str) -> str:
    """
    从LLM响应中提取可能的JSON字符串（不修复）。

    返回提取到的原始JSON文本片段或原始响应。
    
    Args:
        response: LLM的原始响应文本
        
    Returns:
        提取到的JSON字符串
    """
    # 尝试查找JSON代码块
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        return json_match.group(1).strip()

    # 优先匹配JSON数组
    array_match = re.search(r'(\[[\s\S]*\])', response)
    if array_match:
        return array_match.group(1).strip()

    # 其次匹配JSON对象
    obj_match = re.search(r'(\{[\s\S]*\})', response)
    if obj_match:
        return obj_match.group(1).strip()

    return response.strip()


def extract_and_repair_json(llm_response: str) -> Union[Dict[str, Any], list]:
    """
    从大模型响应中提取并修复JSON。
    
    解析策略（按优先级）：
    1. 尝试标准json.loads()
    2. 提取JSON片段后尝试json5.loads()（更宽容）
    3. 使用json_repair修复后再解析
    4. 最后使用标准json.loads()

    Args:
        llm_response: 大模型的原始响应文本

    Returns:
        解析后的JSON对象（字典或列表）

    Raises:
        ValueError: 如果无法解析为有效的JSON
    """
    # 先尝试直接解析（标准JSON）
    try:
        return json.loads(llm_response)
    except json.JSONDecodeError:
        pass
    
    # 提取 JSON 片段
    try:
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$'
        match = re.search(json_pattern, llm_response)

        if match:
            json_str = match.group(1) or match.group(2)
        else:
            start = llm_response.find('{')
            end = llm_response.rfind('}')
            if start >= 0 and end > start:
                json_str = llm_response[start:end+1]
            else:
                # 尝试查找数组
                start = llm_response.find('[')
                end = llm_response.rfind(']')
                if start >= 0 and end > start:
                    json_str = llm_response[start:end+1]
                else:
                    raise ValueError("无法从响应中提取JSON")
        
        # 策略1: 尝试json5（最宽容）
        if json5_available:
            try:
                result = json5.loads(json_str)
                return result
            except Exception:
                pass
        
        # 策略2: 尝试json_repair修复
        if json_repair_available:
            try:
                repaired = repair_json(json_str)
                return json.loads(repaired)
            except Exception:
                pass
        
        # 策略3: 最后尝试标准JSON
        try:
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(
                f"无法解析为有效的JSON:\n"
                f"  错误: {str(e)}\n"
                f"  提取的JSON: {json_str[:200]}...\n"
                f"  原始响应: {llm_response[:300]}...\n"
                f"  可用解析器: json5={json5_available}, json_repair={json_repair_available}"
            )
            
    except Exception as e:
        if "无法解析为有效的JSON" in str(e):
            raise
        raise ValueError(f"JSON提取失败: {str(e)}\n原始响应: {llm_response[:500]}...")


def clean_json_response(response: str) -> str:
    """
    清理 LLM 返回的响应，移除可能的 markdown 代码块标记
    
    Args:
        response: 原始响应文本
        
    Returns:
        清理后的文本
    """
    response = response.strip()
    
    # 移除可能的 markdown 代码块标记
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    return response.strip()


# Prompt模板常量
STRUCTURED_EXTRACTION_PROMPT = """
<instruction>
你是一个专业的信息提取助手。
请从提供的文本中提取信息，并严格按照提供的 JSON Schema 返回结果。
</instruction>

<input_text>
{text_input}
</input_text>

<json_schema>
{schema}
</json_schema>

<requirements>
1. 必须返回有效的 JSON 对象
2. 严格遵守上述 Schema 的字段定义和类型约束
3. 如果某个字段信息在文本中不存在，请设置为 null
4. 只返回 JSON 对象，不要包含任何其他说明文字或markdown代码块标记
</requirements>

<output_format>
请以纯 JSON 格式返回提取结果。
</output_format>
"""

REPAIR_PROMPT = """
<instruction>
以下 JSON 格式有误或不符合要求的 Schema，请根据错误信息修复它。
</instruction>

<original_json>
{original_response}
</original_json>

<validation_error>
{error_message}
</validation_error>

<target_schema>
{schema}
</target_schema>

<requirements>
1. 仔细阅读验证错误信息
2. 对照目标 Schema 修复 JSON
3. 确保所有字段类型正确
4. 只返回修复后的 JSON 对象，不要包含任何解释或markdown代码块标记
</requirements>

<output_format>
请返回修复后的纯 JSON 对象。
</output_format>
"""


if __name__ == "__main__":
    # 测试代码
    print("=== Prompt Utils 测试 ===\n")
    
    # 测试 JSON 提取
    test_response = """
    这是提取的结果：
    ```json
    {
        "name": "测试",
        "value": 123
    }
    ```
    """
    
    extracted = extract_json_from_response(test_response)
    print("提取的JSON:")
    print(extracted)
    
    # 测试变量填充
    template = "你好，{{name}}！今天是{{date}}。"
    variables = {"name": "用户", "date": "2025-10-10"}
    filled = fill_prompt_with_variables(template, variables)
    print(f"\n填充后的模板:\n{filled}")
