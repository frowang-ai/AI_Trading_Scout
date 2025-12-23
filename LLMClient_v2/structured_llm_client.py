#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
结构化LLM客户端

继承自LLMClient，提供基于Pydantic的结构化数据提取功能
支持自动验证和修复
"""

import json
from typing import Type, Optional, TypeVar
from pydantic import BaseModel, ValidationError

from .llm_client import LLMClient, LLMResponse
from .prompt_utils import (
    clean_json_response,
    STRUCTURED_EXTRACTION_PROMPT,
    REPAIR_PROMPT
)

T = TypeVar('T', bound=BaseModel)


class StructuredLLMClient(LLMClient):
    """
    结构化LLM客户端
    
    在LLMClient的基础上增加：
    - 基于Pydantic模型的结构化数据提取
    - 自动JSON验证
    - 自动修复机制（当验证失败时）
    """
    
    def __init__(self, *args, **kwargs):
        """
        初始化结构化LLM客户端
        
        参数与LLMClient相同
        """
        super().__init__(*args, **kwargs)
        print(f"✅ StructuredLLMClient 已就绪（基于 {self.api_name}）")
    
    async def get_structured_completion(
        self,
        text_input: str,
        response_model: Type[T],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        enable_repair: bool = True,
        stage: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[T]:
        """
        获取结构化输出（核心方法）
        
        Args:
            text_input: 待处理的输入文本
            response_model: Pydantic模型类
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数（结构化输出建议使用较低温度，默认0.1）
            enable_repair: 是否启用自动修复机制
            stage: 阶段名称（用于路由）
            metadata: 额外的元数据
            
        Returns:
            验证后的Pydantic模型实例，失败返回None
        """
        # 为结构化输出设置较低的默认温度
        if temperature is None:
            temperature = 0.1
        
        # 生成JSON Schema
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
        
        # 构建Prompt
        prompt = STRUCTURED_EXTRACTION_PROMPT.format(
            text_input=text_input,
            schema=schema_str
        )
        
        # 第一次尝试：调用底层的get_completion
        print(f"🔄 正在调用 LLM 进行结构化提取（模型: {response_model.__name__}）...")
        
        # 合并元数据
        call_metadata = {
            "task": "structured_extraction",
            "response_model": response_model.__name__,
            "enable_repair": enable_repair
        }
        if metadata:
            call_metadata.update(metadata)
        
        response = await self.get_completion(
            prompt=prompt,
            model=model,
            temperature=temperature,
            stage=stage,
            metadata=call_metadata
        )
        
        if not response.success:
            print(f"❌ LLM调用失败: {response.error}")
            return None
        
        # 清理响应
        cleaned_response = clean_json_response(response.content)
        
        # 尝试验证
        try:
            extracted = response_model.model_validate_json(cleaned_response)
            print(f"✅ 结构化提取成功！")
            return extracted
        
        except ValidationError as e:
            print(f"⚠️ 第一次验证失败:")
            print(f"   错误: {e}")
            
            if not enable_repair:
                print("❌ 自动修复已禁用，返回 None")
                return None
            
            # 尝试自动修复
            return await self._repair_and_retry(
                original_response=cleaned_response,
                error=e,
                response_model=response_model,
                schema_str=schema_str,
                model=model,
                stage=stage,
                metadata=call_metadata
            )
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"   原始响应: {cleaned_response[:200]}...")
            return None
    
    async def _repair_and_retry(
        self,
        original_response: str,
        error: ValidationError,
        response_model: Type[T],
        schema_str: str,
        model: Optional[str] = None,
        stage: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[T]:
        """
        自动修复并重试
        
        Args:
            original_response: 原始响应
            error: 验证错误
            response_model: Pydantic模型类
            schema_str: JSON Schema字符串
            model: 模型名称
            stage: 阶段名称
            metadata: 元数据
            
        Returns:
            修复后的模型实例，失败返回None
        """
        print("🛠️ 正在尝试自动修复...")
        
        # 构建修复Prompt
        repair_prompt = REPAIR_PROMPT.format(
            original_response=original_response,
            error_message=str(error),
            schema=schema_str
        )
        
        # 合并元数据
        repair_metadata = {
            "task": "json_repair",
            "response_model": response_model.__name__,
            "original_error": str(error)
        }
        if metadata:
            repair_metadata.update(metadata)
        
        # 使用较低温度进行修复
        repair_response = await self.get_completion(
            prompt=repair_prompt,
            model=model,
            temperature=0,
            stage=stage,
            metadata=repair_metadata
        )
        
        if not repair_response.success:
            print(f"❌ 修复调用失败: {repair_response.error}")
            return None
        
        cleaned_repaired = clean_json_response(repair_response.content)
        
        # 第二次验证
        try:
            extracted = response_model.model_validate_json(cleaned_repaired)
            print("✅ 自动修复成功！")
            return extracted
        
        except ValidationError as final_e:
            print(f"❌ 修复后仍然验证失败: {final_e}")
            print(f"   原始响应: {original_response[:200]}...")
            print(f"   修复后响应: {cleaned_repaired[:200]}...")
            return None
        
        except json.JSONDecodeError as e:
            print(f"❌ 修复后JSON解析失败: {e}")
            print(f"   修复后响应: {cleaned_repaired[:200]}...")
            return None
    
    async def batch_structured_completion(
        self,
        items: list,
        response_model: Type[T],
        text_extractor: callable = None,
        **kwargs
    ) -> list:
        """
        批量结构化提取
        
        Args:
            items: 待处理的项目列表
            response_model: Pydantic模型类
            text_extractor: 从项目中提取文本的函数，如果为None则直接使用项目作为文本
            **kwargs: 传递给get_structured_completion的其他参数
            
        Returns:
            提取结果列表（成功的Pydantic对象，失败为None）
        """
        results = []
        
        for i, item in enumerate(items):
            print(f"\n处理项目 {i+1}/{len(items)}...")
            
            # 提取文本
            text_input = text_extractor(item) if text_extractor else str(item)
            
            # 调用结构化提取
            result = await self.get_structured_completion(
                text_input=text_input,
                response_model=response_model,
                metadata={"batch_index": i, "batch_total": len(items)},
                **kwargs
            )
            
            results.append(result)
        
        # 统计
        success_count = sum(1 for r in results if r is not None)
        print(f"\n✅ 批量处理完成: {success_count}/{len(items)} 成功")
        
        return results


# 测试代码
if __name__ == "__main__":
    import asyncio
    from pydantic import BaseModel, Field
    
    # 定义测试用的Pydantic模型
    class ProcurementInfo(BaseModel):
        """政府采购信息"""
        purchaser: Optional[str] = Field(None, description="采购方名称")
        winner: Optional[str] = Field(None, description="中标商名称")
        item_name: Optional[str] = Field(None, description="采购物品名称")
        quantity: Optional[int] = Field(None, description="采购数量")
        amount: Optional[float] = Field(None, description="中标金额（元）")
    
    async def test_structured_client():
        print("=== StructuredLLMClient 测试 ===\n")
        
        # 创建客户端
        client = StructuredLLMClient(
            api_name="yunwu_gemini",
            log_file="test_logs/test_structured_activity.jsonl"
        )
        
        # 测试文本
        test_text = """
        某市人民医院发布采购公告，采购医疗设备一批。
        经过公开招标，某医疗设备有限公司中标，
        采购数量为10台，中标金额为150000元。
        """
        
        # 调用结构化提取
        result = await client.get_structured_completion(
            text_input=test_text,
            response_model=ProcurementInfo,
            enable_repair=True
        )
        
        if result:
            print("\n提取结果:")
            print(result.model_dump_json(indent=2, ensure_ascii=False))
        else:
            print("\n提取失败")
        
        # 打印会话摘要
        print("\n会话摘要:")
        import json
        print(json.dumps(client.get_session_summary(), ensure_ascii=False, indent=2))
    
    # 运行测试
    asyncio.run(test_structured_client())
