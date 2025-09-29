"""
调用链功能实现 - 支持任务执行的拦截和增强
"""
import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
from dataclasses import dataclass, field
from enum import Enum


class ChainStatus(Enum):
    """调用链状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ChainContext:
    """调用链上下文"""
    chain_id: str
    task_id: str
    function_name: str
    args: tuple
    kwargs: dict
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None
    status: ChainStatus = ChainStatus.PENDING
    
    @property
    def duration(self) -> Optional[float]:
        """执行耗时"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class ChainInterceptor(ABC):
    """调用链拦截器基类"""
    
    @abstractmethod
    async def before_execute(self, context: ChainContext) -> None:
        """执行前拦截"""
        pass
    
    @abstractmethod
    async def after_execute(self, context: ChainContext) -> None:
        """执行后拦截"""
        pass
    
    async def on_error(self, context: ChainContext, error: Exception) -> None:
        """错误处理"""
        pass


class CallChain:
    """调用链管理器"""
    
    def __init__(self):
        self._interceptors: List[ChainInterceptor] = []
        self._active_chains: Dict[str, ChainContext] = {}
        self._chain_results: Dict[str, Any] = {}
    
    def generate_chain_id(self) -> str:
        """生成调用链ID"""
        return str(uuid.uuid4())
    
    def add_interceptor(self, interceptor: ChainInterceptor) -> None:
        """添加拦截器"""
        self._interceptors.append(interceptor)
    
    def remove_interceptor(self, interceptor: ChainInterceptor) -> None:
        """移除拦截器"""
        if interceptor in self._interceptors:
            self._interceptors.remove(interceptor)
    
    async def execute(
        self,
        func: Callable,
        *args,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """执行函数并应用调用链拦截"""
        chain_id = str(uuid.uuid4())
        task_id = task_id or chain_id
        
        context = ChainContext(
            chain_id=chain_id,
            task_id=task_id,
            function_name=func.__name__,
            args=args,
            kwargs=kwargs,
            metadata=metadata or {}
        )
        
        self._active_chains[chain_id] = context
        
        try:
            # 执行前拦截
            context.status = ChainStatus.RUNNING
            context.start_time = time.time()
            
            for interceptor in self._interceptors:
                await interceptor.before_execute(context)
            
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            context.result = result
            context.status = ChainStatus.SUCCESS
            
        except Exception as e:
            context.error = e
            context.status = ChainStatus.FAILED
            
            # 错误处理
            for interceptor in self._interceptors:
                await interceptor.on_error(context, e)
            
            raise
        
        finally:
            context.end_time = time.time()
            
            # 只有在成功执行后才调用 after_execute
            if context.status == ChainStatus.SUCCESS:
                for interceptor in self._interceptors:
                    await interceptor.after_execute(context)
            
            # 保存结果并清理
            self._chain_results[chain_id] = context.result
            if chain_id in self._active_chains:
                del self._active_chains[chain_id]
        
        return context.result
    
    async def execute_with_context(self, context: ChainContext) -> Any:
        """使用现有上下文执行函数"""
        self._active_chains[context.chain_id] = context
        
        try:
            # 执行前拦截
            context.status = ChainStatus.RUNNING
            context.start_time = time.time()
            
            for interceptor in self._interceptors:
                await interceptor.before_execute(context)
            
            # 执行函数
            func = context.metadata.get('target')
            if func:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*context.args, **context.kwargs)
                else:
                    result = func(*context.args, **context.kwargs)
                
                context.result = result
                context.status = ChainStatus.SUCCESS
            else:
                raise ValueError("No target function provided in context metadata")
            
        except Exception as e:
            context.error = e
            context.status = ChainStatus.FAILED
            
            # 错误处理
            for interceptor in self._interceptors:
                await interceptor.on_error(context, e)
            
            raise
        
        finally:
            context.end_time = time.time()
            
            # 只有在成功执行后才调用 after_execute
            if context.status == ChainStatus.SUCCESS:
                for interceptor in self._interceptors:
                    await interceptor.after_execute(context)
            
            # 保存结果并清理
            self._chain_results[context.chain_id] = context.result
            if context.chain_id in self._active_chains:
                del self._active_chains[context.chain_id]
        
        return context.result
    
    def get_chain_context(self, chain_id: str) -> Optional[ChainContext]:
        """获取调用链上下文"""
        return self._active_chains.get(chain_id)
    
    def get_chain_result(self, chain_id: str) -> Any:
        """获取调用链执行结果"""
        return self._chain_results.get(chain_id)
    
    def cancel_chain(self, chain_id: str) -> bool:
        """取消调用链"""
        context = self._active_chains.get(chain_id)
        if context:
            context.status = ChainStatus.CANCELLED
            context.end_time = time.time()
            return True
        return False
    
    def get_active_chains(self) -> List[ChainContext]:
        """获取所有活跃的调用链"""
        return list(self._active_chains.values())
    
    def clear_finished_chains(self) -> None:
        """清理已完成的调用链"""
        finished_chains = [
            chain_id for chain_id, context in self._active_chains.items()
            if context.status not in [ChainStatus.PENDING, ChainStatus.RUNNING]
        ]
        for chain_id in finished_chains:
            del self._active_chains[chain_id]


# 内置拦截器实现
class LoggingInterceptor(ChainInterceptor):
    """日志记录拦截器"""
    
    async def before_execute(self, context: ChainContext) -> None:
        print(f"[Chain] 开始执行任务: {context.function_name} (ID: {context.chain_id})")
    
    async def after_execute(self, context: ChainContext) -> None:
        duration = context.duration
        print(f"[Chain] 任务完成: {context.function_name} (耗时: {duration:.3f}s)")
    
    async def on_error(self, context: ChainContext, error: Exception) -> None:
        print(f"[Chain] 任务出错: {context.function_name} - {error}")


class MetricsInterceptor(ChainInterceptor):
    """指标收集拦截器"""
    
    def __init__(self):
        self.metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_duration': 0.0
        }
    
    async def before_execute(self, context: ChainContext) -> None:
        self.metrics['total_executions'] += 1
    
    async def after_execute(self, context: ChainContext) -> None:
        if context.status == ChainStatus.SUCCESS:
            self.metrics['successful_executions'] += 1
            if context.duration:
                self.metrics['total_duration'] += context.duration
    
    async def on_error(self, context: ChainContext, error: Exception) -> None:
        self.metrics['failed_executions'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标数据"""
        metrics = self.metrics.copy()
        if self.metrics['successful_executions'] > 0:
            metrics['avg_duration'] = self.metrics['total_duration'] / self.metrics['successful_executions']
        else:
            metrics['avg_duration'] = 0.0
        return metrics


class TimeoutInterceptor(ChainInterceptor):
    """超时控制拦截器"""
    
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
    
    async def before_execute(self, context: ChainContext) -> None:
        # 在metadata中记录超时时间
        context.metadata['timeout'] = self.timeout_seconds
    
    async def after_execute(self, context: ChainContext) -> None:
        duration = context.duration
        if duration and duration > self.timeout_seconds:
            print(f"[Warning] 任务 {context.function_name} 执行超时: {duration:.3f}s (限制: {self.timeout_seconds}s)")


# 全局调用链实例
default_chain = CallChain()


def chain(
    func: Optional[Callable] = None,
    *,
    task_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Union[Callable, Any]:
    """调用链装饰器"""
    
    def decorator(f: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            return await default_chain.execute(
                f, *args, task_id=task_id, metadata=metadata, **kwargs
            )
        
        # 保持原始函数的元数据
        wrapper.__name__ = f.__name__
        wrapper.__doc__ = f.__doc__
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)