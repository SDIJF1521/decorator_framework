"""
核心功能模块 - 调用链、依赖注入和任务管理
"""
from .chain import (
    CallChain,
    ChainContext,
    ChainInterceptor,
    ChainStatus,
    LoggingInterceptor,
    MetricsInterceptor,
    TimeoutInterceptor
)

from .di import (
    DependencyContainer,
    ServiceLifetime,
    ServiceDescriptor,
    ServiceScope,
    Injectable,
    Singleton
)

from .task_manager import (
    TaskManager,
    TaskInfo,
    TaskStatus,
    TaskCancellationToken,
    default_task_manager,
    task
)

from .integration import (
    FrameworkIntegration,
    enable_framework_integration,
    inject,
    service,
    task_with_chain,
    get_task_manager,
    get_dependency_container,
    get_call_chain,
    get_framework_integration,
    framework_integration
)

__all__ = [
    # 调用链
    'CallChain',
    'ChainContext',
    'ChainInterceptor',
    'ChainStatus',
    'LoggingInterceptor',
    'MetricsInterceptor',
    'TimeoutInterceptor',
    
    # 依赖注入
    'DependencyContainer',
    'ServiceLifetime',
    'ServiceDescriptor',
    'ServiceScope',
    'Injectable',
    'Singleton',
    
    # 任务管理
    'TaskManager',
    'TaskInfo',
    'TaskStatus',
    'TaskCancellationToken',
    'default_task_manager',
    'task',
    
    # 集成
    'FrameworkIntegration',
    'enable_framework_integration',
    'inject',
    'service',
    'task_with_chain',
    'get_task_manager',
    'get_dependency_container',
    'get_call_chain',
    'get_framework_integration',
    'framework_integration'
]