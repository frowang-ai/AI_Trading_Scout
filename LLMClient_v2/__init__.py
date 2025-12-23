"""
LLMClient - 工程化的大模型调用客户端

主要功能：
- 异步LLM调用（基于AsyncOpenAI）
- 多供应商支持（云雾、Deepseek、WD等）
- 完整的调用日志记录（每次调用生成唯一ID）
- Token使用量和成本追踪
- 基于Pydantic的结构化数据提取
- 自动验证和修复机制
- 阶段路由配置

使用示例：
    from LLMClient import LLMClient, StructuredLLMClient
    from LLMClient.models import ProcurementInfo
    
    # 基础文本调用
    client = LLMClient(api_name="yunwu_gemini")
    response = await client.get_completion(prompt="你好")
    
    # 结构化数据提取
    structured_client = StructuredLLMClient(api_name="yunwu_gemini")
    result = await structured_client.get_structured_completion(
        text_input="某市医院采购设备...",
        response_model=ProcurementInfo
    )
"""

__version__ = "1.0.0"

# 导入配置管理
from .llm_config import (
    LLM_CONFIG,
    CURRENT_API,
    LLM_STAGE_ROUTING,
    get_api_config,
    get_route_for_stage,
    list_available_apis,
    list_available_providers,
)

# 导入追踪器
from .token_usage_tracker import (
    TokenUsageTracker,
    TokenUsage,
    ModelPricing,
    ModelPricingConfig,
)

# 导入客户端
from .llm_client import (
    LLMClient,
    LLMResponse,
)

from .structured_llm_client import (
    StructuredLLMClient,
)

# 导入工具函数
from .prompt_utils import (
    fill_prompt_with_document,
    fill_prompt_with_variables,
    get_prompt_template_path,
    load_prompt_template,
    render_prompt_template,
    extract_json_from_response,
    extract_and_repair_json,
    clean_json_response,
)

# 导入任务管理器
from .task_manager import (
    TaskManager,
    BatchTaskManager,
    BatchTaskExecutor,
    BatchExecutionContext,
    TaskExecutionResult,
    LLMActivityLog,
)

# 导入示例模型
from .models import (
    ProcurementInfo,
)

__all__ = [
    # 配置
    "LLM_CONFIG",
    "CURRENT_API",
    "LLM_STAGE_ROUTING",
    "get_api_config",
    "get_route_for_stage",
    "list_available_apis",
    "list_available_providers",
    
    # 追踪器
    "TokenUsageTracker",
    "TokenUsage",
    "ModelPricing",
    "ModelPricingConfig",
    
    # 客户端
    "LLMClient",
    "LLMResponse",
    "StructuredLLMClient",
    
    # 任务管理
    "TaskManager",
    "BatchTaskManager",
    "BatchTaskExecutor",
    "BatchExecutionContext",
    "TaskExecutionResult",
    "LLMActivityLog",
    
    # 工具函数
    "fill_prompt_with_document",
    "fill_prompt_with_variables",
    "get_prompt_template_path",
    "load_prompt_template",
    "render_prompt_template",
    "extract_json_from_response",
    "extract_and_repair_json",
    "clean_json_response",
    
    # 示例模型
    "ProcurementInfo",
]
