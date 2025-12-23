# LLMClient - 工程化的大模型调用客户端

一个遵循 Python 最佳实践的、工程化的 LLM 调用客户端，支持多供应商、完整日志追踪、成本计算和结构化数据提取。

## ✨ 核心特性

### 1. **基础 LLM 调用 (`LLMClient`)**
- ✅ 异步调用（基于 `AsyncOpenAI`）
- ✅ 自动重试机制（指数退避）
- ✅ 空响应检测
- ✅ 完整的元数据日志（每次调用生成唯一 ID，支持追溯）
- ✅ Token 使用量统计
- ✅ 多供应商成本计算（云雾专用公式 + 标准计费）

### 2. **结构化数据提取 (`StructuredLLMClient`)**
- ✅ 基于 Pydantic 的数据验证
- ✅ 自动生成 JSON Schema Prompt
- ✅ 验证失败时自动修复（二次调用 LLM）
- ✅ 批量处理支持

### 3. **批量任务管理 (`TaskManager`)**
- ✅ 大规模批量处理支持（10万+ 任务）
- ✅ 状态追踪（pending / success / failed）
- ✅ 断点续传（程序崩溃后恢复）
- ✅ 多轮重试支持
- ✅ 完整的统计和报告

### 4. **多供应商支持**
- ✅ 云雾 AI（Gemini、GPT、Deepseek）
- ✅ Deepseek 官方
- ✅ WD 渠道
- ✅ 配置化设计，易于扩展

### 5. **阶段路由**
- ✅ 为不同任务配置不同的 API/模型/温度
- ✅ 支持快速切换

## 📦 安装依赖

```bash
# 推荐使用uv
uv add openai pydantic json5 json-repair

# 或使用pip
pip install openai pydantic json5 json-repair
```

**依赖说明**：
- `openai`: 异步LLM API调用
- `pydantic`: 数据验证和Schema生成
- `json5`: 宽容的JSON解析（支持注释、尾部逗号等）
- `json-repair`: JSON自动修复（处理格式错误）

## 🚀 快速开始

### 基础文本调用

```python
import asyncio
from LLMClient import LLMClient

async def main():
    # 创建客户端
    client = LLMClient(
        api_name="yunwu_gemini",  # 使用云雾的 Gemini
        log_file="logs/my_app.jsonl"  # 日志文件路径
    )
    
    # 调用 LLM
    response = await client.get_completion(
        prompt="请用一句话介绍 Python",
        temperature=0.7,
        metadata={"user_id": "12345", "session": "test"}  # 可选的额外元数据
    )
    
    if response.success:
        print(f"回复: {response.content}")
        print(f"Token: {response.usage.total_tokens}")
        print(f"成本: ${response.cost['primary_cost']:.6f}")
        print(f"调用ID: {response.call_id}")
    else:
        print(f"调用失败: {response.error}")

asyncio.run(main())
```

### 结构化数据提取

```python
import asyncio
from LLMClient import StructuredLLMClient
from LLMClient.models import ProcurementInfo

async def main():
    # 创建结构化客户端
    client = StructuredLLMClient(api_name="yunwu_gemini")
    
    # 待提取的文本
    text = """
    某市人民医院发布采购公告，采购医疗设备一批。
    经过公开招标，某医疗设备有限公司中标，
    采购数量为10台，中标金额为150000元。
    """
    
    # 提取结构化数据
    result = await client.get_structured_completion(
        text_input=text,
        response_model=ProcurementInfo,  # Pydantic 模型
        enable_repair=True  # 启用自动修复
    )
    
    if result:
        print(result.model_dump_json(indent=2, ensure_ascii=False))
        # 输出:
        # {
        #   "purchaser": "某市人民医院",
        #   "winner": "某医疗设备有限公司",
        #   "item_name": "医疗设备",
        #   "quantity": 10,
        #   "amount": 150000.0
        # }

asyncio.run(main())
```

### 使用阶段路由

```python
# 为特定阶段创建客户端（自动从 llm_config.py 读取配置）
client = LLMClient.from_stage("metadata_extraction")

response = await client.get_completion(
    prompt="...",
    stage="metadata_extraction"  # 会覆盖 model 和 temperature
)
```

### 自定义 Pydantic 模型

```python
from pydantic import BaseModel, Field
from typing import Optional

class MyDataModel(BaseModel):
    """你的自定义数据模型"""
    name: str = Field(..., description="名称")
    value: Optional[float] = Field(None, description="数值")

# 使用
result = await client.get_structured_completion(
    text_input="...",
    response_model=MyDataModel
)
```

## 📊 日志和追踪

### 调用日志格式

每次调用都会生成一条 JSON Lines 格式的日志：

```json
{
  "call_id": "call_a1b2c3d4",
  "timestamp_start": "2025-10-10T10:30:01.123Z",
  "timestamp_end": "2025-10-10T10:30:03.456Z",
  "duration_ms": 2333,
  "status": "success",
  "api_name": "yunwu_gemini",
  "provider": "yunwu",
  "model": "gemini-2.5-pro",
  "temperature": 0.7,
  "prompt": "...",
  "response": "...",
  "usage": {
    "prompt_tokens": 512,
    "completion_tokens": 128,
    "total_tokens": 640
  },
  "cost": {
    "yunwu_formula_cost": 0.0015,
    "standard_cost": 0.0019,
    "primary_cost": 0.0015,
    "currency": "USD"
  },
  "error": null,
  "metadata": {"user_id": "12345"}
}
```

### 查看会话统计

```python
# 获取当前会话的统计摘要
summary = client.get_session_summary()
print(summary)
# {
#   "total_calls": 10,
#   "successful_calls": 9,
#   "failed_calls": 1,
#   "success_rate": 0.9,
#   "total_usage": {"prompt_tokens": 5000, "completion_tokens": 1200, ...},
#   "total_cost": 0.0234,
#   "average_cost_per_call": 0.00234
# }

# 导出会话记录
client.export_session("session_report.json")

# 重置统计
client.reset_session()
```

## ⚙️ 配置管理

### 在 `llm_config.py` 中添加新的 API

```python
LLM_CONFIG = {
    "my_new_api": {
        "provider": "my_provider",  # 供应商名称
        "api_url": "https://api.example.com/v1",
        "api_key": "sk-xxxxxxxxxxxx",
        "default_model": "my-model",
        "temperature": 0.7,
        "max_retries": 5,
        "retry_base_delay": 1,
    },
    # ...
}
```

### 配置阶段路由

```python
LLM_STAGE_ROUTING = {
    "quick_task": "deepseek",  # 简写：只指定 API
    "complex_task": {  # 扩展：指定 API、模型和温度
        "api": "yunwu_gemini",
        "model": "gemini-2.5-pro",
        "temperature": 0.7
    },
}
```

## 🏗️ 架构设计

```
LLMClient/
├── llm_config.py              # 配置管理（API、路由）
├── token_usage_tracker.py     # Token 统计和成本计算
├── prompt_utils.py            # Prompt 工具（填充、JSON 提取）
├── llm_client.py              # 基础 LLM 客户端（核心）
├── structured_llm_client.py   # 结构化客户端（继承 LLMClient）
├── models.py                  # Pydantic 模型示例
└── __init__.py                # 包导出
```

### 类继承关系

```
LLMClient (基类)
    ↓ 继承
StructuredLLMClient (增强类)
```

### 核心流程

1. **LLMClient.get_completion()**
   - 生成 call_id 和元数据
   - 调用 AsyncOpenAI
   - 提取 Token 使用量
   - 计算成本（根据 provider）
   - 记录日志到 TokenUsageTracker
   - 返回 LLMResponse

2. **StructuredLLMClient.get_structured_completion()**
   - 生成包含 JSON Schema 的 Prompt
   - 调用 `super().get_completion()`
   - 验证响应（Pydantic）
   - 如果失败且启用修复：生成修复 Prompt → 再次调用 → 再次验证
   - 返回验证后的 Pydantic 对象

## 💡 最佳实践

### 1. 为不同任务创建不同的客户端实例

```python
# 快速任务使用 Deepseek
quick_client = LLMClient(api_name="deepseek")

# 复杂任务使用 GPT-5
complex_client = LLMClient(api_name="yunwu_gpt5")
```

### 2. 使用较低温度进行结构化提取

```python
result = await client.get_structured_completion(
    text_input=text,
    response_model=MyModel,
    temperature=0.1  # 低温度提高稳定性
)
```

### 3. 利用元数据追溯问题

```python
response = await client.get_completion(
    prompt="...",
    metadata={
        "user_id": "user123",
        "document_id": "doc456",
        "operation": "extract_metadata"
    }
)

# 后续可以通过 call_id 或 metadata 在日志中快速定位
```

### 4. 定期导出和分析日志

```python
# 处理完一批任务后
client.export_session("reports/batch_001.json")
client.reset_session()
```

## 🔧 扩展

### 添加新的成本计算逻辑

在 `token_usage_tracker.py` 的 `ModelPricingConfig.calculate_cost()` 中：

```python
def calculate_cost(self, usage, model_name, provider, ...):
    # 标准计算
    standard_cost = ...
    
    # 云雾专用计算
    if provider == "yunwu":
        yunwu_cost = ...
    
    # 添加你的供应商
    if provider == "my_provider":
        my_cost = ...
        result["my_formula_cost"] = my_cost
        result["primary_cost"] = my_cost
    
    return result
```

## 📝 License

MIT

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
