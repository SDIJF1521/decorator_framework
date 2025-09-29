# decorators/on.py
import uuid
import asyncio
import inspect
from typing import List, Optional, Union, Callable, Dict, Any, Coroutine

from nucleus import Myclass
from nucleus.core import get_framework_integration, inject

class RegistryDecoratorTemplate:
    def __init__(self, name: str, *extra_args):
        self.name = name
        self.extra_args = extra_args
        self.fun = None

    def execute(self):
        def decorator(func):
            self.fun = func
            self._register_class()
            return func
        return decorator

    def _register_class(self) -> None:
        raise NotImplementedError

# @on 装饰器（普通事件注册，支持同步/异步函数）
def on(name: str) -> RegistryDecoratorTemplate:
    class OnDecorator(RegistryDecoratorTemplate):
        def _register_class(self) -> None:
            random_class_name = f"OnClass_{uuid.uuid4().hex[:8]}"
            
            # 创建支持依赖注入和调用链的执行函数
            async def execute_with_di(*args, **kwargs):
                # 获取框架集成
                framework = get_framework_integration()
                if not framework:
                    # 框架未启用，直接执行原函数
                    if asyncio.iscoroutinefunction(self.fun):
                        return await self.fun(*args, **kwargs)
                    else:
                        return self.fun(*args, **kwargs)
                
                # 使用依赖注入装饰器包装函数
                injected_func = framework.inject_dependencies(self.fun)
                
                # 使用调用链执行注入后的函数
                return await framework.call_chain.execute(
                    injected_func, *args, **kwargs
                )
            
            attrs = {
                "fun_name": self.name,
                "execute": staticmethod(execute_with_di)  # 支持依赖注入和调用链
            }
            Myclass.ClassNucleus(random_class_name, (object,), attrs)
    return OnDecorator(name)

# @command_on 装饰器（命令注册，支持异步/同步函数）
def command_on(
    name: str,
    command: str,
    aliases: list = None,
    cooldown: int = 0,
    arg_parser: Callable[[str], Dict[str, Any]] = None,
)-> RegistryDecoratorTemplate:
    if not command.startswith("/"):
        raise ValueError(f"命令 {command} 必须以 '/' 开头")

    class CommandDecorator(RegistryDecoratorTemplate):
        def _register_class(self) -> None:
            random_class_name = f"CommandClass_{uuid.uuid4().hex[:8]}"
            
            # 创建支持依赖注入和调用链的执行函数
            async def execute_with_di(*args, **kwargs):
                # 获取框架集成
                framework = get_framework_integration()
                if not framework:
                    # 框架未启用，直接执行原函数
                    if asyncio.iscoroutinefunction(self.fun):
                        return await self.fun(*args, **kwargs)
                    else:
                        return self.fun(*args, **kwargs)
                
                # 使用依赖注入装饰器包装函数
                injected_func = framework.inject_dependencies(self.fun)
                
                # 使用调用链执行注入后的函数
                return await framework.call_chain.execute(
                    injected_func, *args, **kwargs
                )
            
            class_attrs = {
                "fun_name": self.name,
                "command": command,
                "aliases": aliases or [],
                "cooldown": cooldown,
                "arg_parser": arg_parser,
                "execute": staticmethod(execute_with_di),  # 支持依赖注入和调用链
                "last_executed": 0,
                "cooldown_lock": asyncio.Lock(),  # 异步锁
            }
            Myclass.ClassNucleus(random_class_name, (object,), class_attrs)
    return CommandDecorator(name, command)

# @time_on装饰器（普通事件注册，支持同步/异步函数）
def time_on(
    name: str,
    priority: int = 1,
    interval: int = 0  # 改为interval参数
):
    class TimeOn(RegistryDecoratorTemplate):
        def _register_class(self) -> None:
            random_class_name = f"TimeHandler_{uuid.uuid4().hex[:8]}"
            
            # 创建支持依赖注入和调用链的执行函数
            async def execute_with_di(*args, **kwargs):
                # 获取框架集成
                framework = get_framework_integration()
                if not framework:
                    # 框架未启用，直接执行原函数
                    if asyncio.iscoroutinefunction(self.fun):
                        return await self.fun(*args, **kwargs)
                    else:
                        return self.fun(*args, **kwargs)
                
                # 使用依赖注入装饰器包装函数
                injected_func = framework.inject_dependencies(self.fun)
                
                # 使用调用链执行注入后的函数
                return await framework.call_chain.execute(
                    injected_func, *args, **kwargs
                )
            
            attrs = {
                "fun_name": self.name,
                "priority": priority,
                "interval": interval,  # 改为interval属性
                "execute": staticmethod(execute_with_di)  # 支持依赖注入和调用链
            }
            Myclass.ClassNucleus(random_class_name, (object,), attrs)
    return TimeOn(name)

# @re_on装饰器(普通事件注册，支持同步/异步函数)
def re_on(
    name: str,
    content: str,
    pattern: object,
    priority: int = 1,
)-> RegistryDecoratorTemplate:
    class ReOn(RegistryDecoratorTemplate):
        def _register_class(self) -> None:
            random_class_name = f"ReHandler_{uuid.uuid4().hex[:8]}"
            
            # 创建支持依赖注入和调用链的执行函数
            async def execute_with_di(*args, **kwargs):
                # 获取框架集成
                framework = get_framework_integration()
                if not framework:
                    # 框架未启用，直接执行原函数
                    if asyncio.iscoroutinefunction(self.fun):
                        return await self.fun(*args, **kwargs)
                    else:
                        return self.fun(*args, **kwargs)
                
                # 使用依赖注入装饰器包装函数
                injected_func = framework.inject_dependencies(self.fun)
                
                # 使用调用链执行注入后的函数
                return await framework.call_chain.execute(
                    injected_func, *args, **kwargs
                )
            
            attrs = {
                "fun_name": self.name,
                "priority": priority,
                "content": content,
                "rule": pattern,
                "execute": staticmethod(execute_with_di)  # 支持依赖注入和调用链
            }
            Myclass.ClassNucleus(random_class_name, (object,), attrs)

    return ReOn(name)