import time
import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable, Union, Dict, Any, Tuple, TypeAlias

from .Myclass import ClassNucleus

# Type alias
Context: TypeAlias = Dict[str, Any]
Condition: TypeAlias = Callable[[Context], bool | Awaitable[bool]]
Action: TypeAlias = Union["DecisionNode", Callable[[Context], Any | Awaitable[Any]]]

# 判断是否为异步函数并包裹
def maybe_async(func: Callable[[Context], Any]) -> Callable[[Context], Awaitable[Any]]:
    async def wrapper(ctx: Context):
        if asyncio.iscoroutinefunction(func):
            return await func(ctx)
        return func(ctx)
    return wrapper

@dataclass
class DecisionNode:
    condition: Condition
    if_true: Action
    if_false: Action | None = None

    async def evaluate(self, context: Context) -> Any:
        """递归评估决策逻辑树"""
        result = await maybe_async(self.condition)(context)
        next_node = self.if_true if result else self.if_false
        if isinstance(next_node, DecisionNode):
            return await next_node.evaluate(context)
        elif callable(next_node):
            return await maybe_async(next_node)(context)
        return next_node

class EventDispatcher:
    """事件调度器：触发普通事件"""
    def __init__(self):
        self.registry = ClassNucleus.get_registry()

    async def trigger_event(self, event_name: str, *args, **kwargs) -> Any:
        handler_cls = self.registry.get(event_name)
        if not handler_cls:
            return f"事件 {event_name} 未注册"
        execute = handler_cls.execute
        return await execute(*args, **kwargs) if asyncio.iscoroutinefunction(execute) else execute(*args, **kwargs)

class DecisionCommandDispatcher:
    """基于决策树的命令调度器"""
    def __init__(self):
        self.registry = ClassNucleus.get_registry()
        self.tree = self._build_tree()

    def _build_tree(self) -> DecisionNode:
        return DecisionNode(
            condition=lambda ctx: ctx["message"].startswith("/"),
            if_true=self._check_registered(),
            if_false=lambda ctx: "这不是一个命令"
        )

    def _check_registered(self) -> DecisionNode:
        return DecisionNode(
            condition=lambda ctx: "handler" in ctx,
            if_true=self._check_cooldown(),
            if_false=lambda ctx: f"未知命令: {ctx['command']}"
        )

    def _check_cooldown(self) -> DecisionNode:
        return DecisionNode(
            condition=lambda ctx: ctx.get("cooldown_passed", False),
            if_true=lambda ctx: ctx.get("exec_result", "命令执行失败"),
            if_false=lambda ctx: f"命令冷却中，请等待 {ctx['handler'].cooldown} 秒"
        )

    def _parse_command(self, message: str) -> Tuple[str, str]:
        if not message.startswith("/"):
            return "", ""
        parts = message.strip().split(" ", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    def _get_handler(self, ctx: Context) -> bool:
        cmd = ctx["command"]
        for cls in self.registry.values():
            if getattr(cls, "command", None) == cmd or cmd in getattr(cls, "aliases", []):
                ctx["handler"] = cls
                return True
        return False

    async def _check_cooldown_flag(self, ctx: Context) -> None:
        handler = ctx["handler"]
        if handler.cooldown <= 0:
            ctx["cooldown_passed"] = True
            return
        async with handler.cooldown_lock:
            now = time.time()
            if now - handler.last_executed >= handler.cooldown:
                handler.last_executed = now
                ctx["cooldown_passed"] = True
            else:
                ctx["cooldown_passed"] = False

    async def _execute(self, ctx: Context) -> None:
        handler = ctx["handler"]
        args = ctx["args"]
        parsed = handler.arg_parser(args) if handler.arg_parser else {"args": args.split()}
        exec_func = handler.execute
        ctx["exec_result"] = await exec_func(**parsed) if asyncio.iscoroutinefunction(exec_func) else exec_func(**parsed)

    async def handle(self, message: str) -> str:
        command, args = self._parse_command(message)
        ctx: Context = {"message": message, "command": command, "args": args}

        if command and self._get_handler(ctx):
            await self._check_cooldown_flag(ctx)
            if ctx.get("cooldown_passed"):
                await self._execute(ctx)

        return await self.tree.evaluate(ctx)
