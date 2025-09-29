"""
集成模块 - 将调用链、依赖注入和任务管理集成到框架中
"""
import asyncio
import inspect
from typing import Any, Dict, List, Optional, Callable, Type, Union
from functools import wraps

from .chain import CallChain, ChainContext, ChainInterceptor
from .di import DependencyContainer, Injectable, Singleton, ServiceLifetime
from .task_manager import TaskManager, TaskCancellationToken, default_task_manager


class FrameworkIntegration:
    """框架集成器"""
    
    def __init__(self, container: Optional[DependencyContainer] = None, task_manager: Optional[TaskManager] = None):
        self.container = container or DependencyContainer()
        self.task_manager = task_manager or default_task_manager
        self.call_chain = CallChain()
        self._integration_enabled = False
    
    def enable_integration(self) -> None:
        """启用集成"""
        self._integration_enabled = True
        
        # 注册核心服务到依赖注入容器
        self._register_core_services()
        
        # 设置调用链拦截器
        self._setup_interceptors()
        
        # 添加内置拦截器
        self._add_builtin_interceptors()
    
    def _register_core_services(self) -> None:
        """注册核心服务"""
        # 注册任务管理器
        self.container.register_instance(TaskManager, self.task_manager)
        
        # 注册依赖注入容器本身
        self.container.register_instance(DependencyContainer, self.container)
        
        # 注册调用链
        self.container.register_instance(CallChain, self.call_chain)
    
    def _setup_interceptors(self) -> None:
        """设置调用链拦截器"""
        # 添加任务管理拦截器
        class TaskManagementInterceptor(ChainInterceptor):
            def __init__(self, task_manager):
                self.task_manager = task_manager
            
            async def before_execute(self, context: ChainContext) -> None:
                # 创建任务
                target = context.metadata.get('target')
                if target and inspect.iscoroutinefunction(target):
                    task_id = self.task_manager.create_task(
                        coro=target(*context.args, **context.kwargs),
                        name=context.function_name,
                        metadata={
                            'chain_id': context.chain_id,
                            'target_name': getattr(target, '__name__', str(target)),
                            'args': str(context.args),
                            'kwargs': str(context.kwargs)
                        }
                    )
                    context.metadata['task_id'] = task_id
            
            async def after_execute(self, context: ChainContext) -> None:
                # 任务完成处理
                task_id = context.metadata.get('task_id')
                if task_id:
                    task_info = self.task_manager.get_task_info(task_id)
                    if task_info and task_info.status.value == 'completed':
                        context.metadata['task_result'] = task_info.result
            
            async def on_error(self, context: ChainContext, error: Exception) -> None:
                # 任务错误处理
                task_id = context.metadata.get('task_id')
                if task_id:
                    task_info = self.task_manager.get_task_info(task_id)
                    if task_info:
                        context.metadata['task_error'] = task_info.error
        
        # 创建拦截器实例并添加到调用链
        task_interceptor = TaskManagementInterceptor(self.task_manager)
        self.call_chain.add_interceptor(task_interceptor)
    
    def _add_builtin_interceptors(self) -> None:
        """添加内置拦截器"""
        # 添加日志拦截器
        from .chain import LoggingInterceptor
        self.call_chain.add_interceptor(LoggingInterceptor())
        
        # 添加指标收集拦截器
        from .chain import MetricsInterceptor
        self.call_chain.add_interceptor(MetricsInterceptor())
    
    def inject_dependencies(self, func: Callable) -> Callable:
        """依赖注入装饰器"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self._integration_enabled:
                return await func(*args, **kwargs)
            
            # 获取函数签名
            sig = inspect.signature(func)
            
            # 解析依赖
            injected_kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    continue
                
                param_type = param.annotation
                if param_type != inspect.Parameter.empty:
                    try:
                        # 从容器中解析依赖
                        instance = self.container.resolve(param_type)
                        injected_kwargs[param_name] = instance
                    except Exception:
                        # 如果解析失败，跳过该参数
                        continue
            
            # 合并参数
            final_kwargs = {**injected_kwargs, **kwargs}
            
            # 通过调用链执行
            if self._integration_enabled:
                return await self.call_chain.execute(
                    func,
                    *args,
                    task_id=None,
                    metadata={'target': func, 'args': args, 'kwargs': final_kwargs},
                    **final_kwargs
                )
            else:
                return await func(*args, **final_kwargs)
        
        return wrapper
    
    def create_service(self, service_type: Type, lifetime: str = 'singleton') -> Type:
        """创建服务类"""
        from .di import ServiceLifetime
        
        # 注册服务到容器 - 支持接口到实现的映射
        if hasattr(service_type, '__bases__') and service_type.__bases__:
            # 如果有基类，注册接口到实现的映射
            for base_class in service_type.__bases__:
                if base_class != object:
                    # 注册基类（接口）到实现类的映射
                    if lifetime == 'singleton':
                        self.container.register_singleton(base_class, service_type)
                    elif lifetime == 'scoped':
                        self.container.register_scoped(base_class, service_type)
                    else:
                        self.container.register_transient(base_class, service_type)
        
        # 同时注册实现类自身
        if lifetime == 'singleton':
            self.container.register_singleton(service_type, service_type)
        elif lifetime == 'scoped':
            self.container.register_scoped(service_type, service_type)
        else:
            self.container.register_transient(service_type, service_type)
        
        return service_type
    
    def register_service(self, service_type: Type, implementation: Optional[Type] = None, lifetime: str = 'singleton') -> None:
        """注册服务"""
        if implementation is None:
            implementation = service_type
        
        if lifetime == 'singleton':
            self.container.register_singleton(service_type, implementation)
        else:
            self.container.register_transient(service_type, implementation)
    
    def resolve_service(self, service_type: Type) -> Any:
        """解析服务"""
        return self.container.resolve(service_type)
    
    def create_task_with_chain(self, coro: Callable, name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """通过调用链创建任务"""
        if not self._integration_enabled:
            return self.task_manager.create_task(coro(), name, metadata)
        
        # 创建链式上下文
        chain_id = self.call_chain.generate_chain_id()
        context = ChainContext(
            chain_id=chain_id,
            task_id=chain_id,
            function_name=name or getattr(coro, '__name__', 'task'),
            args=(),
            kwargs={},
            metadata={'target': coro, **(metadata or {})}
        )
        
        # 执行调用链
        async def chain_wrapper():
            return await self.call_chain.execute_with_context(context)
        
        return self.task_manager.create_task(chain_wrapper(), name, metadata)
    
    def add_chain_interceptor(self, interceptor: ChainInterceptor) -> None:
        """添加调用链拦截器"""
        self.call_chain.add_interceptor(interceptor)
    
    def get_task_manager(self) -> TaskManager:
        """获取任务管理器"""
        return self.task_manager
    
    def get_dependency_container(self) -> DependencyContainer:
        """获取依赖注入容器"""
        return self.container
    
    def get_call_chain(self) -> CallChain:
        """获取调用链"""
        return self.call_chain
    
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        task_info = self.task_manager.get_task_info(task_id)
        if task_info:
            return {
                'task_id': task_info.task_id,
                'name': task_info.name,
                'status': task_info.status.value,
                'created_at': task_info.created_at,
                'started_at': task_info.started_at,
                'completed_at': task_info.completed_at,
                'duration': task_info.duration,
                'wait_time': task_info.wait_time,
                'result': task_info.result,
                'error': str(task_info.error) if task_info.error else None,
                'metadata': task_info.metadata,
                'parent_task_id': task_info.parent_task_id,
                'child_task_ids': task_info.child_task_ids
            }
        return None
    
    def get_all_tasks_info(self) -> List[Dict[str, Any]]:
        """获取所有任务信息"""
        all_tasks = self.task_manager.get_all_tasks()
        return [self.get_task_info(task.task_id) for task in all_tasks if task]
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        return asyncio.run(self.task_manager.cancel_task(task_id))
    
    def cancel_all_tasks(self) -> int:
        """取消所有任务"""
        return self.task_manager.cancel_all_tasks()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.task_manager.get_statistics()


# 全局集成器实例
framework_integration = FrameworkIntegration()

# 延迟注册的服务列表
_pending_services = []


def _register_pending_services():
    """注册所有待处理的服务"""
    global _pending_services
    
    # 创建待处理服务的副本，避免在迭代时修改列表
    pending_copy = _pending_services.copy()
    
    for service_info in pending_copy:
        service_type, lifetime_str = service_info
        container = framework_integration.container
        
        # 转换字符串生命周期为枚举
        if lifetime_str == 'singleton':
            lifetime = ServiceLifetime.SINGLETON
        elif lifetime_str == 'scoped':
            lifetime = ServiceLifetime.SCOPED
        else:
            lifetime = ServiceLifetime.TRANSIENT
        
        # 注册服务到容器 - 支持接口到实现的映射
        if hasattr(service_type, '__bases__') and service_type.__bases__:
            # 如果有基类，注册接口到实现的映射
            registered = False
            for base_class in service_type.__bases__:
                if base_class != object:
                    # 注册基类（接口）到实现类的映射
                    container.register(base_class, service_type, lifetime=lifetime)
                    registered = True
            
            # 如果没有有效的基类映射，注册实现类自身
            if not registered:
                container.register(service_type, service_type, lifetime=lifetime)
        else:
            # 没有基类（接口），直接注册实现类自身
            container.register(service_type, service_type, lifetime=lifetime)
    
    # 清空待处理列表
    _pending_services.clear()


def enable_framework_integration() -> FrameworkIntegration:
    """启用框架集成"""
    framework_integration.enable_integration()
    # 注册所有待处理的服务
    _register_pending_services()
    return framework_integration


def inject(func: Callable) -> Callable:
    """依赖注入装饰器"""
    return framework_integration.inject_dependencies(func)


def service(lifetime_or_interface: Union[str, Type] = 'singleton') -> Callable:
    """服务装饰器 - 延迟注册版本
    
    支持两种使用方式：
    1. @service() - 默认单例
    2. @service('singleton') - 指定生命周期
    3. @service(IMyInterface) - 指定接口映射
    """
    def decorator(service_type: Type) -> Type:
        # 确定生命周期和接口映射
        if isinstance(lifetime_or_interface, str):
            lifetime = lifetime_or_interface
            interface_type = None
        elif isinstance(lifetime_or_interface, type):
            # 如果传入的是类型，将其作为接口映射
            lifetime = 'singleton'  # 默认使用单例
            interface_type = lifetime_or_interface
        else:
            lifetime = 'singleton'
            interface_type = None
        
        # 如果框架已经启用，立即注册服务
        if framework_integration._integration_enabled:
            container = framework_integration.container
            
            # 转换字符串生命周期为枚举
            if lifetime == 'singleton':
                lifetime_enum = ServiceLifetime.SINGLETON
            elif lifetime == 'scoped':
                lifetime_enum = ServiceLifetime.SCOPED
            else:
                lifetime_enum = ServiceLifetime.TRANSIENT
            
            # 注册服务到容器 - 支持接口到实现的映射
            if interface_type:
                # 指定了接口映射
                container.register(interface_type, service_type, lifetime=lifetime_enum)
            elif hasattr(service_type, '__bases__') and service_type.__bases__:
                # 有基类，注册接口到实现的映射
                registered = False
                for base_class in service_type.__bases__:
                    if base_class != object:
                        # 注册基类（接口）到实现类的映射
                        container.register(base_class, service_type, lifetime=lifetime_enum)
                        registered = True
                
                # 如果没有有效的基类映射，注册实现类自身
                if not registered:
                    container.register(service_type, service_type, lifetime=lifetime_enum)
            else:
                # 没有基类（接口），直接注册实现类自身
                container.register(service_type, service_type, lifetime=lifetime_enum)
        else:
            # 框架未启用，添加到待处理列表
            _pending_services.append((service_type, lifetime))
        
        return service_type
    return decorator


def task_with_chain(name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Callable:
    """链式任务装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 创建任务
            async def coro():
                return await func(*args, **kwargs)
            
            task_id = framework_integration.create_task_with_chain(coro, name, metadata)
            
            # 等待任务完成
            return await framework_integration.task_manager.wait_for_task_async(task_id)
        
        return wrapper
    return decorator


def get_task_manager() -> TaskManager:
    """获取任务管理器"""
    return framework_integration.get_task_manager()


def get_dependency_container() -> DependencyContainer:
    """获取依赖注入容器"""
    return framework_integration.get_dependency_container()


def get_call_chain() -> CallChain:
    """获取调用链"""
    return framework_integration.get_call_chain()


def get_framework_integration() -> FrameworkIntegration:
    """获取框架集成器"""
    return framework_integration