#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务状态管理组件

TaskManager: 核心状态读写与统计。
BatchTaskManager: 在 TaskManager 基础上扩展批处理、并发执行与批次化持久化能力。
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence


class TaskManager:
    """
    批量任务状态管理器
    
    核心功能：
    - 初始化任务列表（从输入数据生成状态文件）
    - 追踪任务状态（pending / success / failed）
    - 支持断点续传（程序崩溃后恢复）
    - 多轮重试支持
    - 统计和报告生成
    
    状态文件结构（JSONL格式）：
    {
        "unique_id": "原始数据的唯一标识",
        "status": "pending | success | failed",
        "llm_call_id": "关联的LLM调用ID（处理后才有）",
        "error": "错误信息（失败时才有）",
        "created_at": "任务创建时间",
        "updated_at": "最后更新时间",
        "retry_count": "重试次数"
    }
    """
    
    def __init__(self, state_file: str):
        """
        初始化任务管理器
        
        Args:
            state_file: 状态文件路径（.jsonl格式）
        """
        self.state_file = state_file
        self.tasks: Dict[str, Dict] = {}  # unique_id -> task_dict
        self._ensure_directory()
        
        # 如果文件已存在，加载现有状态
        if os.path.exists(self.state_file):
            self._load_state()
            print(f"✅ 已加载现有任务状态: {len(self.tasks)} 个任务")
        else:
            print(f"📝 任务状态文件将创建于: {self.state_file}")
    
    def _ensure_directory(self):
        """确保状态文件所在目录存在"""
        directory = os.path.dirname(self.state_file)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳（ISO 8601格式）"""
        return datetime.utcnow().isoformat() + 'Z'
    
    def _load_state(self):
        """从JSONL文件加载任务状态"""
        self.tasks = {}
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    task = json.loads(line)
                    unique_id = task.get('unique_id')
                    if unique_id:
                        self.tasks[unique_id] = task
        except Exception as e:
            print(f"⚠️ 加载状态文件失败: {e}")
            self.tasks = {}
    
    def _save_state(self):
        """保存任务状态到JSONL文件（覆盖写入）"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                for task in self.tasks.values():
                    f.write(json.dumps(task, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"❌ 保存状态文件失败: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """检查是否已初始化（状态文件是否存在且有任务）"""
        return len(self.tasks) > 0
    
    def initialize_tasks(self, items: List[Dict[str, Any]], force: bool = False) -> int:
        """
        初始化任务列表
        
        Args:
            items: 输入数据列表，每项必须包含 'unique_id' 字段
                   格式: [{"unique_id": "xxx", ...}, ...]
            force: 是否强制重新初始化（会覆盖现有状态）
            
        Returns:
            初始化的任务数量
            
        Raises:
            ValueError: 如果输入数据格式不正确
        """
        if self.is_initialized() and not force:
            print(f"⚠️ 任务已初始化（{len(self.tasks)} 个任务），使用 force=True 强制重新初始化")
            return len(self.tasks)
        
        # 验证输入数据
        if not items:
            raise ValueError("输入数据列表不能为空")
        
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"第 {i} 项不是字典类型")
            if 'unique_id' not in item:
                raise ValueError(f"第 {i} 项缺少 'unique_id' 字段")
        
        # 检查唯一性
        unique_ids = [item['unique_id'] for item in items]
        if len(unique_ids) != len(set(unique_ids)):
            raise ValueError("存在重复的 unique_id")
        
        # 初始化任务
        current_time = self._get_current_timestamp()
        self.tasks = {}
        
        for item in items:
            unique_id = item['unique_id']
            self.tasks[unique_id] = {
                'unique_id': unique_id,
                'status': 'pending',
                'llm_call_id': None,
                'error': None,
                'created_at': current_time,
                'updated_at': current_time,
                'retry_count': 0
            }
        
        # 保存到文件
        self._save_state()
        
        print(f"✅ 已初始化 {len(self.tasks)} 个任务")
        return len(self.tasks)
    
    def get_pending_tasks(self, limit: Optional[int] = None) -> List[str]:
        """
        获取待处理任务的 unique_id 列表
        
        Args:
            limit: 最多返回多少个任务，None表示返回全部
            
        Returns:
            待处理任务的 unique_id 列表
        """
        pending_ids = [
            uid for uid, task in self.tasks.items() 
            if task['status'] == 'pending'
        ]
        
        if limit is not None and limit > 0:
            pending_ids = pending_ids[:limit]
        
        return pending_ids
    
    def get_failed_tasks(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取失败任务的详细信息
        
        Args:
            limit: 最多返回多少个任务
            
        Returns:
            失败任务列表，包含 unique_id 和 error
        """
        failed = [
            {
                'unique_id': task['unique_id'],
                'error': task['error'],
                'llm_call_id': task['llm_call_id'],
                'retry_count': task['retry_count'],
                'updated_at': task['updated_at']
            }
            for task in self.tasks.values() 
            if task['status'] == 'failed'
        ]
        
        if limit is not None and limit > 0:
            failed = failed[:limit]
        
        return failed
    
    def update_task_success(self, unique_id: str, llm_call_id: str):
        """
        标记任务为成功状态
        
        Args:
            unique_id: 任务的唯一标识
            llm_call_id: LLM调用ID（用于关联到llm_activity.jsonl）
        """
        if unique_id not in self.tasks:
            print(f"⚠️ 任务不存在: {unique_id}")
            return
        
        task = self.tasks[unique_id]
        
        # 如果之前是pending，retry_count保持为0
        # 如果之前是failed，retry_count已经+1了
        if task['status'] == 'pending' and task['retry_count'] == 0:
            # 首次尝试成功
            pass
        else:
            # 重试成功（retry_count已在处理时递增）
            pass
        
        task['status'] = 'success'
        task['llm_call_id'] = llm_call_id
        task['error'] = None
        task['updated_at'] = self._get_current_timestamp()
        
        # 保存到文件
        self._save_state()
    
    def update_task_failure(self, unique_id: str, llm_call_id: str, error: str):
        """
        标记任务为失败状态
        
        Args:
            unique_id: 任务的唯一标识
            llm_call_id: LLM调用ID
            error: 错误信息
        """
        if unique_id not in self.tasks:
            print(f"⚠️ 任务不存在: {unique_id}")
            return
        
        task = self.tasks[unique_id]
        
        # 递增重试计数
        if task['status'] == 'pending' and task['retry_count'] == 0:
            # 首次尝试
            task['retry_count'] = 1
        else:
            # 重试
            task['retry_count'] += 1
        
        task['status'] = 'failed'
        task['llm_call_id'] = llm_call_id
        task['error'] = error
        task['updated_at'] = self._get_current_timestamp()
        
        # 保存到文件
        self._save_state()
    
    def reset_failed_tasks(self) -> int:
        """
        将所有失败任务重置为待处理状态（用于重试）
        
        Returns:
            重置的任务数量
        """
        count = 0
        for task in self.tasks.values():
            if task['status'] == 'failed':
                task['status'] = 'pending'
                task['error'] = None
                task['updated_at'] = self._get_current_timestamp()
                count += 1
        
        if count > 0:
            self._save_state()
            print(f"✅ 已将 {count} 个失败任务重置为待处理")
        
        return count
    
    def reset_specific_tasks(self, unique_ids: List[str]) -> int:
        """
        将指定的任务重置为待处理状态
        
        Args:
            unique_ids: 要重置的任务ID列表
            
        Returns:
            重置的任务数量
        """
        count = 0
        for uid in unique_ids:
            if uid in self.tasks:
                task = self.tasks[uid]
                if task['status'] in ['failed', 'success']:
                    task['status'] = 'pending'
                    task['error'] = None
                    task['updated_at'] = self._get_current_timestamp()
                    count += 1
        
        if count > 0:
            self._save_state()
            print(f"✅ 已重置 {count} 个任务为待处理")
        
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Returns:
            统计信息字典，包含：
            - total: 总任务数
            - pending: 待处理任务数
            - success: 成功任务数
            - failed: 失败任务数
            - success_rate: 成功率（0-1）
            - completion_rate: 完成率（已处理/总数）
        """
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks.values() if t['status'] == 'pending')
        success = sum(1 for t in self.tasks.values() if t['status'] == 'success')
        failed = sum(1 for t in self.tasks.values() if t['status'] == 'failed')
        
        processed = success + failed
        success_rate = success / processed if processed > 0 else 0
        completion_rate = processed / total if total > 0 else 0
        
        return {
            'total': total,
            'pending': pending,
            'success': success,
            'failed': failed,
            'processed': processed,
            'success_rate': success_rate,
            'completion_rate': completion_rate
        }
    
    def get_success_map(self) -> Dict[str, str]:
        """
        获取成功任务的映射关系
        
        Returns:
            {unique_id: llm_call_id} 的映射字典，只包含成功的任务
            用于后续从 llm_activity.jsonl 中提取响应并合并到原始数据
        """
        return {
            uid: task['llm_call_id']
            for uid, task in self.tasks.items()
            if task['status'] == 'success' and task['llm_call_id']
        }

    def export_results(
        self,
        output_file: str,
        status_filter: Optional[str] = None,
        format: str = 'json'
    ):
        """
        导出任务结果
        
        Args:
            output_file: 输出文件路径
            status_filter: 状态过滤器（'pending' / 'success' / 'failed' / None）
            format: 输出格式（'json' / 'jsonl'）
        """
        # 筛选任务
        if status_filter:
            tasks = [t for t in self.tasks.values() if t['status'] == status_filter]
        else:
            tasks = list(self.tasks.values())
        
        # 确保目录存在
        directory = os.path.dirname(output_file)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # 导出
        if format == 'jsonl':
            with open(output_file, 'w', encoding='utf-8') as f:
                for task in tasks:
                    f.write(json.dumps(task, ensure_ascii=False) + '\n')
        else:  # json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已导出 {len(tasks)} 个任务到: {output_file}")
    
    def print_summary(self):
        """打印任务统计摘要"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("任务统计摘要")
        print("=" * 60)
        print(f"总任务数:     {stats['total']}")
        print(f"待处理:       {stats['pending']}")
        print(f"成功:         {stats['success']}")
        print(f"失败:         {stats['failed']}")
        print(f"完成率:       {stats['completion_rate']*100:.1f}%")
        print(f"成功率:       {stats['success_rate']*100:.1f}%")
        print("=" * 60 + "\n")


# 辅助函数：从 llm_activity.jsonl 中提取响应
class LLMActivityLog:
    """LLM活动日志读取器（辅助工具）"""
    
    def __init__(self, log_file: str):
        """
        初始化日志读取器
        
        Args:
            log_file: llm_activity.jsonl 文件路径
        """
        self.log_file = log_file
        self._index = None  # 延迟加载索引
    
    def _build_index(self):
        """构建 call_id -> record 的索引"""
        if self._index is not None:
            return
        
        self._index = {}
        if not os.path.exists(self.log_file):
            print(f"⚠️ 日志文件不存在: {self.log_file}")
            return
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    call_id = record.get('call_id')
                    if call_id:
                        self._index[call_id] = record
                except json.JSONDecodeError:
                    continue
    
    def get_response_by_call_id(self, call_id: str) -> Optional[Dict]:
        """
        根据 call_id 获取完整的调用记录
        
        Args:
            call_id: LLM调用ID
            
        Returns:
            调用记录字典，包含 response、usage、cost 等信息
        """
        self._build_index()
        return self._index.get(call_id)
    
    def get_responses_by_unique_id(self, unique_id: str) -> List[Dict]:
        """
        根据 unique_id 获取所有相关的调用记录（用于查看重试历史）
        
        Args:
            unique_id: 原始数据的唯一标识
            
        Returns:
            调用记录列表，按时间排序
        """
        self._build_index()
        
        records = [
            r for r in self._index.values()
            if r.get('metadata', {}).get('unique_id') == unique_id
        ]
        
        # 按时间排序
        records.sort(key=lambda x: x.get('timestamp_start', ''))
        return records


# 测试代码
if __name__ == "__main__":
    print("=== TaskManager 测试 ===\n")
    
    # 模拟输入数据
    test_data = [
        {"unique_id": f"doc_{i:03d}"} 
        for i in range(1, 11)
    ]
    
    # 创建任务管理器
    task_mgr = TaskManager(state_file="test_tasks/batch_test.jsonl")
    
    # 初始化任务
    task_mgr.initialize_tasks(test_data, force=True)
    
    # 模拟处理：成功5个，失败3个
    for i in range(1, 6):
        task_mgr.update_task_success(f"doc_{i:03d}", f"call_{i:03d}")
    
    for i in range(6, 9):
        task_mgr.update_task_failure(f"doc_{i:03d}", f"call_{i:03d}", "模拟错误")
    
    # 查看统计
    task_mgr.print_summary()
    
    # 查看失败任务
    print("失败的任务:")
    for task in task_mgr.get_failed_tasks():
        print(f"  - {task['unique_id']}: {task['error']}")
    
    # 重置失败任务
    print(f"\n重置失败任务...")
    task_mgr.reset_failed_tasks()
    
    # 再次查看统计
    task_mgr.print_summary()
    
    # 导出成功任务
    success_map = task_mgr.get_success_map()
    print(f"成功任务映射: {success_map}")


# =====================
# 批处理扩展能力
# =====================


@dataclass
class BatchExecutionContext:
    """批次内单任务执行上下文"""

    unique_id: str
    batch_index: int
    task_index: int
    total_batches: int
    payload: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecutionResult:
    """单个任务执行结果"""

    unique_id: str
    status: str  # 'success' | 'failed'
    llm_call_id: Optional[str] = None
    error: Optional[str] = None
    log_record: Optional[Dict[str, Any]] = None
    retry_increment: int = 1
    attachments: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == 'success'


class BatchTaskExecutor(Protocol):
    """
    批处理任务执行器接口

    由业务方实现，封装单条任务的执行逻辑与日志构建方式。
    """

    def get_payload(self, unique_id: str) -> Any:
        """根据 unique_id 返回执行所需的原始数据或上下文"""

    async def execute(
        self,
        context: BatchExecutionContext
    ) -> TaskExecutionResult:
        """
        执行单个任务

        Args:
            context: 当前任务上下文，包含 payload、批次和索引信息
        """


class BatchTaskManager(TaskManager):
    """
    在 TaskManager基础上封装批量执行、批次日志/状态写入、备份恢复等能力。
    """

    def __init__(
        self,
        *,
        state_file: str,
        executor: BatchTaskExecutor,
        batch_size: int = 1000,
        max_concurrent: int = 10,
        logs_dir: Optional[str] = None,
        retain_batches: bool = True
    ):
        super().__init__(state_file=state_file)
        self.executor = executor
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.retain_batches = retain_batches

        base_dir = Path(state_file).resolve().parent
        self.tasks_dir = base_dir
        self.logs_dir = Path(logs_dir) if logs_dir else base_dir / "logs"
        self.batch_logs_dir = self.logs_dir / "batches"
        self.backup_dir = base_dir / "backups"

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.batch_logs_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.batch_counter = 0
        self.current_batch_logs: List[Dict[str, Any]] = []
        self.current_batch_updates: List[TaskExecutionResult] = []

    # -----------------
    # 批处理入口
    # -----------------

    async def process_pending_tasks(
        self,
        *,
        limit: Optional[int] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        对 pending 状态的任务执行批量处理。

        Args:
            limit: 限制处理任务数（调试使用）
            batch_metadata: 附加到 BatchExecutionContext 的公共元数据
        """
        pending_ids = self.get_pending_tasks(limit=limit)
        total_tasks = len(pending_ids)

        if total_tasks == 0:
            print("✅ 没有待处理任务")
            return

        batches = [
            pending_ids[i:i + self.batch_size]
            for i in range(0, total_tasks, self.batch_size)
        ]
        total_batches = len(batches)

        print(f"🧮 待处理任务: {total_tasks:,}，批次数: {total_batches}")

        for batch_index, batch_ids in enumerate(batches, start=1):
            await self._process_single_batch(
                batch_ids=batch_ids,
                batch_index=batch_index,
                total_batches=total_batches,
                batch_metadata=batch_metadata or {}
            )

            # 默认强制刷新，避免长任务中断丢失状态
            self.flush(force=True)

        # 最终确保缓存刷写
        self.flush(force=True)

    async def _process_single_batch(
        self,
        *,
        batch_ids: Sequence[str],
        batch_index: int,
        total_batches: int,
        batch_metadata: Dict[str, Any]
    ):
        """内部：并发处理单个批次"""
        print(f"\n🔄 处理批次 {batch_index}/{total_batches}，共 {len(batch_ids)} 条")

        semaphore = asyncio.Semaphore(self.max_concurrent)
        completed = 0

        async def _run_task(idx: int, unique_id: str):
            nonlocal completed
            async with semaphore:
                payload = None
                try:
                    payload = self.executor.get_payload(unique_id)
                except Exception as err:
                    result = TaskExecutionResult(
                        unique_id=unique_id,
                        status='failed',
                        llm_call_id=None,
                        error=f"payload_error: {err}",
                        retry_increment=1,
                        log_record={
                            "unique_id": unique_id,
                            "error": f"payload_error: {err}",
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "batch_info": {
                                "batch_num": batch_index,
                                "task_index": idx
                            }
                        }
                    )
                    self._buffer_result(result)
                    completed += 1
                    return

                context = BatchExecutionContext(
                    unique_id=unique_id,
                    batch_index=batch_index,
                    task_index=idx,
                    total_batches=total_batches,
                    payload=payload,
                    metadata=batch_metadata
                )

                try:
                    result = await self.executor.execute(context)
                except Exception as err:
                    result = TaskExecutionResult(
                        unique_id=unique_id,
                        status='failed',
                        llm_call_id=None,
                        error=str(err),
                        retry_increment=1,
                        log_record={
                            "unique_id": unique_id,
                            "error": str(err),
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "batch_info": {
                                "batch_num": batch_index,
                                "task_index": idx
                            }
                        }
                    )

                self._buffer_result(result)
                completed += 1

        await asyncio.gather(
            *(_run_task(idx, uid) for idx, uid in enumerate(batch_ids))
        )

        progress = completed / len(batch_ids) * 100 if batch_ids else 0
        print(f"✅ 批次 {batch_index}/{total_batches} 完成 ({progress:.1f}% of batch)")

    # -----------------
    # 缓存 & Flush
    # -----------------

    def _buffer_result(self, result: TaskExecutionResult):
        """将执行结果追加到当前批次缓存"""
        self.current_batch_updates.append(result)

        if result.log_record:
            self.current_batch_logs.append(result.log_record)

    def should_flush(self) -> bool:
        """是否达到刷新阈值"""
        return len(self.current_batch_updates) >= self.batch_size

    def flush(self, *, force: bool = False):
        """将当前批次缓存刷写到磁盘"""
        if not self.current_batch_updates and not self.current_batch_logs:
            return

        if not force and not self.should_flush():
            return

        backup_file = self.create_state_backup()
        try:
            self._write_log_batch()
            self._apply_state_updates(self.current_batch_updates)
            self._write_state_batch_file(self.current_batch_updates)

            logs_count = len(self.current_batch_logs)
            updates_count = len(self.current_batch_updates)

            self.current_batch_logs.clear()
            self.current_batch_updates.clear()

            self.batch_counter += 1
            print(f"💾 批次 {self.batch_counter:03d} 已刷新: {updates_count} 状态, {logs_count} 日志")
        except Exception as err:
            print(f"❌ 批次刷新失败: {err}")
            if backup_file and os.path.exists(backup_file):
                print("🔄 尝试从备份回滚状态文件...")
                self.restore_from_backup(backup_file)
            raise
        finally:
            if backup_file and not self.retain_batches:
                try:
                    os.remove(backup_file)
                except OSError:
                    pass

    def _apply_state_updates(self, updates: Sequence[TaskExecutionResult]):
        """批量写入状态（内存更新 + 单次保存）"""
        if not updates:
            return

        for result in updates:
            if result.unique_id not in self.tasks:
                continue

            if result.is_success:
                self._apply_success_update(result)
            else:
                self._apply_failure_update(result)

        self._save_state()

    def _apply_success_update(self, result: TaskExecutionResult):
        task = self.tasks[result.unique_id]
        task['status'] = 'success'
        task['llm_call_id'] = result.llm_call_id
        task['error'] = None
        task['updated_at'] = self._get_current_timestamp()

    def _apply_failure_update(self, result: TaskExecutionResult):
        task = self.tasks[result.unique_id]
        increment = result.retry_increment if result.retry_increment is not None else 1

        if task['status'] == 'pending' and task['retry_count'] == 0:
            task['retry_count'] = max(1, increment)
        else:
            task['retry_count'] += max(1, increment)

        task['status'] = 'failed'
        task['llm_call_id'] = result.llm_call_id
        task['error'] = result.error
        task['updated_at'] = self._get_current_timestamp()

    def _write_log_batch(self):
        if not self.current_batch_logs:
            return

        batch_file = self.batch_logs_dir / f"logs_batch_{self.session_timestamp}_{self.batch_counter:03d}.jsonl"
        with open(batch_file, 'w', encoding='utf-8') as f:
            for record in self.current_batch_logs:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

    def _write_state_batch_file(self, updates: Sequence[TaskExecutionResult]):
        if not updates:
            return

        batch_state_file = self.tasks_dir / f"state_batch_{self.session_timestamp}_{self.batch_counter:03d}.jsonl"
        with open(batch_state_file, 'w', encoding='utf-8') as f:
            for result in updates:
                entry = {
                    "unique_id": result.unique_id,
                    "status": result.status,
                    "llm_call_id": result.llm_call_id,
                    "error": result.error,
                    "timestamp": self._get_current_timestamp(),
                    "batch_number": self.batch_counter
                }
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def force_flush_remaining(self):
        """强制刷新剩余缓存"""
        self.flush(force=True)

    # -----------------
    # 备份与恢复
    # -----------------

    def create_state_backup(self) -> Optional[str]:
        """备份当前状态文件（若存在）"""
        if not os.path.exists(self.state_file):
            return None

        backup_path = self.backup_dir / f"state_backup_{self.session_timestamp}_{self.batch_counter:03d}.jsonl"
        try:
            import shutil
            shutil.copy2(self.state_file, backup_path)
            return str(backup_path)
        except Exception as err:
            print(f"⚠️ 状态备份失败: {err}")
            return None

    def restore_from_backup(self, backup_file: Optional[str] = None) -> bool:
        """从备份恢复状态文件"""
        try:
            if backup_file is None:
                backup_file = self._find_latest_backup()

            if not backup_file or not os.path.exists(backup_file):
                print("⚠️ 未找到可用备份")
                return False

            import shutil
            if os.path.exists(self.state_file):
                damaged_path = f"{self.state_file}.damaged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(self.state_file, damaged_path)
                print(f"📁 原状态文件已备份为: {damaged_path}")

            shutil.copy2(backup_file, self.state_file)
            self._load_state()
            print(f"✅ 已从备份恢复状态: {backup_file}")
            return True
        except Exception as err:
            print(f"❌ 备份恢复失败: {err}")
            return False

    def _find_latest_backup(self) -> Optional[str]:
        backups = list(self.backup_dir.glob("state_backup_*.jsonl"))
        if not backups:
            return None
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return str(backups[0])

    def find_latest_backup(self) -> Optional[str]:
        """公开接口：获取最新备份路径"""
        return self._find_latest_backup()

    # -----------------
    # 批次文件运维工具
    # -----------------

    def merge_batch_logs(self, output_file: Optional[str] = None) -> Optional[str]:
        if output_file is None:
            output_file = self.logs_dir / f"merged_logs_{self.session_timestamp}.jsonl"

        batch_files = sorted(self.batch_logs_dir.glob("logs_batch_*.jsonl"))
        if not batch_files:
            print("⚠️ 没有找到批次日志文件")
            return None

        total_records = 0
        try:
            with open(output_file, 'w', encoding='utf-8') as merged:
                for batch_file in batch_files:
                    with open(batch_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                merged.write(line)
                                total_records += 1

            print(f"✅ 合并日志完成，共 {total_records} 条，输出 {output_file}")
            return str(output_file)
        except Exception as err:
            print(f"❌ 合并日志失败: {err}")
            return None

    def merge_state_batches(self, output_file: Optional[str] = None) -> Optional[str]:
        if output_file is None:
            output_file = self.tasks_dir / f"merged_states_{self.session_timestamp}.jsonl"

        batch_files = sorted(self.tasks_dir.glob(f"state_batch_{self.session_timestamp}_*.jsonl"))
        if not batch_files:
            print("⚠️ 没有找到批次状态文件")
            return None

        total_records = 0
        try:
            with open(output_file, 'w', encoding='utf-8') as merged:
                for batch_file in batch_files:
                    with open(batch_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                merged.write(line)
                                total_records += 1

            print(f"✅ 合并状态批次完成，共 {total_records} 条，输出 {output_file}")
            return str(output_file)
        except Exception as err:
            print(f"❌ 合并状态文件失败: {err}")
            return None

    def cleanup_batch_files(self):
        """清理本次会话产生的批次文件"""
        target_logs = list(self.batch_logs_dir.glob(f"logs_batch_{self.session_timestamp}_*.jsonl"))
        target_states = list(self.tasks_dir.glob(f"state_batch_{self.session_timestamp}_*.jsonl"))

        for file_path in target_logs + target_states:
            try:
                os.remove(file_path)
            except OSError:
                pass
