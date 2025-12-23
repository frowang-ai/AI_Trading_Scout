#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**整体流程**
- `main` 入口解析命令行参数，确保状态文件/输出/日志目录完整，然后按 limit 读取 CSV 数据 `LLMClient_v2/extract_matched_proc_info_example.py:206`.
- 构建 `StructuredLLMClient`，将日志输出指向本次会话文件；用数据集、模型配置初始化 `ProcurementExtractionExecutor`，再用它组装 `BatchTaskManager` 以驱动批量处理 `LLMClient_v2/extract_matched_proc_info_example.py:222`.
- 调用 `initialise_tasks` 生成或加载形如 `matched_row_{idx}` 的任务列表，实现断点续传式的状态管理 `LLMClient_v2/extract_matched_proc_info_example.py:238`.
- 异步执行 `task_manager.process_pending_tasks`：任务被分批、并发调度，每条任务由 executor 的 `execute` 方法拉取文本、渲染提示词并调用 LLM，随后把 `TaskExecutionResult` 回写状态与批次日志 `LLMClient_v2/extract_matched_proc_info_example.py:247`.
- 批处理结束后打印统计信息，并用 `export_success_results` 遍历成功任务映射，结合活动日志解析响应，输出 JSON/CSV 结果并记录失败样本 `LLMClient_v2/extract_matched_proc_info_example.py:255`.

**执行器职责**
- `get_payload` 根据任务 ID 找到 DataFrame 行，返回文本与行号；`execute` 负责 Prompt 渲染、调用 LLM、处理异常及构造日志；内部依赖 `_fetch_session_record`、`_build_log_record` 将 LLM 调用上下文附着在任务结果上，便于追溯 `LLMClient_v2/extract_matched_proc_info_example.py:71`.

**响应解析与导出**
- `parse_response` 通过 pydantic→JSON5→原始解析的多层兜底策略把字符串响应转为结构化数据，并给出成功/失败标签；`resolve_parsing_method` 标记使用的解析途径；`sanitize_response_text`、`json5_loads` 提供辅助清洗与解析 `LLMClient_v2/extract_matched_proc_info_example.py:320`.

**控制命令行**
- `build_arg_parser` 定义所有可调参数（输入路径、批大小、模型、并发度等），使脚本可按需复现不同规模测试 `LLMClient_v2/extract_matched_proc_info_example.py:167`.

如需继续探索，可以 1) 在少量样本上运行脚本观察日志/状态文件产物，2) 将 executor 改造成处理自定义结构化任务，复用同一批处理骨架。

"""

import argparse
import importlib.util
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import json5  # type: ignore
except ImportError:
    json5 = None  # type: ignore

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
# package是python的一个内置属性，用于标识模块所属的包
# 保证在作为脚本直接运行时，能够正确导入同一目录下的模块
if __package__ in (None, ""):
    parent_dir = CURRENT_DIR.parent
    sys.path.insert(0, str(parent_dir))

    tm_spec = importlib.util.spec_from_file_location("task_manager_module", CURRENT_DIR / "task_manager.py")
    if tm_spec is None or tm_spec.loader is None:
        raise ImportError("无法加载 task_manager.py")
    task_manager_module = importlib.util.module_from_spec(tm_spec)
    tm_spec.loader.exec_module(task_manager_module)
    BatchExecutionContext = task_manager_module.BatchExecutionContext  # type: ignore[attr-defined]
    BatchTaskExecutor = task_manager_module.BatchTaskExecutor  # type: ignore[attr-defined]
    BatchTaskManager = task_manager_module.BatchTaskManager  # type: ignore[attr-defined]
    TaskExecutionResult = task_manager_module.TaskExecutionResult  # type: ignore[attr-defined]
    LLMActivityLog = task_manager_module.LLMActivityLog  # type: ignore[attr-defined]

    from LLMClient_v2.models import ProcurementInfo  # type: ignore
    from LLMClient_v2.prompt_utils import render_prompt_template  # type: ignore
    from LLMClient_v2.structured_llm_client import StructuredLLMClient  # type: ignore
else:
    from .task_manager import (
        BatchExecutionContext,
        BatchTaskExecutor,
        BatchTaskManager,
        TaskExecutionResult,
        LLMActivityLog,
    )
    from .models import ProcurementInfo
    from .prompt_utils import render_prompt_template
    from .structured_llm_client import StructuredLLMClient


TEMPLATE_NAME = "matched_procurement_extraction"


class ProcurementExtractionExecutor(BatchTaskExecutor):
    """执行实际的结构化提取任务"""

    def __init__(
        self,
        df: pd.DataFrame,
        client: StructuredLLMClient,
        model: str,
        *,
        temperature: float = 0.1,
    ):
        """初始化提取执行器，缓存数据源与 LLM 客户端配置并生成字段说明。

        Args:
            df: 含原始采购文本的 DataFrame。
            client: 结构化调用客户端。
            model: 使用的模型名称。
            temperature: LLM 请求温度。
        """
        self.df = df
        self.client = client
        self.model = model
        self.temperature = temperature

        schema = ProcurementInfo.model_json_schema()
        self.schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
        self.field_explanations = self._build_field_explanations(schema)

    @staticmethod
    def _build_field_explanations(schema: Dict[str, object]) -> str:
        """将 schema 字段定义转换成提示词用的说明文本。
        在最后输入到prompt里面的时候，我们是既有json schema，也有这个文本说明，文本说明起辅助作用。

        Args:
            schema: `ProcurementInfo` 的 JSON schema。

        Returns:
            str: 字段说明多行文本。
        """
        properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
        explanations = []
        for field_name, field_info in properties.items():
            if not isinstance(field_info, dict):
                continue
            desc = field_info.get("description", "")
            field_type = field_info.get("type", "any")
            if field_type == "array":
                items_type = field_info.get("items", {}).get("type", "any")
                field_type = f"array of {items_type}"
            if field_name in ("quantity", "amount") and "minimum" in field_info:
                field_type = f"{field_type} (>= {field_info['minimum']})"
            explanations.append(f"{field_name} ({field_type}): {desc}")
        return "\n".join(explanations)

    @staticmethod
    def _extract_row_index(unique_id: str) -> Optional[int]:
        """从任务唯一 ID 中解析原始行下标。

        Args:
            unique_id: 形如 ``matched_row_123`` 的标识。

        Returns:
            行号整数；解析失败时返回 ``None``。
        """
        if not unique_id.startswith("matched_row_"):
            return None
        try:
            return int(unique_id.replace("matched_row_", ""))
        except ValueError:
            return None

    def get_payload(self, unique_id: str) -> Dict[str, object]:
        """根据任务 ID 构造批处理执行所需的 payload。

        Args:
            unique_id: 任务唯一 ID。

        Returns:
            dict: 包含 ``row_index`` 与 ``text`` 的字典。

        Raises:
            ValueError: 当无法定位对应数据行时抛出。
        """
        row_idx = self._extract_row_index(unique_id)
        if row_idx is None or row_idx >= len(self.df):
            raise ValueError(f"无法定位 unique_id={unique_id} 对应的数据行")

        row = self.df.iloc[row_idx]
        content = row.get("内容简介", "")
        if pd.isna(content):
            content = ""
        return {"row_index": row_idx, "text": str(content)}

    async def execute(self, context: BatchExecutionContext) -> TaskExecutionResult:
        """执行单条结构化提取任务并生成批处理结果。

        Args:
            context: 当前任务的批处理上下文。这里的context是一个字典（用dataclass定义的），
                     包含了任务的各种信息，比如唯一ID，批次索引，任务索引，payload等。

        Returns:
            TaskExecutionResult: 成功或失败的执行结果。
        """
        payload = context.payload or {}
        text = payload.get("text", "") or ""
        row_index = payload.get("row_index")

        batch_info = {
            "batch_num": context.batch_index,
            "task_index": context.task_index,
            "total_batches": context.total_batches,
        }

        if not text.strip():
            error_msg = "内容为空"
            log_record = {
                "call_id": "N/A",
                "unique_id": context.unique_id,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "batch_info": batch_info,
            }
            return TaskExecutionResult(
                unique_id=context.unique_id,
                status="failed",
                llm_call_id=None,
                error=error_msg,
                log_record=log_record,
                retry_increment=1,
                attachments={"row_index": row_index},
            )

        prompt = render_prompt_template(
            TEMPLATE_NAME,
            {
                "input_text": text,
                "schema_json": self.schema_json,
                "field_explanations": self.field_explanations,
            },
        )

        metadata = {
            "unique_id": context.unique_id,
            "batch_num": context.batch_index,
            "task_index": context.task_index,
            "source": "matched_procurement_csv_example",
        }

        try:
            result_model = await self.client.get_structured_completion(
                text_input=prompt,
                response_model=ProcurementInfo,
                model=self.model,
                temperature=self.temperature,
                enable_repair=True,
                metadata=metadata,
            )
        except Exception as err:
            log_record = {
                "call_id": "error",
                "unique_id": context.unique_id,
                "error": str(err),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "batch_info": batch_info,
            }
            return TaskExecutionResult(
                unique_id=context.unique_id,
                status="failed",
                llm_call_id=None,
                error=str(err),
                log_record=log_record,
                retry_increment=1,
                attachments={"row_index": row_index},
            )

        session_record = self._fetch_session_record(context.unique_id)
        call_id = session_record.get("call_id", "unknown") if session_record else "unknown"
        log_record = self._build_log_record(session_record, context.unique_id, batch_info)

        if result_model:
            return TaskExecutionResult(
                unique_id=context.unique_id,
                status="success",
                llm_call_id=call_id,
                error=None,
                log_record=log_record,
                retry_increment=0,
                attachments={"row_index": row_index},
            )

        return TaskExecutionResult(
            unique_id=context.unique_id,
            status="failed",
            llm_call_id=call_id,
            error="结构化提取失败",
            log_record=log_record,
            retry_increment=1,
            attachments={"row_index": row_index},
        )

    def _fetch_session_record(self, unique_id: str) -> Optional[Dict[str, object]]:
        """检索与任务 ID 匹配的最新会话记录。
            从 StructuredLLMClient 内部的 tracker.session_records（内存里的调用日志列表）里，找到 metadata 中 unique_id 与当前任务一致的那条 LLM 调用记录。遍历 tracker 里的记录，优先返回最近符合的那一条；如果没找到就退回到最后一条记录。
        Args:
            unique_id: 任务唯一标识。

        Returns:
            dict|None: 匹配的会话记录或 ``None``。
        """
        tracker = getattr(self.client, "tracker", None)
        records = getattr(tracker, "session_records", None)
        if not records:
            return None
        for record in reversed(records):
            metadata = record.get("metadata") or {}
            if metadata.get("unique_id") == unique_id:
                return record
        return records[-1]

    @staticmethod
    def _build_log_record(
        session_record: Optional[Dict[str, object]],
        unique_id: str,
        batch_info: Dict[str, int],
    ) -> Dict[str, object]:
        """整合会话记录与批次信息生成日志条目。

        Args:
            session_record: LLM 调用记录。
            unique_id: 任务唯一标识。
            batch_info: 批次元数据。

        Returns:
            dict: 可直接写入批次日志文件的数据项。
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        base_record = {
            "call_id": session_record.get("call_id", "unknown") if session_record else "unknown",
            "unique_id": unique_id,
            "timestamp": session_record.get("timestamp", timestamp) if session_record else timestamp,
            "batch_info": batch_info,
        }
        if session_record:
            base_record.update(
                {
                    "request": session_record.get("request", ""),
                    "response": session_record.get("response", ""),
                    "usage": session_record.get("usage", {}),
                    "cost": session_record.get("cost", {}),
                    "error": session_record.get("error"),
                }
            )
        return base_record


def build_arg_parser() -> argparse.ArgumentParser:
    """构建示例脚本的命令行参数解析器。

    Returns:
        argparse.ArgumentParser: 已配置的解析器实例。
    """
    parser = argparse.ArgumentParser(description="BatchTaskManager procurement extraction example")
    default_input = (
        CURRENT_DIR.parent
        / "匹配诉讼数据"
        / "extracted_matched_data"
        / "matched_procurement_data.csv"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=str(default_input),
        help="路径指向 matched_procurement_data.csv",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=2000,
        help="只处理前N条数据",
    )
    parser.add_argument(
        "--state-file",
        type=str,
        default=str(CURRENT_DIR / "examples" / "tasks" / "matched_procurement_example.jsonl"),
        help="状态文件路径",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(CURRENT_DIR / "examples" / "output"),
        help="结果输出目录",
    )
    parser.add_argument(
        "--logs-dir",
        type=str,
        default=str(CURRENT_DIR / "examples" / "logs"),
        help="批次日志目录",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="批处理大小",
    )
    parser.add_argument(
        "--api-name",
        type=str,
        default="yunwu_gemini",
        help="LLM API 名称",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="LLM 模型名称",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="LLM 请求温度",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="并发任务数量",
    )
    return parser


def ensure_directories(state_file: str, output_dir: str, logs_dir: str):
    """确保任务状态、输出结果与日志目录存在。"""
    Path(state_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(logs_dir).mkdir(parents=True, exist_ok=True)


def initialise_tasks(task_manager: BatchTaskManager, limit: int):
    """按数据规模初始化任务状态或复用既有状态。
        “既有状态”指的是 BatchTaskManager 已经加载过现成的任务状态文件（state_file）。如果之前跑过一次、状态文件里已经记录了每个 unique_id 的 status/retry_count/llm_call_id 等信息，TaskManager.is_initialized() 会返回 True。这时我们就不重新生成一遍任务列表，而是直接“复用”这份状态：

        保留哪些任务已成功、哪些失败、哪些仍 pending 的信息；
        继续处理剩余的 pending（或后来被重置的 failed）任务，实现断点续传。
    Args:
        task_manager: 批处理任务管理器。
        limit: 初始化的任务数量。
    """
    pending_ids = [{"unique_id": f"matched_row_{idx}"} for idx in range(limit)]
    if not task_manager.is_initialized():
        print(f"📝 初始化 {len(pending_ids)} 个任务")
        task_manager.initialize_tasks(pending_ids)
    else:
        print("✅ 任务已初始化，从现有状态恢复")
    task_manager.print_summary()


def export_success_results(task_manager: BatchTaskManager, df: pd.DataFrame, log_file: str, output_dir: str):
    """导出成功任务的解析结果并记录失败样本。

    Args:
        task_manager: 批处理任务管理器。
        df: 原始数据 DataFrame。
        log_file: LLM 活动日志路径。
        output_dir: 结果输出目录。
    """
    success_map = task_manager.get_success_map()
    if not success_map:
        print("⚠️ 无成功任务，跳过导出")
        return

    activity_log = LLMActivityLog(log_file)
    results = []
    failures = []
    success_count = 0

    for unique_id, call_id in success_map.items():
        idx = int(unique_id.replace("matched_row_", ""))
        if idx >= len(df):
            continue

        row = df.iloc[idx]
        record = activity_log.get_response_by_call_id(call_id)
        if not record:
            failures.append({"unique_id": unique_id, "call_id": call_id, "reason": "no_response_in_logs"})
            continue

        raw_resp = record.get("response", "")
        parsed, validated, error_msg = parse_response(raw_resp)

        if parsed is None:
            failures.append(
                {
                    "unique_id": unique_id,
                    "call_id": call_id,
                    "reason": "parsing_failed",
                    "error": error_msg,
                    "raw": (raw_resp[:200] + "...") if raw_resp else None,
                }
            )
            continue

        success_count += 1
        item = {
            "unique_id": unique_id,
            "row_index": idx,
            "llm_call_id": call_id,
            "内容简介": row.get("内容简介"),
            "采购方名称": parsed.get("purchaser"),
            "中标商名称": parsed.get("winner"),
            "采购物品名称": parsed.get("item_name"),
            "采购数量": parsed.get("quantity"),
            "中标金额": parsed.get("amount"),
            "是否设备采购": parsed.get("device"),
            "pydantic_validated": validated is not None,
            "parsing_method": resolve_parsing_method(validated, error_msg),
        }

        results.append(item)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_json = output_dir_path / f"matched_procurement_example_results_{timestamp}.json"
    output_csv = output_dir_path / f"matched_procurement_example_results_{timestamp}.csv"
    failures_file = output_dir_path / f"matched_procurement_example_failures_{timestamp}.jsonl"

    pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(failures_file, "w", encoding="utf-8") as f:
        for rec in failures:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"✅ 成功结果已导出:\n   JSON: {output_json}\n   CSV: {output_csv}")
    if failures:
        print(f"⚠️ 失败样本记录: {failures_file} (数量: {len(failures)})")
    print(f"🎯 解析成功 {success_count} 条 / 总计 {len(success_map)} 条")


def parse_response(raw_response: str) -> Tuple[Optional[Dict[str, object]], Optional[ProcurementInfo], Optional[str]]:
    """多阶段解析 LLM 返回的文本。

    Args:
        raw_response: 原始响应字符串。

    Returns:
        tuple: (解析出的 dict、Pydantic 校验结果、错误信息)。
    """
    try:
        validated = ProcurementInfo.model_validate_json(raw_response)
        return validated.model_dump(), validated, None
    except Exception as first_error:
        try:
            cleaned = sanitize_response_text(raw_response)
            intermediate = json5_loads(cleaned) if cleaned else {}
            validated = ProcurementInfo.model_validate(intermediate)
            return validated.model_dump(), validated, None
        except Exception as second_error:
            try:
                parsed = json5_loads(raw_response if raw_response else "{}")
                return parsed, None, (
                    f"pydantic_validation_failed_but_json5_ok; "
                    f"pydantic_error={first_error}; json5_intermediate_error={second_error}"
                )
            except Exception as third_error:
                return None, None, (
                    f"all_parsing_failed; pydantic_error={first_error}; "
                    f"json5_intermediate_error={second_error}; final_error={third_error}"
                )


def resolve_parsing_method(validated: Optional[ProcurementInfo], error_msg: Optional[str]) -> str:
    """根据校验结果判断最终使用的解析途径。"""
    if validated is not None:
        return "pydantic_direct" if error_msg is None else "pydantic_fallback"
    if error_msg:
        return "json5_only"
    return "unknown"


def sanitize_response_text(raw: str) -> str:
    """去除代码块包裹和噪声，提取可能的 JSON 文本。"""
    if raw is None:
        return ""
    s = str(raw).strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", s, re.S | re.I)
    if match:
        s = match.group(1).strip()
    else:
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.I)
        s = re.sub(r"\s*```$", "", s)
    if not (s.startswith("{") and s.endswith("}")):
        first = s.find("{")
        last = s.rfind("}")
        if first != -1 and last != -1 and last > first:
            s = s[first : last + 1]
    return s.strip()


def json5_loads(text: str):
    """优先调用 json5.loads，缺失时回退到 json.loads。"""
    if json5 is not None:
        return json5.loads(text)
    return json.loads(text)


async def main():
    """CLI 入口：解析参数、执行批处理并导出结果。"""
    parser = build_arg_parser()
    args = parser.parse_args()

    ensure_directories(args.state_file, args.output_dir, args.logs_dir)

    try:
        df = pd.read_csv(args.input, nrows=args.limit)
    except Exception as err:
        raise FileNotFoundError(f"无法加载数据文件 {args.input}: {err}")

    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir_path = Path(args.logs_dir)
    logs_dir_path.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir_path / f"matched_procurement_example_{session_timestamp}.jsonl"

    client = StructuredLLMClient(api_name=args.api_name, log_file=str(log_file))
    executor = ProcurementExtractionExecutor(
        df,
        client,
        args.model,
        temperature=args.temperature,
    )
    task_manager = BatchTaskManager(
        state_file=args.state_file,
        executor=executor,
        batch_size=args.batch_size,
        max_concurrent=args.max_concurrent,
        logs_dir=args.logs_dir,
    )

    initialise_tasks(task_manager, limit=len(df))

    await task_manager.process_pending_tasks(
        batch_metadata={
            "temperature": args.temperature,
            "api": args.api_name,
            "model": args.model,
        }
    )
    task_manager.print_summary()
    export_success_results(task_manager, df, str(log_file), args.output_dir)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
