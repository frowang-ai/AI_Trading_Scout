#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM客户端基类

提供异步LLM调用、自动重试、元数据日志记录和Token使用量追踪功能
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

# 尝试导入OpenAI库
try:
    from openai import AsyncOpenAI, APIConnectionError, APIError
    openai_available = True
except ImportError:
    print("警告: 未安装openai库，请使用 'pip install openai' 安装")
    openai_available = False

from .llm_config import get_api_config, get_route_for_stage, CURRENT_API
from .token_usage_tracker import TokenUsageTracker, TokenUsage


@dataclass
class LLMResponse:
    """LLM响应数据类"""
    success: bool
    content: str
    usage: Optional[TokenUsage] = None
    cost: Optional[Dict[str, float]] = None
    error: Optional[str] = None
    call_id: Optional[str] = None
    duration_ms: Optional[int] = None


class LLMClient:
    """
    LLM客户端基类
    
    特性：
    - 异步调用大模型API
    - 自动重试机制（指数退避）
    - 完整的元数据日志记录（每次调用都有唯一ID）
    - Token使用量和成本追踪
    - 空响应检测
    - 支持多供应商配置
    """
    
    def __init__(
        self, 
        api_name: Optional[str] = None,
        log_file: Optional[str] = None,
        enable_tracking: bool = True
    ):
        """
        初始化LLM客户端
        
        Args:
            api_name: API名称，如果为None则使用默认API（在llm_config.py中配置）
            log_file: 调用日志文件路径（.jsonl格式），如果为None则使用默认路径
            enable_tracking: 是否启用Token使用量追踪和日志记录
        """
        if not openai_available:
            raise ImportError("未安装openai库，无法初始化客户端")
        
        self.api_name = api_name or CURRENT_API
        self.config = get_api_config(self.api_name)
        
        # 提取配置信息
        self.provider = self.config.get("provider", "unknown")
        self.default_model = self.config["default_model"]
        self.default_temperature = self.config.get("temperature", 0.7)
        self.max_retries = self.config.get("max_retries", 5)
        self.retry_base_delay = self.config.get("retry_base_delay", 1)
        
        # 获取API密钥
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError(f"缺少API密钥，请在llm_config.py中为{self.api_name}配置api_key")
        
        # 初始化异步客户端
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.config["api_url"]
        )
        
        # 初始化追踪器
        self.enable_tracking = enable_tracking
        if self.enable_tracking:
            default_log_file = log_file or f"logs/llm_activity_{self.api_name}.jsonl"
            self.tracker = TokenUsageTracker(log_file=default_log_file)
        else:
            self.tracker = None
        
        print(f"✅ LLMClient 初始化成功:")
        print(f"   - API: {self.api_name}")
        print(f"   - Provider: {self.provider}")
        print(f"   - Default Model: {self.default_model}")
        print(f"   - Tracking: {'Enabled' if enable_tracking else 'Disabled'}")
    
    @classmethod
    def from_stage(
        cls, 
        stage_name: str, 
        fallback_api: Optional[str] = None,
        **kwargs
    ) -> "LLMClient":
        """
        根据阶段名称创建LLMClient
        
        从llm_config.py的LLM_STAGE_ROUTING中查找阶段对应的API配置
        
        Args:
            stage_name: 阶段名称（如 'metadata_extraction', 'report_generation'）
            fallback_api: 如果阶段未配置，使用此API作为回退
            **kwargs: 传递给__init__的其他参数
            
        Returns:
            配置好的LLMClient实例
        """
        route = get_route_for_stage(stage_name, default=fallback_api or CURRENT_API)
        api_name = route.get("api_name")
        return cls(api_name=api_name, **kwargs)
    
    def _generate_call_id(self) -> str:
        """生成唯一的调用ID（16位哈希）

        格式保持为 `call_<16 hex>`，以兼容现有日志前缀 `call_`。
        如果需要兼容历史的8位ID，旧的日志仍然保留在 logs/ 中，不受本方法影响。
        """
        return f"call_{uuid.uuid4().hex[:16]}"
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳（ISO 8601格式）"""
        return datetime.utcnow().isoformat() + 'Z'
    
    async def get_vision_completion(
        self,
        prompt: str,
        image_base64: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stage: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        获取包含图片的LLM完成结果（vision API）
        
        Args:
            prompt: 提示词
            image_base64: Base64编码的图片数据
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数，如果为None则使用默认温度
            stage: 阶段名称，用于路由覆盖（可选）
            metadata: 额外的元数据，会被记录到日志中（可选）
            
        Returns:
            LLMResponse对象，包含成功状态、内容、用量、成本等信息
        """
        # 生成调用ID和开始时间
        call_id = self._generate_call_id()
        timestamp_start = self._get_current_timestamp()
        start_time = asyncio.get_event_loop().time()
        
        # 解析阶段覆盖
        route_override = None
        if stage:
            route_override = get_route_for_stage(stage, default=self.api_name)
        
        # 确定最终使用的参数
        model_name = model or (route_override or {}).get("model") or self.default_model
        temperature_effective = (
            temperature
            if temperature is not None
            else (route_override or {}).get("temperature", self.default_temperature)
        )
        
        # 构建vision消息
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }]
        
        # 构建初始元数据记录
        call_record = {
            "call_id": call_id,
            "timestamp_start": timestamp_start,
            "api_name": self.api_name,
            "provider": self.provider,
            "model": model_name,
            "temperature": temperature_effective,
            "prompt": prompt,
            "prompt_length": len(prompt),
            "has_image": True,
            "image_size_bytes": len(image_base64),
            "stage": stage,
        }
        
        # 添加用户提供的额外元数据
        if metadata:
            call_record["metadata"] = metadata
        
        # 执行调用（带重试机制）
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                print(f"[{call_id}] 调用Vision API: {self.api_name}, 模型: {model_name}, 重试: {retries}/{self.max_retries}")
                
                response = await self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature_effective,
                )
                
                # 提取响应内容
                if hasattr(response, 'choices') and response.choices:
                    content = response.choices[0].message.content or ""
                else:
                    raise ValueError("API返回了意外的响应格式")
                
                # 检测空响应
                if not content.strip():
                    raise ValueError("Empty response from LLM")
                
                # 提取Token使用量
                usage = None
                if hasattr(response, 'usage') and response.usage:
                    usage = TokenUsage(
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens,
                        total_tokens=response.usage.total_tokens
                    )
                
                # 计算成本
                cost = None
                if usage and self.tracker:
                    cost = self.tracker.pricing_config.calculate_cost(
                        usage=usage,
                        model_name=model_name,
                        provider=self.provider
                    )
                
                # 计算耗时
                end_time = asyncio.get_event_loop().time()
                duration_ms = int((end_time - start_time) * 1000)
                timestamp_end = self._get_current_timestamp()
                
                # 补完调用记录
                call_record.update({
                    "timestamp_end": timestamp_end,
                    "duration_ms": duration_ms,
                    "status": "success",
                    "response": content,
                    "response_length": len(content),
                    "usage": usage.__dict__ if usage else None,
                    "cost": cost,
                    "error": None,
                    "retry_count": retries
                })
                
                # 记录到追踪器
                if self.tracker:
                    self.tracker.log_call_record(call_record)
                
                print(f"[{call_id}] ✅ Vision调用成功 ({duration_ms}ms)")
                if usage:
                    print(f"[{call_id}] Token: {usage.prompt_tokens}+{usage.completion_tokens}={usage.total_tokens}")
                if cost:
                    print(f"[{call_id}] Cost: ${cost.get('primary_cost', 0):.6f}")
                
                # 返回成功响应
                return LLMResponse(
                    success=True,
                    content=content,
                    usage=usage,
                    cost=cost,
                    error=None,
                    call_id=call_id,
                    duration_ms=duration_ms
                )
                
            except ValueError as e:
                # 空响应或格式错误
                if "Empty response from LLM" in str(e):
                    last_error = f"空响应: {str(e)}"
                    print(f"[{call_id}] ⚠️ 收到空响应，重试中...")
                else:
                    last_error = f"值错误: {str(e)}"
                    print(f"[{call_id}] ❌ 值错误: {e}")
                    break  # 格式错误不重试
                
            except APIConnectionError as e:
                last_error = f"连接错误: {str(e)}"
                print(f"[{call_id}] ⚠️ API连接失败: {e}")
                
            except APIError as e:
                last_error = f"API错误: {str(e)}"
                print(f"[{call_id}] ⚠️ API错误: {e}")
                
            except asyncio.TimeoutError:
                last_error = "请求超时"
                print(f"[{call_id}] ⚠️ 请求超时")
                
            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                print(f"[{call_id}] ❌ 未知错误: {e}")
                break  # 未知错误不重试
            
            # 重试逻辑
            retries += 1
            if retries <= self.max_retries:
                delay = self.retry_base_delay * (2 ** (retries - 1))
                print(f"[{call_id}] 等待 {delay} 秒后重试...")
                await asyncio.sleep(delay)
        
        # 所有重试都失败，记录失败
        end_time = asyncio.get_event_loop().time()
        duration_ms = int((end_time - start_time) * 1000)
        timestamp_end = self._get_current_timestamp()
        
        call_record.update({
            "timestamp_end": timestamp_end,
            "duration_ms": duration_ms,
            "status": "failure",
            "response": None,
            "response_length": 0,
            "usage": None,
            "cost": None,
            "error": last_error,
            "retry_count": retries
        })
        
        if self.tracker:
            self.tracker.log_call_record(call_record)
        
        print(f"[{call_id}] ❌ Vision调用失败: {last_error}")
        
        return LLMResponse(
            success=False,
            content="",
            usage=None,
            cost=None,
            error=last_error,
            call_id=call_id,
            duration_ms=duration_ms
        )
    
    async def get_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stage: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        获取LLM完成结果（核心方法）
        
        Args:
            prompt: 提示词
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数，如果为None则使用默认温度
            stage: 阶段名称，用于路由覆盖（可选）
            metadata: 额外的元数据，会被记录到日志中（可选）
            
        Returns:
            LLMResponse对象，包含成功状态、内容、用量、成本等信息
        """
        # 生成调用ID和开始时间
        call_id = self._generate_call_id()
        timestamp_start = self._get_current_timestamp()
        start_time = asyncio.get_event_loop().time()
        
        # 解析阶段覆盖
        route_override = None
        if stage:
            route_override = get_route_for_stage(stage, default=self.api_name)
        
        # 确定最终使用的参数
        model_name = model or (route_override or {}).get("model") or self.default_model
        temperature_effective = (
            temperature
            if temperature is not None
            else (route_override or {}).get("temperature", self.default_temperature)
        )
        
        # 构建初始元数据记录
        call_record = {
            "call_id": call_id,
            "timestamp_start": timestamp_start,
            "api_name": self.api_name,
            "provider": self.provider,
            "model": model_name,
            "temperature": temperature_effective,
            "prompt": prompt,
            "prompt_length": len(prompt),
            "stage": stage,
        }
        
        # 添加用户提供的额外元数据
        if metadata:
            call_record["metadata"] = metadata
        
        # 执行调用（带重试机制）
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                print(f"[{call_id}] 调用API: {self.api_name}, 模型: {model_name}, 重试: {retries}/{self.max_retries}")
                
                response = await self.client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature_effective,
                )
                
                # 提取响应内容
                if hasattr(response, 'choices') and response.choices:
                    content = response.choices[0].message.content or ""
                else:
                    raise ValueError("API返回了意外的响应格式")
                
                # 检测空响应
                if not content.strip():
                    raise ValueError("Empty response from LLM")
                
                # 提取Token使用量
                usage = None
                if hasattr(response, 'usage') and response.usage:
                    usage = TokenUsage(
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens,
                        total_tokens=response.usage.total_tokens
                    )
                
                # 计算成本
                cost = None
                if usage and self.tracker:
                    cost = self.tracker.pricing_config.calculate_cost(
                        usage=usage,
                        model_name=model_name,
                        provider=self.provider
                    )
                
                # 计算耗时
                end_time = asyncio.get_event_loop().time()
                duration_ms = int((end_time - start_time) * 1000)
                timestamp_end = self._get_current_timestamp()
                
                # 补完调用记录
                call_record.update({
                    "timestamp_end": timestamp_end,
                    "duration_ms": duration_ms,
                    "status": "success",
                    "response": content,
                    "response_length": len(content),
                    "usage": usage.__dict__ if usage else None,
                    "cost": cost,
                    "error": None,
                    "retry_count": retries
                })
                
                # 记录到追踪器
                if self.tracker:
                    self.tracker.log_call_record(call_record)
                
                print(f"[{call_id}] ✅ 调用成功 ({duration_ms}ms)")
                if usage:
                    print(f"[{call_id}] Token: {usage.prompt_tokens}+{usage.completion_tokens}={usage.total_tokens}")
                if cost:
                    print(f"[{call_id}] Cost: ${cost.get('primary_cost', 0):.6f}")
                
                # 返回成功响应
                return LLMResponse(
                    success=True,
                    content=content,
                    usage=usage,
                    cost=cost,
                    error=None,
                    call_id=call_id,
                    duration_ms=duration_ms
                )
                
            except ValueError as e:
                # 空响应或格式错误
                if "Empty response from LLM" in str(e):
                    last_error = f"空响应: {str(e)}"
                    print(f"[{call_id}] ⚠️ 收到空响应，重试中...")
                else:
                    last_error = f"值错误: {str(e)}"
                    print(f"[{call_id}] ❌ 值错误: {e}")
                    break  # 格式错误不重试
                
            except APIConnectionError as e:
                last_error = f"连接错误: {str(e)}"
                print(f"[{call_id}] ⚠️ API连接失败: {e}")
                
            except APIError as e:
                last_error = f"API错误: {str(e)}"
                print(f"[{call_id}] ⚠️ API错误: {e}")
                
            except asyncio.TimeoutError:
                last_error = "请求超时"
                print(f"[{call_id}] ⚠️ 请求超时")
                
            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                print(f"[{call_id}] ❌ 未知错误: {e}")
                break  # 未知错误不重试
            
            # 重试逻辑
            retries += 1
            if retries <= self.max_retries:
                delay = self.retry_base_delay * (2 ** (retries - 1))
                print(f"[{call_id}] 等待 {delay} 秒后重试...")
                await asyncio.sleep(delay)
        
        # 所有重试都失败，记录失败
        end_time = asyncio.get_event_loop().time()
        duration_ms = int((end_time - start_time) * 1000)
        timestamp_end = self._get_current_timestamp()
        
        call_record.update({
            "timestamp_end": timestamp_end,
            "duration_ms": duration_ms,
            "status": "failure",
            "response": None,
            "response_length": 0,
            "usage": None,
            "cost": None,
            "error": last_error,
            "retry_count": retries
        })
        
        if self.tracker:
            self.tracker.log_call_record(call_record)
        
        print(f"[{call_id}] ❌ 调用失败: {last_error}")
        
        return LLMResponse(
            success=False,
            content="",
            usage=None,
            cost=None,
            error=last_error,
            call_id=call_id,
            duration_ms=duration_ms
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        获取当前会话的统计摘要
        
        Returns:
            包含调用次数、成功率、总成本等信息的字典
        """
        if not self.tracker:
            return {"error": "Tracking is disabled"}
        return self.tracker.get_session_summary()
    
    def reset_session(self):
        """重置会话统计"""
        if self.tracker:
            self.tracker.reset_session()
            print("✅ 会话统计已重置")
    
    def export_session(self, output_file: str):
        """
        导出会话记录到JSON文件
        
        Args:
            output_file: 输出文件路径
        """
        if self.tracker:
            self.tracker.export_session_to_json(output_file)
    
    async def process_batch_with_manager(
        self,
        task_manager: 'TaskManager',
        input_data: Dict[str, str],
        prompt_template: Optional[str] = None,
        max_concurrent: int = 5,
        **llm_kwargs
    ) -> Dict[str, Any]:
        """
        使用 TaskManager 批量处理任务
        
        Args:
            task_manager: TaskManager 实例
            input_data: {unique_id: text} 的映射字典
            prompt_template: Prompt 模板（可选，用 {text} 占位符），如果为None则直接使用text
            max_concurrent: 最大并发数
            **llm_kwargs: 传递给 get_completion 的其他参数（如 temperature, model 等）
            
        Returns:
            处理摘要统计字典
            
        Example:
            task_mgr = TaskManager("tasks/batch.jsonl")
            input_data = {"doc_001": "文本1", "doc_002": "文本2"}
            
            summary = await client.process_batch_with_manager(
                task_manager=task_mgr,
                input_data=input_data,
                prompt_template="请处理：{text}",
                max_concurrent=10,
                temperature=0.7
            )
        """
        # 获取待处理任务
        pending_ids = task_manager.get_pending_tasks()
        
        if not pending_ids:
            print("✅ 没有待处理的任务")
            return task_manager.get_statistics()
        
        print(f"📋 开始处理 {len(pending_ids)} 个待处理任务...")
        print(f"⚙️  并发数: {max_concurrent}")
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # 处理单个任务的函数
        async def process_one(unique_id: str, index: int):
            async with semaphore:
                # 获取文本
                text = input_data.get(unique_id)
                if text is None:
                    error_msg = f"在 input_data 中找不到 unique_id: {unique_id}"
                    print(f"[{index}/{len(pending_ids)}] ❌ {unique_id}: {error_msg}")
                    task_manager.update_task_failure(unique_id, "N/A", error_msg)
                    return
                
                # 构建 prompt
                if prompt_template:
                    prompt = prompt_template.replace("{text}", text)
                else:
                    prompt = text
                
                # 调用 LLM
                print(f"[{index}/{len(pending_ids)}] 🔄 处理中: {unique_id}")
                
                response = await self.get_completion(
                    prompt=prompt,
                    metadata={"unique_id": unique_id},
                    **llm_kwargs
                )
                
                # 更新任务状态
                if response.success:
                    task_manager.update_task_success(unique_id, response.call_id)
                    print(f"[{index}/{len(pending_ids)}] ✅ 成功: {unique_id} (call_id: {response.call_id})")
                else:
                    task_manager.update_task_failure(unique_id, response.call_id or "N/A", response.error or "Unknown error")
                    print(f"[{index}/{len(pending_ids)}] ❌ 失败: {unique_id} - {response.error}")
        
        # 并发处理所有任务
        tasks = [
            process_one(uid, i+1) 
            for i, uid in enumerate(pending_ids)
        ]
        
        await asyncio.gather(*tasks)
        
        # 返回统计信息
        stats = task_manager.get_statistics()
        
        print("\n" + "="*60)
        print("批量处理完成")
        print("="*60)
        print(f"总任务数:   {stats['total']}")
        print(f"成功:       {stats['success']}")
        print(f"失败:       {stats['failed']}")
        print(f"待处理:     {stats['pending']}")
        print(f"成功率:     {stats['success_rate']*100:.1f}%")
        print("="*60 + "\n")
        
        return stats


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_client():
        print("=== LLMClient 测试 ===\n")
        
        # 创建客户端
        client = LLMClient(
            api_name="yunwu_gemini",
            log_file="test_logs/test_llm_activity.jsonl"
        )
        
        # 测试调用
        response = await client.get_completion(
            prompt="你好，请用一句话介绍自己。",
            temperature=0.7,
            metadata={"test": True, "purpose": "greeting"}
        )
        
        print(f"\n响应:")
        print(f"- 成功: {response.success}")
        print(f"- 内容: {response.content[:100]}...")
        print(f"- Call ID: {response.call_id}")
        
        if response.usage:
            print(f"- Token使用: {response.usage.total_tokens}")
        
        if response.cost:
            print(f"- 成本: ${response.cost.get('primary_cost', 0):.6f}")
        
        # 打印会话摘要
        print("\n会话摘要:")
        import json
        print(json.dumps(client.get_session_summary(), ensure_ascii=False, indent=2))
    
    # 运行测试
    asyncio.run(test_client())
