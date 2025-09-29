"""
依赖注入容器实现 - 支持组件的自动装配
"""
import inspect
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, TypeVar, Callable, Optional, Union, get_type_hints, Set
from dataclasses import dataclass
from enum import Enum
from functools import wraps


class ServiceLifetime(Enum):
    """服务生命周期"""
    TRANSIENT = "transient"  # 每次请求创建新实例
    SINGLETON = "singleton"  # 单例模式
    SCOPED = "scoped"        # 作用域内单例


@dataclass
class ServiceDescriptor:
    """服务描述符"""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Any = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT


T = TypeVar('T')


class DependencyContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_cache: Dict[str, Dict[Type, Any]] = {}
    
    def register(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None,
        instance: Optional[T] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ) -> None:
        """注册服务"""
        if implementation_type is None and factory is None and instance is None:
            implementation_type = service_type
        
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            instance=instance,
            lifetime=lifetime
        )
        
        self._services[service_type] = descriptor
        
        # 如果是单例，立即创建实例
        if lifetime == ServiceLifetime.SINGLETON and instance is None and factory is None:
            self._singletons[service_type] = self._create_instance(descriptor)
    
    def register_transient(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None
    ) -> None:
        """注册瞬态服务"""
        self.register(service_type, implementation_type, lifetime=ServiceLifetime.TRANSIENT)
    
    def register_singleton(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        instance: Optional[T] = None
    ) -> None:
        """注册单例服务"""
        self.register(service_type, implementation_type, instance=instance, lifetime=ServiceLifetime.SINGLETON)
    
    def register_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None
    ) -> None:
        """注册作用域服务"""
        self.register(service_type, implementation_type, lifetime=ServiceLifetime.SCOPED)
    
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """注册实例"""
        self.register(service_type, instance=instance, lifetime=ServiceLifetime.SINGLETON)
    
    def _create_instance(self, descriptor: ServiceDescriptor, scope_id: Optional[str] = None) -> Any:
        """创建服务实例"""
        # 如果已有实例，直接返回
        if descriptor.instance is not None:
            return descriptor.instance
        
        # 如果使用工厂方法
        if descriptor.factory is not None:
            result = descriptor.factory()
            if asyncio.iscoroutine(result):
                # 异步工厂方法
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(result)
            return result
        
        # 创建新实例
        if descriptor.implementation_type is None:
            raise ValueError(f"无法创建服务实例: {descriptor.service_type}")
        
        implementation_type = descriptor.implementation_type
        
        # 获取构造函数参数
        try:
            sig = inspect.signature(implementation_type.__init__)
            params = list(sig.parameters.values())[1:]  # 跳过self参数
            
            # 解析依赖
            dependencies = {}
            for param in params:
                if param.annotation != inspect.Parameter.empty:
                    # 有类型注解，尝试解析依赖
                    dependency = self.resolve(param.annotation, scope_id)
                    dependencies[param.name] = dependency
                else:
                    # 无类型注解，尝试按名称解析
                    try:
                        dependency = self.resolve_by_name(param.name)
                        if dependency is not None:
                            dependencies[param.name] = dependency
                    except:
                        pass  # 忽略无法解析的参数
            
            # 创建实例
            instance = implementation_type(**dependencies)
            return instance
            
        except Exception as e:
            # 如果自动注入失败，尝试无参构造
            try:
                return implementation_type()
            except:
                raise ValueError(f"创建服务实例失败: {implementation_type}, 错误: {e}")
    
    def resolve(self, service_type: Type[T], scope_id: Optional[str] = None) -> T:
        """解析服务"""
        descriptor = self._services.get(service_type)
        if descriptor is None:
            raise ValueError(f"未注册的服务: {service_type}")
        
        # 处理生命周期
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type not in self._singletons:
                self._singletons[service_type] = self._create_instance(descriptor)
            return self._singletons[service_type]
        
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if scope_id is None:
                # 如果没有作用域ID，回退到瞬态
                return self._create_instance(descriptor)
            
            if scope_id not in self._scoped_cache:
                self._scoped_cache[scope_id] = {}
            
            scoped_instances = self._scoped_cache[scope_id]
            if service_type not in scoped_instances:
                scoped_instances[service_type] = self._create_instance(descriptor, scope_id)
            return scoped_instances[service_type]
        
        else:  # TRANSIENT
            return self._create_instance(descriptor, scope_id)
    
    def resolve_by_name(self, name: str) -> Any:
        """按名称解析服务"""
        # 查找匹配的服务
        for service_type, descriptor in self._services.items():
            if (hasattr(service_type, '__name__') and 
                service_type.__name__.lower() == name.lower()):
                return self.resolve(service_type)
        return None
    
    def create_scope(self, scope_id: str) -> 'ServiceScope':
        """创建作用域"""
        return ServiceScope(self, scope_id)
    
    def clear_scope(self, scope_id: str) -> None:
        """清理作用域"""
        if scope_id in self._scoped_cache:
            del self._scoped_cache[scope_id]
    
    def clear_singletons(self) -> None:
        """清理所有单例"""
        self._singletons.clear()
    
    def get_registered_services(self) -> List[str]:
        """获取已注册的服务类型"""
        return list(self._services.keys())


class ServiceScope:
    """服务作用域"""
    
    def __init__(self, container: DependencyContainer, scope_id: str):
        self.container = container
        self.scope_id = scope_id
    
    def resolve(self, service_type: Type[T]) -> T:
        """在作用域内解析服务"""
        return self.container.resolve(service_type, self.scope_id)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.clear_scope(self.scope_id)


# 全局容器实例
default_container = DependencyContainer()


# 装饰器
class Injectable:
    """可注入服务基类"""
    
    def __init_subclass__(cls, *, lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
        """自动注册子类"""
        default_container.register(cls, lifetime=lifetime)


class Singleton(Injectable):
    """单例服务基类"""
    
    def __init_subclass__(cls):
        super().__init_subclass__(lifetime=ServiceLifetime.SINGLETON)


class Transient(Injectable):
    """瞬态服务基类"""
    
    def __init_subclass__(cls):
        super().__init_subclass__(lifetime=ServiceLifetime.TRANSIENT)


class Scoped(Injectable):
    """作用域服务基类"""
    
    def __init_subclass__(cls):
        super().__init_subclass__(lifetime=ServiceLifetime.SCOPED)


def inject(func: Callable) -> Callable:
    """依赖注入装饰器"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取函数签名
        sig = inspect.signature(func)
        
        # 解析依赖
        dependencies = {}
        for param_name, param in sig.parameters.items():
            if param_name in kwargs:
                # 如果参数已提供，跳过
                continue
            
            if param.annotation != inspect.Parameter.empty:
                # 有类型注解，尝试解析依赖
                try:
                    dependency = default_container.resolve(param.annotation)
                    dependencies[param_name] = dependency
                except:
                    pass  # 忽略无法解析的参数
        
        # 合并参数
        final_kwargs = {**dependencies, **kwargs}
        
        # 调用函数
        result = func(*args, **final_kwargs)
        
        # 处理异步函数
        if asyncio.iscoroutine(result):
            async def async_wrapper():
                return await result
            return async_wrapper()
        
        return result
    
    return wrapper


def service(
    service_type: Optional[Type] = None,
    *,
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    factory: Optional[Callable] = None,
    instance: Any = None
) -> Callable:
    """服务注册装饰器"""
    
    def decorator(cls: Type) -> Type:
        # 注册服务
        if service_type is None:
            register_type = cls
        else:
            register_type = service_type
        
        default_container.register(
            register_type,
            implementation_type=cls,
            factory=factory,
            instance=instance,
            lifetime=lifetime
        )
        
        return cls
    
    return decorator