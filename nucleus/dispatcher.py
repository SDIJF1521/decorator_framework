import re
import time
import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable, Union, Dict, Any, Tuple, TypeAlias,Optional, List

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

# 定时事件调度器
class TimeTaskScheduler:
    """定时任务调度器：处理time_on装饰器注册的任务"""

    def __init__(self):
        self.registry = ClassNucleus.get_registry()
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.time_tasks: List[Dict[str, Any]] = []  # 存储任务详情
        self.check_interval = 1  # 检查周期（秒）

    def load_time_tasks(self) -> None:
        """从注册器加载所有定时任务"""
        self.time_tasks.clear()
        for name, cls in self.registry.items():
            if hasattr(cls, 'interval') and hasattr(cls, 'execute'):
                interval = getattr(cls, 'interval', 0)
                if interval > 0:  # 只加载有时间间隔的任务
                    self.time_tasks.append({
                        'priority': getattr(cls, 'priority', 1),
                        'interval': interval,
                        'handler': cls.execute,
                        'last_executed': time.time()  # 记录每个任务的上次执行时间
                    })

        # 按优先级排序（数字越小优先级越高）
        self.time_tasks.sort(key=lambda x: x['priority'])
        print(f"已加载 {len(self.time_tasks)} 个定时任务")

    async def execute_due_tasks(self) -> None:
        """执行所有到期的定时任务"""
        current_time = time.time()

        for task in self.time_tasks:
            elapsed = current_time - task['last_executed']
            if elapsed >= task['interval']:
                # 使用异步执行任务，避免阻塞调度器
                asyncio.create_task(self._run_task(task))
                task['last_executed'] = current_time  # 更新任务的上次执行时间

    async def _run_task(self, task: Dict[str, Any]) -> None:
        """安全执行任务，捕获异常"""
        try:
            handler = task['handler']
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
            print(f"任务执行成功: {handler.__name__}")
        except Exception as e:
            print(f"定时任务执行出错: {e}")

    async def scheduler_loop(self) -> None:
        """调度器主循环"""
        while self.running:
            await self.execute_due_tasks()
            await asyncio.sleep(self.check_interval)  # 使用固定的检查周期

    async def start(self) -> None:
        """启动调度器"""
        if not self.running:
            self.load_time_tasks()
            if not self.time_tasks:
                print("警告: 没有注册的定时任务")
                return

            self.running = True
            self.task = asyncio.create_task(self.scheduler_loop())
            print("定时任务调度器已启动")
            print("注册的任务:", [task['handler'].__name__ for task in self.time_tasks])

    async def stop(self) -> None:
        """停止调度器"""
        if self.running and self.task:
            self.running = False
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            print("定时任务调度器已停止")

# 正则规则调度器
class ReTaskScheduler:
    """正则任务调度器：处理re_on装饰器注册的任务"""
    
    def __init__(self):
        self.registry = ClassNucleus.get_registry()
    
    def _get_regex_handlers(self) -> list:
        """获取所有正则任务处理器"""
        handlers = []
        for name, cls in self.registry.items():
            if hasattr(cls, 'rule'):
                handlers.append({
                    'name': getattr(cls, 'fun_name', name),
                    'pattern': cls.rule,
                    'handler': cls.execute,
                    'priority': getattr(cls, 'priority', 1)
                })
        
        # 按优先级排序（数字越小优先级越高）
        handlers.sort(key=lambda x: x['priority'])
        return handlers
    
    async def trigger(self, task_name: str, content: str) -> list[str]:
        """
        触发正则任务
        
        Args:
            task_name: 任务名称
            content: 要匹配的内容
            
        Returns:
            匹配成功的任务执行结果列表
        """
        handlers = self._get_regex_handlers()
        results = []
        
        for handler_info in handlers:
            if handler_info['name'] == task_name:
                pattern = handler_info['pattern']
                
                # 检查正则表达式匹配
                regex_matches = False
                try:
                    if isinstance(pattern, str):
                        regex_matches = bool(re.search(pattern, content))
                    else:
                        regex_matches = bool(pattern.search(content)) if hasattr(pattern, 'search') else False
                except Exception as e:
                    print(f"正则表达式匹配错误: {e}")
                
                if regex_matches:
                    try:
                        handler = handler_info['handler']
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler()
                        else:
                            result = handler()
                        results.append(str(result) if result is not None else f"任务 {task_name} 执行完成")
                        print(f"正则任务触发成功: {task_name}")
                    except Exception as e:
                        error_msg = f"任务 {task_name} 执行失败: {e}"
                        print(error_msg)
                        results.append(error_msg)
        
        return results
    
    async def match_content(self, content: str) -> list[str]:
        """
        匹配所有注册的正则任务
        
        Args:
            content: 要匹配的内容
            
        Returns:
            所有匹配成功的任务执行结果列表
        """
        handlers = self._get_regex_handlers()
        results = []
        
        for handler_info in handlers:
            pattern = handler_info['pattern']
            
            # 检查内容是否匹配正则表达式
            regex_matches = False
            try:
                if isinstance(pattern, str):
                    regex_matches = bool(re.search(pattern, content))
                else:
                    regex_matches = bool(pattern.search(content)) if hasattr(pattern, 'search') else False
            except Exception as e:
                print(f"正则表达式匹配错误: {e}")
            
            if regex_matches:
                try:
                    handler = handler_info['handler']
                    task_name = handler_info['name']
                    
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler()
                    else:
                        result = handler()
                    
                    results.append(str(result) if result is not None else f"任务 {task_name} 执行完成")
                    print(f"正则任务匹配成功: {task_name}")
                except Exception as e:
                    error_msg = f"任务 {handler_info['name']} 执行失败: {e}"
                    print(error_msg)
                    results.append(error_msg)
        
        return results