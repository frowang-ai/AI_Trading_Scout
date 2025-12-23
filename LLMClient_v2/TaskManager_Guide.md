# TaskManager 使用指南

## 📋 概述

`TaskManager` 是专为大规模批量LLM任务设计的状态管理系统，能够处理10万甚至百万级别的任务，支持断点续传和多轮重试。

## 🎯 核心概念

### 双文件系统

```
task_state.jsonl        # 状态管理（轻量级）
├── unique_id          # 原始数据ID
├── status             # pending | success | failed
├── llm_call_id        # 关联键
└── error / retry_count

llm_activity.jsonl      # 详细日志（LLMClient自动记录）
├── call_id            # 关联键
├── prompt / response  # 完整内容
└── usage / cost
```

**设计理念**：
- 状态文件只记录ID和状态（轻量级，快速加载）
- 详细日志记录完整信息（通过ID关联查询）
- 职责分离，互不干扰

## 🚀 快速开始

### 基础工作流

```python
from LLMClient import LLMClient, TaskManager

# 1. 准备数据
input_data = {
    "doc_001": "待处理文本1",
    "doc_002": "待处理文本2",
    "doc_003": "待处理文本3",
}

# 2. 初始化任务管理器
task_mgr = TaskManager(state_file="tasks/my_batch.jsonl")

# 3. 初始化任务（只在第一次运行时）
if not task_mgr.is_initialized():
    init_items = [{"unique_id": uid} for uid in input_data.keys()]
    task_mgr.initialize_tasks(init_items)

# 4. 创建LLM客户端
client = LLMClient(api_name="yunwu_gemini")

# 5. 批量处理
summary = await client.process_batch_with_manager(
    task_manager=task_mgr,
    input_data=input_data,
    prompt_template="请处理以下文本：\n{text}",
    max_concurrent=10,
    temperature=0.7
)

# 6. 查看统计
task_mgr.print_summary()
```

## 📝 状态文件结构

### task_state.jsonl（每行一个任务）

```jsonl
{"unique_id":"doc_001","status":"success","llm_call_id":"call_a1b2c3d4","error":null,"created_at":"2025-10-10T10:00:00Z","updated_at":"2025-10-10T10:05:23Z","retry_count":0}
{"unique_id":"doc_002","status":"failed","llm_call_id":"call_e5f6g7h8","error":"API连接超时","created_at":"2025-10-10T10:00:00Z","updated_at":"2025-10-10T10:05:45Z","retry_count":1}
{"unique_id":"doc_003","status":"pending","llm_call_id":null,"error":null,"created_at":"2025-10-10T10:00:00Z","updated_at":"2025-10-10T10:00:00Z","retry_count":0}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `unique_id` | string | 原始数据的唯一标识（用户提供） |
| `status` | string | 任务状态：pending / success / failed |
| `llm_call_id` | string\|null | LLM调用ID（用于关联到llm_activity.jsonl） |
| `error` | string\|null | 错误信息（失败时才有） |
| `created_at` | string | 任务创建时间（ISO 8601格式） |
| `updated_at` | string | 最后更新时间 |
| `retry_count` | int | 重试次数 |

## 🔄 多轮重试

### 场景：100个任务，第一轮成功50个，失败50个

```python
# 第一轮处理
task_mgr = TaskManager("tasks/batch.jsonl")
task_mgr.initialize_tasks(init_items)

await client.process_batch_with_manager(task_mgr, input_data)
# 结果：50 success, 50 failed

# 查看失败原因
failed_tasks = task_mgr.get_failed_tasks()
for task in failed_tasks:
    print(f"{task['unique_id']}: {task['error']}")

# 第二轮：重试失败的50个
task_mgr.reset_failed_tasks()  # 将 failed → pending
await client.process_batch_with_manager(task_mgr, input_data)
# 结果：新增成功20个，30个仍失败

# 最终状态：70 success, 30 failed
stats = task_mgr.get_statistics()
print(f"成功率: {stats['success_rate']*100:.1f}%")
```

### retry_count 自动递增

```jsonl
// 第一轮失败后
{"unique_id":"doc_002","status":"failed","retry_count":1,...}

// 第二轮成功后
{"unique_id":"doc_002","status":"success","retry_count":1,...}
```

## 💾 断点续传

### 场景：程序崩溃，处理到一半

```python
# 程序崩溃前：已处理30/100个任务

# 重启后
task_mgr = TaskManager("tasks/batch.jsonl")  # 自动加载现有状态

stats = task_mgr.get_statistics()
print(f"已完成: {stats['processed']}")  # 30
print(f"待处理: {stats['pending']}")     # 70

# 继续处理剩余的70个
await client.process_batch_with_manager(task_mgr, input_data)
```

## 🔗 结果合并

### 将LLM响应合并回原始数据

```python
from LLMClient import TaskManager, LLMActivityLog

# 1. 加载任务管理器
task_mgr = TaskManager("tasks/batch.jsonl")

# 2. 获取成功任务的映射
success_map = task_mgr.get_success_map()
# 返回: {"doc_001": "call_a1b2c3d4", "doc_003": "call_xyz789", ...}

# 3. 加载活动日志
activity_log = LLMActivityLog("logs/llm_activity.jsonl")

# 4. 合并结果
results = []
for unique_id, call_id in success_map.items():
    # 从日志中获取完整响应
    record = activity_log.get_response_by_call_id(call_id)
    
    if record:
        results.append({
            "unique_id": unique_id,
            "original_text": input_data[unique_id],  # 原始文本
            "llm_response": record['response'],      # LLM响应
            "tokens": record['usage']['total_tokens'],
            "cost": record['cost']['primary_cost']
        })

# 5. 保存合并结果
import json
with open("results/merged.json", 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

## 📊 统计和分析

### 基础统计

```python
stats = task_mgr.get_statistics()

print(f"总任务数:     {stats['total']}")
print(f"待处理:       {stats['pending']}")
print(f"成功:         {stats['success']}")
print(f"失败:         {stats['failed']}")
print(f"成功率:       {stats['success_rate']*100:.1f}%")
print(f"完成率:       {stats['completion_rate']*100:.1f}%")
```

### 高级统计（包含Token和成本）

```python
from LLMClient import LLMActivityLog

# 加载日志
activity_log = LLMActivityLog("logs/llm_activity.jsonl")
success_map = task_mgr.get_success_map()

# 收集统计
total_tokens = 0
total_cost = 0.0

for call_id in success_map.values():
    record = activity_log.get_response_by_call_id(call_id)
    if record:
        total_tokens += record['usage']['total_tokens']
        total_cost += record['cost']['primary_cost']

print(f"总Token消耗:  {total_tokens:,}")
print(f"总成本:       ${total_cost:.4f}")
print(f"平均Token:    {total_tokens/len(success_map):.1f}")
print(f"平均成本:     ${total_cost/len(success_map):.4f}")
```

## 🎯 TaskManager API 参考

### 初始化

```python
task_mgr = TaskManager(state_file="tasks/batch.jsonl")
```

### 核心方法

```python
# 初始化任务
task_mgr.initialize_tasks(
    items=[{"unique_id": "xxx"}, ...],
    force=False  # 是否强制重新初始化
)

# 获取待处理任务ID列表
pending_ids = task_mgr.get_pending_tasks(limit=100)

# 获取失败任务详情
failed = task_mgr.get_failed_tasks()

# 更新任务状态（通常由LLMClient自动调用）
task_mgr.update_task_success(unique_id, llm_call_id)
task_mgr.update_task_failure(unique_id, llm_call_id, error)

# 重置失败任务为待处理
count = task_mgr.reset_failed_tasks()

# 重置指定任务
count = task_mgr.reset_specific_tasks(["doc_001", "doc_002"])

# 获取统计信息
stats = task_mgr.get_statistics()

# 获取成功任务映射
success_map = task_mgr.get_success_map()

# 导出结果
task_mgr.export_results(
    output_file="results/tasks.json",
    status_filter="success",  # "pending" / "failed" / None
    format="json"  # "json" / "jsonl"
)

# 打印摘要
task_mgr.print_summary()
```

## 🏭 大规模处理最佳实践

### 处理100万+任务

```python
# 1. 分批初始化（避免内存溢出）
def batch_init(all_unique_ids, batch_size=10000):
    task_mgr = TaskManager("tasks/large_batch.jsonl")
    
    for i in range(0, len(all_unique_ids), batch_size):
        batch = all_unique_ids[i:i+batch_size]
        init_items = [{"unique_id": uid} for uid in batch]
        
        if i == 0:
            task_mgr.initialize_tasks(init_items, force=True)
        else:
            # 追加新任务（需自定义实现，或分多个文件）
            pass

# 2. 分批处理
async def process_large_batch():
    task_mgr = TaskManager("tasks/large_batch.jsonl")
    client = LLMClient(api_name="yunwu_gemini")
    
    batch_size = 1000
    
    while True:
        # 获取一批待处理任务
        pending = task_mgr.get_pending_tasks(limit=batch_size)
        
        if not pending:
            break
        
        # 准备这批任务的input_data（从数据库或文件读取）
        input_data = load_texts_for_ids(pending)
        
        # 处理
        await client.process_batch_with_manager(
            task_manager=task_mgr,
            input_data=input_data,
            max_concurrent=20
        )
        
        # 定期保存检查点
        task_mgr.print_summary()

# 3. 监控进度
stats = task_mgr.get_statistics()
progress = (stats['processed'] / stats['total']) * 100
print(f"进度: {progress:.1f}%")
```

### 并发控制建议

| 任务规模 | 并发数 | 说明 |
|---------|--------|------|
| < 1,000 | 5-10 | 快速处理 |
| 1,000 - 10,000 | 10-20 | 平衡速度和稳定性 |
| 10,000 - 100,000 | 20-50 | 需要监控API限流 |
| > 100,000 | 分批处理 | 每批1000-10000，设置并发20-50 |

## 🐛 故障排查

### 问题：状态文件损坏

```python
# 从llm_activity.jsonl重建状态文件
def rebuild_state():
    activity_log = LLMActivityLog("logs/llm_activity.jsonl")
    # 自定义重建逻辑
```

### 问题：重复任务

```python
# 初始化时会检查unique_id唯一性
try:
    task_mgr.initialize_tasks(items)
except ValueError as e:
    print(f"错误: {e}")  # "存在重复的 unique_id"
```

### 问题：查看某个任务的完整历史

```python
# 获取所有尝试记录
activity_log = LLMActivityLog("logs/llm_activity.jsonl")
history = activity_log.get_responses_by_unique_id("doc_001")

for i, record in enumerate(history, 1):
    print(f"尝试 {i}: {record['status']} at {record['timestamp_end']}")
```

## 📚 完整示例

查看 `task_manager_examples.py` 获取更多完整示例：
- 基础批量处理
- 断点续传和重试
- 结果合并
- 高级统计
- 大规模处理

```bash
python task_manager_examples.py
```
