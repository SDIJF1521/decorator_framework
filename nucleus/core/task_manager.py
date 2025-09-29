"""
任务管理器 - 支持任务取消、状态跟踪和生命周期管理
"""
import asyncio
import uuid
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
import weakref


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"      # 执行超时


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    name: str
    status: TaskStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_task_id: Optional[str] = None
    child_task_ids: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[float]:
        """任务执行耗时"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def wait_time(self) -> Optional[float]:
        """任务等待时间"""
        if self.created_at and self.started_at:
            return self.started_at - self.created_at
        return None


class TaskCancellationToken:
    """任务取消令牌"""
    
    def __init__(self):
        self._cancelled = False
        self._callbacks: List[Callable] = []
        self._lock = Lock()
    
    def cancel(self) -> None:
        """请求取消"""
        with self._lock:
            if not self._cancelled:
                self._cancelled = True
                # 执行回调
                for callback in self._callbacks:
                    try:
                        callback()
                    except Exception as e:
                        print(f"取消回调执行失败: {e}")
    
    @property
    def is_cancelled(self) -> bool:
        """是否已请求取消"""
        with self._lock:
            return self._cancelled
    
    def register_callback(self, callback: Callable) -> None:
        """注册取消回调"""
        with self._lock:
            if self._cancelled:
                # 如果已经取消，立即执行回调
                try:
                    callback()
                except Exception as e:
                    print(f"取消回调执行失败: {e}")
            else:
                self._callbacks.append(callback)
    
    def throw_if_cancelled(self) -> None:
        """如果已取消则抛出异常"""
        if self.is_cancelled:
            raise asyncio.CancelledError("任务已被取消")


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._cancellation_tokens: Dict[str, TaskCancellationToken] = {}
        self._task_callbacks: Dict[str, List[Callable]] = {}
        self._lock = Lock()
        self._task_counter = 0
        
        # 使用弱引用跟踪异步任务，避免内存泄漏
        self._weak_task_refs: Dict[str, weakref.ref] = {}
    
    def create_task(
        self,
        coro: Callable,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_task_id: Optional[str] = None
    ) -> str:
        """创建任务"""
        task_id = str(uuid.uuid4())
        
        # 创建任务信息
        task_info = TaskInfo(
            task_id=task_id,
            name=name or coro.__name__,
            status=TaskStatus.PENDING,
            created_at=time.time(),
            metadata=metadata or {},
            parent_task_id=parent_task_id
        )
        
        # 创建取消令牌
        cancellation_token = TaskCancellationToken()
        
        with self._lock:
            self._tasks[task_id] = task_info
            self._cancellation_tokens[task_id] = cancellation_token
            
            # 如果是子任务，更新父任务的子任务列表
            if parent_task_id and parent_task_id in self._tasks:
                self._tasks[parent_task_id].child_task_ids.append(task_id)
        
        # 创建异步任务
        async def task_wrapper():
            try:
                # 检查是否已取消
                cancellation_token.throw_if_cancelled()
                
                # 更新任务状态
                with self._lock:
                    task_info.status = TaskStatus.RUNNING
                    task_info.started_at = time.time()
                
                # 执行协程
                result = await coro
                
                # 更新任务状态
                with self._lock:
                    task_info.status = TaskStatus.COMPLETED
                    task_info.completed_at = time.time()
                    task_info.result = result
                
                return result
                
            except asyncio.CancelledError:
                # 任务被取消
                with self._lock:
                    task_info.status = TaskStatus.CANCELLED
                    task_info.completed_at = time.time()
                raise
                
            except Exception as e:
                # 任务执行失败
                with self._lock:
                    task_info.status = TaskStatus.FAILED
                    task_info.completed_at = time.time()
                    task_info.error = e
                raise
                
            finally:
                # 清理
                self._cleanup_task(task_id)
        
        # 创建并启动异步任务
        task = asyncio.create_task(task_wrapper())
        
        with self._lock:
            self._active_tasks[task_id] = task
            self._weak_task_refs[task_id] = weakref.ref(task)
        
        return task_id
    
    def _cleanup_task(self, task_id: str) -> None:
        """清理任务资源"""
        with self._lock:
            # 执行回调
            callbacks = self._task_callbacks.get(task_id, [])
            for callback in callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"任务回调执行失败: {e}")
            
            # 清理资源
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]
            if task_id in self._cancellation_tokens:
                del self._cancellation_tokens[task_id]
            if task_id in self._task_callbacks:
                del self._task_callbacks[task_id]
            if task_id in self._weak_task_refs:
                del self._weak_task_refs[task_id]
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            task_info = self._tasks[task_id]
            if task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return False
            
            # 取消任务
            cancellation_token = self._cancellation_tokens.get(task_id)
            if cancellation_token:
                cancellation_token.cancel()
            
            # 立即更新任务状态为已取消
            task_info.status = TaskStatus.CANCELLED
            task_info.completed_at = time.time()
            
            # 取消异步任务（不等待其完成）
            task = self._active_tasks.get(task_id)
            if task and not task.done():
                task.cancel()
            
            # 递归取消子任务
            for child_task_id in task_info.child_task_ids:
                await self.cancel_task(child_task_id)
            
            return True
    
    def cancel_task_sync(self, task_id: str) -> bool:
        """同步取消任务"""
        if task_id not in self._tasks:
            return False
        
        task_info = self._tasks[task_id]
        if task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
        
        # 请求取消
        cancellation_token = self._cancellation_tokens.get(task_id)
        if cancellation_token:
            cancellation_token.cancel()
        
        # 取消异步任务
        task = self._active_tasks.get(task_id)
        if task and not task.done():
            task.cancel()
        
        return True
    
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[TaskInfo]:
        """获取所有任务"""
        with self._lock:
            return list(self._tasks.values())
    
    def get_active_tasks(self) -> List[TaskInfo]:
        """获取活跃任务"""
        with self._lock:
            return [
                task_info for task_info in self._tasks.values()
                if task_info.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
            ]
    
    def get_completed_tasks(self) -> List[TaskInfo]:
        """获取已完成任务"""
        with self._lock:
            return [
                task_info for task_info in self._tasks.values()
                if task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT]
            ]
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        task_info = self.get_task_info(task_id)
        return task_info.status if task_info else None
    
    def get_task_result(self, task_id: str) -> Any:
        """获取任务结果"""
        task_info = self.get_task_info(task_id)
        return task_info.result if task_info else None
    
    def get_task_error(self, task_id: str) -> Optional[Exception]:
        """获取任务错误"""
        task_info = self.get_task_info(task_id)
        return task_info.error if task_info else None
    
    def register_task_callback(self, task_id: str, callback: Callable) -> None:
        """注册任务回调"""
        with self._lock:
            if task_id not in self._task_callbacks:
                self._task_callbacks[task_id] = []
            self._task_callbacks[task_id].append(callback)
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """等待任务完成"""
        task = self._active_tasks.get(task_id)
        if task:
            try:
                # 创建新的事件循环来运行异步任务
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(asyncio.wait_for(task, timeout))
                    return result
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            except asyncio.TimeoutError:
                # 超时处理
                task_info = self._tasks.get(task_id)
                if task_info:
                    task_info.status = TaskStatus.TIMEOUT
                    task_info.completed_at = time.time()
                raise
        return None
    
    async def wait_for_task_async(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """异步等待任务完成"""
        task = self._active_tasks.get(task_id)
        if task:
            try:
                return await asyncio.wait_for(task, timeout)
            except asyncio.TimeoutError:
                # 超时处理
                task_info = self._tasks.get(task_id)
                if task_info:
                    task_info.status = TaskStatus.TIMEOUT
                    task_info.completed_at = time.time()
                raise
        return None
    
    def cancel_all_tasks(self) -> int:
        """取消所有活跃任务"""
        active_tasks = self.get_active_tasks()
        cancelled_count = 0
        
        for task_info in active_tasks:
            if self.cancel_task_sync(task_info.task_id):
                cancelled_count += 1
        
        return cancelled_count
    
    def cleanup_completed_tasks(self, max_age_seconds: float = 3600) -> int:
        """清理完成任务"""
        current_time = time.time()
        cleaned_count = 0
        
        with self._lock:
            completed_tasks = [
                task_id for task_id, task_info in self._tasks.items()
                if (task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT] and
                    task_info.completed_at and
                    current_time - task_info.completed_at > max_age_seconds)
            ]
            
            for task_id in completed_tasks:
                del self._tasks[task_id]
                cleaned_count += 1
        
        return cleaned_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取任务统计"""
        with self._lock:
            total_tasks = len(self._tasks)
            active_tasks = len([t for t in self._tasks.values() if t.status in [TaskStatus.PENDING, TaskStatus.RUNNING]])
            completed_tasks = len([t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED])
            failed_tasks = len([t for t in self._tasks.values() if t.status == TaskStatus.FAILED])
            cancelled_tasks = len([t for t in self._tasks.values() if t.status == TaskStatus.CANCELLED])
            
            return {
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'cancelled_tasks': cancelled_tasks,
                'pending_tasks': len([t for t in self._tasks.values() if t.status == TaskStatus.PENDING]),
                'running_tasks': len([t for t in self._tasks.values() if t.status == TaskStatus.RUNNING])
            }


# 任务管理器实例
default_task_manager = TaskManager()


def task(
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    parent_task_id: Optional[str] = None
) -> Callable:
    """任务装饰器"""
    
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            task_id = default_task_manager.create_task(
                func(*args, **kwargs),
                name=name or func.__name__,
                metadata=metadata,
                parent_task_id=parent_task_id
            )
            
            return await default_task_manager.wait_for_task_async(task_id)
        
  
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator