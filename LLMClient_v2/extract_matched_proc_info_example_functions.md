# `extract_matched_proc_info_example.py` 函数说明

逐个说明示例脚本中的关键类与函数，涵盖用途、主要输入以及返回值/副作用，便于快速理解批处理示例的执行链路。

## `ProcurementExtractionExecutor`

### `__init__(self, df, client, model, *, temperature=0.1)`
- 作用：缓存要处理的 DataFrame、结构化 LLM 客户端和模型配置，并提前生成字段说明文本，供后续 Prompt 渲染使用。
- 输入：
  - `df (pd.DataFrame)`：包含采购文本的原始数据。
  - `client (StructuredLLMClient)`：已配置的结构化调用客户端。
  - `model (str)`：目标模型名称。
  - `temperature (float)`：LLM 采样温度。
- 输出：无返回值；在实例上保存 prompt 所需的 schema 信息。

### `_build_field_explanations(schema)`
- 作用：把 Pydantic schema 的字段描述转写成多行字符串，帮助提示词中解释各字段意图。
- 输入：`schema (dict)`：`ProcurementInfo` 导出的 JSON schema。
- 输出：`str`，包含每个字段的名称、类型和说明。

### `_extract_row_index(unique_id)`
- 作用：从任务唯一 ID（形如 `matched_row_123`）解析出原始数据行下标。
- 输入：`unique_id (str)`。
- 输出：`Optional[int]`，成功解析返回整数下标，失败返回 `None`。

### `get_payload(self, unique_id)`
- 作用：根据任务 ID 获取该行的文本内容，构造批处理执行所需 payload。
- 输入：`unique_id (str)`。
- 输出：`dict`，包含 `row_index` 与 `text`。若 ID 非法或越界会抛出 `ValueError`。

### `execute(self, context)`
- 作用：真正调用 LLM 做结构化提取，并根据执行结果构造 `TaskExecutionResult`。
- 输入：`context (BatchExecutionContext)`：提供 unique_id、批次数、payload 等信息。
- 输出：`TaskExecutionResult`（异步返回）；成功时携带 call_id 与日志，失败时附带错误描述并请求重试。

### `_fetch_session_record(self, unique_id)`
- 作用：从 LLM 客户端的 tracker 中找到与当前任务关联的最后一次调用记录。
- 输入：`unique_id (str)`。
- 输出：`Optional[dict]`，返回日志记录字典或 `None`。

### `_build_log_record(session_record, unique_id, batch_info)`
- 作用：把 session 信息整合成批次日志结构，附带请求/响应、用量等字段。
- 输入：
  - `session_record (dict|None)`：结构化 LLM 的调用记录。
  - `unique_id (str)`。
  - `batch_info (dict)`：包含批次号、批内索引等。
- 输出：`dict`，可直接写入批次日志文件。

## 顶层工具函数

### `build_arg_parser()`
- 作用：创建 CLI 参数解析器，支持输入路径、批大小、模型等可配置项。
- 输入：无。
- 输出：`argparse.ArgumentParser` 实例。

### `ensure_directories(state_file, output_dir, logs_dir)`
- 作用：确保状态文件、输出和日志目录存在。
- 输入：三个路径字符串。
- 输出：无返回值；发生在文件系统上的副作用是创建目录。

### `initialise_tasks(task_manager, limit)`
- 作用：在第一次运行时根据数据行数初始化任务状态；若已有状态则打印摘要并跳过。
- 输入：
  - `task_manager (BatchTaskManager)`。
  - `limit (int)`：需要生成的任务数量。
- 输出：无返回值；调用 `TaskManager` 的初始化逻辑并打印统计信息。

### `export_success_results(task_manager, df, log_file, output_dir)`
- 作用：把成功任务的解析结果汇总成 JSON/CSV，并记录解析失败样本。
- 输入：
  - `task_manager (BatchTaskManager)`。
  - `df (pd.DataFrame)`：原始数据。
  - `log_file (str)`：LLM 活动日志路径。
  - `output_dir (str)`：输出目录。
- 输出：无返回值；在磁盘上写入结果文件并输出统计日志。

### `parse_response(raw_response)`
- 作用：多阶段解析 LLM 返回文本，优先使用 Pydantic 校验，失败时退化为 JSON5 解析。
- 输入：`raw_response (str)`。
- 输出：`Tuple[dict|None, ProcurementInfo|None, str|None]`：依次为可用的字典结果、成功的 Pydantic 对象以及错误信息。

### `resolve_parsing_method(validated, error_msg)`
- 作用：根据解析是否通过 Pydantic 判断解析方式，用于结果标记。
- 输入：
  - `validated (ProcurementInfo|None)`。
  - `error_msg (str|None)`。
- 输出：`str`，可能为 `"pydantic_direct"`, `"pydantic_fallback"`, `"json5_only"` 或 `"unknown"`。

### `sanitize_response_text(raw)`
- 作用：清洗带有代码块包裹或前后噪声的响应文本，提取纯 JSON 字符串。
- 输入：`raw (str)`。
- 输出：`str`，已清洗的文本。

### `json5_loads(text)`
- 作用：提供 JSON5 与标准 JSON 的统一入口。
- 输入：`text (str)`。
- 输出：解析后的 Python 对象；如果未安装 `json5` 则退回 `json.loads`。

## 入口函数

### `async def main()`
- 作用：串联 CLI 流程——解析参数、载入数据、构造执行器和批处理管理器、初始化任务、启动批处理并导出结果。
- 输入：无（读取命令行参数）。
- 输出：无直接返回值；驱动完整的示例流程。

### `if __name__ == "__main__": asyncio.run(main())`
- 作用：允许脚本直接运行时启动异步 `main` 函数。
- 输入/输出：无；触发脚本入口。
