# decorators/on.py
import uuid
import asyncio
from typing import List, Optional, Union, Callable, Dict, Any, Coroutine

from nucleus import Myclass

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
            attrs = {
                "fun_name": self.name,
                "execute": staticmethod(self.fun)  # 支持异步函数
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
):
    if not command.startswith("/"):
        raise ValueError(f"命令 {command} 必须以 '/' 开头")

    class CommandDecorator(RegistryDecoratorTemplate):
        def _register_class(self) -> None:
            random_class_name = f"CommandClass_{uuid.uuid4().hex[:8]}"
            class_attrs = {
                "fun_name": self.name,
                "command": command,
                "aliases": aliases or [],
                "cooldown": cooldown,
                "arg_parser": arg_parser,
                "execute": staticmethod(self.fun),
                "last_executed": 0,
                "cooldown_lock": asyncio.Lock(),  # 异步锁
            }
            Myclass.ClassNucleus(random_class_name, (object,), class_attrs)
    return CommandDecorator(name, command)