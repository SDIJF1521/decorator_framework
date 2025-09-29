import re
import time
import asyncio
import threading
from dataclasses import dataclass
from typing import Callable, Awaitable, Union, Dict, Any, Tuple, TypeAlias,Optional, List

from .Myclass import ClassNucleus
from .data.priority_queue import PriorityQueue, ResourceController

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
    """事件调度器：触发普通事件，使用优先级队列管理事件处理"""
    def __init__(self):
        self.registry = ClassNucleus.get_registry()
        
        # 使用优先级队列管理事件处理
        self.event_queue = PriorityQueue(
            max_size=200,
            max_memory_mb=20,
            name="事件处理队列"
        )
        self.event_resource_controller = ResourceController(
            max_size=5,  # 最大并发事件处理数
            max_memory_mb=10
        )
        self.active_event_handlers = set()
        self.event_lock = threading.Lock()
        self.event_processing_task = None
        self.event_processing = False

    async def trigger_event(self, event_name: str, priority: int = 5, *args, **kwargs) -> Any:
        """触发事件，使用优先级队列管理事件处理
        
        Args:
            event_name: 事件名称
            priority: 事件优先级（数字越小优先级越高，默认5）
            *args: 位置参数
            **kwargs: 关键字参数
        """
        handler_cls = self.registry.get(event_name)
        if not handler_cls:
            return f"事件 {event_name} 未注册"
        
        # 创建事件处理任务
        event_data = {
            'event_name': event_name,
            'handler_cls': handler_cls,
            'args': args,
            'kwargs': kwargs,
            'timestamp': time.time(),
            'event_id': f"{event_name}_{int(time.time() * 1000)}"
        }
        
        # 将事件加入优先级队列
        success = self.event_queue.put(event_data, priority=priority)
        if not success:
            return f"事件 {event_name} 加入队列失败（队列满或资源不足）"
        
        # 启动事件处理（如果未运行）
        if not self.event_processing:
            await self._start_event_processing()
        
        return f"事件 {event_name} 已加入处理队列（优先级: {priority}）"
    
    async def _start_event_processing(self) -> None:
        """启动事件处理"""
        if not self.event_processing:
            self.event_processing = True
            self.event_processing_task = asyncio.create_task(self._process_events())
    
    async def _process_events(self) -> None:
        """处理事件队列"""
        while self.event_processing:
            # 检查资源限制
            with self.event_lock:
                if len(self.active_event_handlers) >= self.event_resource_controller.max_size:
                    await asyncio.sleep(0.1)
                    continue
            
            # 从队列获取事件
            event_data = self.event_queue.get(timeout=0.1)
            if not event_data:
                # 队列为空，检查是否继续处理
                if self.event_queue.empty():
                    await asyncio.sleep(0.5)
                continue
            
            # 创建事件处理任务
            handler_coro = self._handle_event_async(event_data)
            handler_future = asyncio.create_task(handler_coro)
            
            with self.event_lock:
                self.active_event_handlers.add(handler_future)
            
            # 设置完成回调
            handler_future.add_done_callback(
                lambda f: self._on_event_handler_complete(f)
            )
    
    async def _handle_event_async(self, event_data: Dict[str, Any]) -> None:
        """异步处理单个事件"""
        try:
            handler_cls = event_data['handler_cls']
            execute = handler_cls.execute
            
            # 执行事件处理，现在execute函数已经支持依赖注入和调用链
            result = await execute(*event_data['args'], **event_data['kwargs'])
            
            print(f"事件处理成功: {event_data['event_name']} (优先级: {event_data.get('priority', 'N/A')})")
            return result
            
        except Exception as e:
            print(f"事件处理出错: {event_data['event_name']}: {e}")
            return f"事件处理出错: {e}"
    
    def _on_event_handler_complete(self, future: asyncio.Future) -> None:
        """事件处理完成回调"""
        with self.event_lock:
            self.active_event_handlers.discard(future)
    
    def stop_event_processing(self) -> None:
        """停止事件处理"""
        self.event_processing = False
        if self.event_processing_task:
            self.event_processing_task.cancel()
    
    def register_event(self, event_name: str, handler_cls: type) -> bool:
        """注册事件处理器
        
        Args:
            event_name: 事件名称
            handler_cls: 处理器类（必须定义fun_name属性）
            
        Returns:
            bool: 是否注册成功
        """
        try:
            # 检查处理器类是否已经注册
            registry = ClassNucleus.get_registry()
            if event_name in registry:
                return True
            
            # 检查处理器类是否有fun_name属性
            if not hasattr(handler_cls, 'fun_name'):
                # 动态添加fun_name属性
                handler_cls.fun_name = event_name
            
            return True
        except Exception as e:
            print(f"事件注册失败: {e}")
            return False
    
    def get_event_queue_stats(self) -> Dict[str, Any]:
        """获取事件队列统计"""
        queue_stats = self.event_queue.get_stats()
        resource_stats = self.event_resource_controller.get_resource_usage()
        
        return {
            'queue_stats': queue_stats,
            'resource_stats': resource_stats,
            'active_handlers': len(self.active_event_handlers),
            'processing': self.event_processing
        }

class DecisionCommandDispatcher:
    """基于决策树的命令调度器，使用优先级队列管理命令执行"""
    def __init__(self):
        self.registry = ClassNucleus.get_registry()
        self.tree = self._build_tree()
        
        # 使用优先级队列管理命令执行
        self.command_queue = PriorityQueue(
            max_size=50,
            max_memory_mb=10,
            name="命令执行队列"
        )
        self.command_resource_controller = ResourceController(
            max_size=3,  # 最大并发命令数
            max_memory_mb=5
        )
        self.active_commands = set()
        self.command_lock = threading.Lock()
        self.command_processing = False
        self.command_processor_task = None

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
        # execute函数已经支持依赖注入和调用链，直接调用即可
        ctx["exec_result"] = await exec_func(**parsed)

    async def handle(self, message: str, priority: int = 5) -> str:
        """处理命令，使用优先级队列管理命令执行
        
        Args:
            message: 命令消息
            priority: 命令优先级（数字越小优先级越高，默认5）
        """
        command, args = self._parse_command(message)
        ctx: Context = {"message": message, "command": command, "args": args}

        if command and self._get_handler(ctx):
            await self._check_cooldown_flag(ctx)
            if ctx.get("cooldown_passed"):
                # 将命令加入优先级队列执行
                return await self._queue_command(ctx, priority)
            else:
                # 冷却中的命令直接返回结果
                return await self.tree.evaluate(ctx)
        else:
            # 非命令消息直接评估
            return await self.tree.evaluate(ctx)
    
    async def _queue_command(self, ctx: Context, priority: int) -> str:
        """将命令加入优先级队列执行"""
        command_data = {
            'context': ctx.copy(),
            'priority': priority,
            'timestamp': time.time(),
            'command_id': f"{ctx['command']}_{int(time.time() * 1000)}"
        }
        
        # 将命令加入优先级队列
        success = self.command_queue.put(command_data, priority=priority)
        if not success:
            return f"命令 {ctx['command']} 加入队列失败（队列满或资源不足）"
        
        # 启动命令处理（如果未运行）
        if not self.command_processing:
            await self._start_command_processing()
        
        return f"命令 {ctx['command']} 已加入执行队列（优先级: {priority}）"
    
    async def _start_command_processing(self) -> None:
        """启动命令处理"""
        if not self.command_processing:
            self.command_processing = True
            self.command_processor_task = asyncio.create_task(self._process_commands())
    
    async def _process_commands(self) -> None:
        """处理命令队列"""
        while self.command_processing:
            # 检查资源限制
            with self.command_lock:
                if len(self.active_commands) >= self.command_resource_controller.max_size:
                    await asyncio.sleep(0.1)
                    continue
            
            # 从队列获取命令
            command_data = self.command_queue.get(timeout=0.1)
            if not command_data:
                # 队列为空，检查是否继续处理
                if self.command_queue.empty():
                    await asyncio.sleep(0.5)
                continue
            
            # 创建命令执行任务
            command_coro = self._execute_command_async(command_data)
            command_future = asyncio.create_task(command_coro)
            
            with self.command_lock:
                self.active_commands.add(command_future)
            
            # 设置完成回调
            command_future.add_done_callback(
                lambda f: self._on_command_complete(f)
            )
    
    async def _execute_command_async(self, command_data: Dict[str, Any]) -> str:
        """异步执行命令"""
        try:
            ctx = command_data['context']
            
            # 重新检查冷却状态（可能在队列中等待了一段时间）
            await self._check_cooldown_flag(ctx)
            if not ctx.get("cooldown_passed"):
                return f"命令 {ctx['command']} 冷却中，请等待"
            
            # 执行命令
            await self._execute(ctx)
            result = await self.tree.evaluate(ctx)
            
            print(f"命令执行成功: {ctx['command']} (优先级: {command_data['priority']})")
            return result
            
        except Exception as e:
            print(f"命令执行出错: {command_data['context']['command']}: {e}")
            return f"命令执行出错: {e}"
    
    def _on_command_complete(self, future: asyncio.Future) -> None:
        """命令执行完成回调"""
        with self.command_lock:
            self.active_commands.discard(future)
    
    def stop_command_processing(self) -> None:
        """停止命令处理"""
        self.command_processing = False
        if self.command_processor_task:
            self.command_processor_task.cancel()
    
    def register_command(self, command_name: str, handler_cls: type) -> bool:
        """注册命令处理器
        
        Args:
            command_name: 命令名称
            handler_cls: 处理器类（必须定义fun_name属性）
            
        Returns:
            bool: 是否注册成功
        """
        try:
            # 检查处理器类是否已经注册
            registry = ClassNucleus.get_registry()
            if command_name in registry:
                return True
            
            # 检查处理器类是否有fun_name属性
            if not hasattr(handler_cls, 'fun_name'):
                # 动态添加fun_name属性
                handler_cls.fun_name = command_name
            
            return True
        except Exception as e:
            print(f"命令注册失败: {e}")
            return False
    
    def get_command_queue_stats(self) -> Dict[str, Any]:
        """获取命令队列统计"""
        queue_stats = self.command_queue.get_stats()
        resource_stats = self.command_resource_controller.get_resource_usage()
        
        return {
            'queue_stats': queue_stats,
            'resource_stats': resource_stats,
            'active_commands': len(self.active_commands),
            'processing': self.command_processing
        }

# 定时事件调度器
class TimeTaskScheduler:
    """定时任务调度器：处理time_on装饰器注册的任务，使用优先级队列管理"""

    def __init__(self):
        self.registry = ClassNucleus.get_registry()
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.time_tasks: List[Dict[str, Any]] = []  # 存储任务详情
        self.check_interval = 1  # 检查周期（秒）
        
        # 使用优先级队列管理任务执行
        self.task_queue = PriorityQueue(
            max_size=100,
            max_memory_mb=50
        )
        self.resource_controller = ResourceController(
            max_size=10,  # 最大并发任务数
            max_memory_mb=100  # 最大内存使用
        )
        self.active_tasks = set()
        self.task_lock = threading.Lock()

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
                        'last_executed': 0  # 设置为0，确保第一次会立即执行
                    })

        # 按优先级排序（数字越小优先级越高）
        self.time_tasks.sort(key=lambda x: x['priority'])
        print(f"已加载 {len(self.time_tasks)} 个定时任务")

    async def execute_due_tasks(self) -> None:
        """执行所有到期的定时任务，使用优先级队列管理"""
        current_time = time.time()

        # 将所有到期的任务加入优先级队列
        for task in self.time_tasks:
            elapsed = current_time - task['last_executed']
            if elapsed >= task['interval']:
                task_data = {
                    'task': task,
                    'scheduled_time': current_time,
                    'task_id': f"{task['handler'].__name__}_{int(current_time * 1000)}"
                }
                success = self.task_queue.put(task_data, priority=task['priority'])
                if success:
                    task['last_executed'] = current_time  # 更新任务的上次执行时间
                else:
                    print(f"警告: 任务加入队列失败 - {task['handler'].__name__}")
        
        # 处理队列中的任务
        await self._process_queued_tasks()

    async def _process_queued_tasks(self) -> None:
        """处理优先级队列中的任务，考虑资源限制"""
        while not self.task_queue.empty():
            # 检查资源限制
            with self.task_lock:
                if len(self.active_tasks) >= self.resource_controller.max_size:
                    print(f"资源限制: 当前活跃任务数 {len(self.active_tasks)} 已达到最大值")
                    break
            
            # 从队列获取任务
            task_data = self.task_queue.get(timeout=0.1)
            if not task_data:
                break
            
            # 检查内存限制
            estimated_memory = 1  # 假设每个任务使用1MB内存
            if (self.resource_controller.current_memory_mb + estimated_memory > 
                self.resource_controller.max_memory_mb):
                print(f"内存限制: 当前内存使用 {self.resource_controller.current_memory_mb}MB 已达到最大值")
                # 将任务重新放回队列
                self.task_queue.put(task_data, priority=task_data['task']['priority'])
                break
            
            # 分配资源并执行任务
            self.resource_controller.current_memory_mb += estimated_memory
            
            # 创建异步任务
            task_coro = self._run_task_async(task_data)
            task_future = asyncio.create_task(task_coro)
            
            with self.task_lock:
                self.active_tasks.add(task_future)
            
            # 设置完成回调
            task_future.add_done_callback(
                lambda f: self._on_task_complete(f, estimated_memory)
            )
    
    async def _run_task_async(self, task_data: Dict[str, Any]) -> None:
        """异步运行任务"""
        task = task_data['task']
        try:
            handler = task['handler']
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                # 对于同步函数，在线程池中运行
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, handler)
            print(f"任务执行成功: {handler.__name__} (优先级: {task['priority']})")
        except Exception as e:
            print(f"定时任务执行出错: {handler.__name__}: {e}")
    
    def _on_task_complete(self, future: asyncio.Future, memory_used: float) -> None:
        """任务完成回调"""
        with self.task_lock:
            self.active_tasks.discard(future)
        self.resource_controller.current_memory_mb -= memory_used
    
    async def _run_task(self, task: Dict[str, Any]) -> None:
        """兼容旧接口的任务运行方法"""
        task_data = {
            'task': task,
            'scheduled_time': time.time(),
            'task_id': f"{task['handler'].__name__}_{int(time.time() * 1000)}"
        }
        await self._run_task_async(task_data)

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
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        queue_stats = self.task_queue.get_stats()
        resource_stats = self.resource_controller.get_resource_usage()
        
        return {
            'queue_stats': queue_stats,
            'resource_stats': resource_stats,
            'active_tasks': len(self.active_tasks),
            'running': self.running,
            'total_tasks': len(self.time_tasks)
        }
    
    def update_resource_limits(self, max_size: int = None, max_memory_mb: float = None) -> None:
        """动态更新资源限制"""
        if max_size is not None:
            self.resource_controller.max_size = max_size
        if max_memory_mb is not None:
            self.resource_controller.max_memory_mb = max_memory_mb
        print(f"资源限制已更新: 最大任务数={self.resource_controller.max_size}, 最大内存={self.resource_controller.max_memory_mb}MB")
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """获取队列中的待处理任务"""
        pending_tasks = []
        for item_data, priority in self.task_queue.get_all_items():
            try:
                # 尝试从任务数据中获取处理器名称
                if 'task' in item_data and 'handler' in item_data['task']:
                    handler = item_data['task']['handler']
                    task_name = getattr(handler, '__name__', str(handler))
                elif 'task_id' in item_data:
                    task_name = item_data['task_id']
                else:
                    task_name = "未知任务"
                
                task_info = {
                    'task_name': task_name,
                    'priority': priority,
                    'scheduled_time': item_data.get('scheduled_time', time.time()),
                    'task_id': item_data.get('task_id', 'unknown')
                }
                pending_tasks.append(task_info)
            except Exception as e:
                print(f"获取待处理任务信息时出错: {e}")
                continue
        return pending_tasks

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
                        
                        # 获取匹配对象
                        if isinstance(pattern, str):
                            match_obj = re.search(pattern, content)
                        else:
                            match_obj = pattern.search(content) if hasattr(pattern, 'search') else None
                        
                        # 调用处理函数时传递文本和匹配对象，handler已经支持依赖注入和调用链
                        result = await handler(content, match_obj)
                            
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
                    
                    # 获取匹配对象
                    if isinstance(pattern, str):
                        match_obj = re.search(pattern, content)
                    else:
                        match_obj = pattern.search(content) if hasattr(pattern, 'search') else None
                    
                    # 调用处理函数时传递文本和匹配对象，handler已经支持依赖注入和调用链
                    result = await handler(content, match_obj)
                    
                    results.append(str(result) if result is not None else f"任务 {task_name} 执行完成")
                    print(f"正则任务匹配成功: {task_name}")
                except Exception as e:
                    error_msg = f"任务 {handler_info['name']} 执行失败: {e}"
                    print(error_msg)
                    results.append(error_msg)
        
        return results