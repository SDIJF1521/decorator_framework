---
**版本**: 2.4.0  
**最后更新**: 2025-01-16  
**文档状态**: ✅ API文档已更新 - 新增依赖注入、调用链、任务管理等核心功能文档
**测试状态**: ✅ 44个测试用例全部通过 - 框架功能验证完成
---
# 装饰器框架 API 参考

## 文档语言

- [English Version](API_REFERENCE_EN.md) - 英文API文档
- [中文版本](API_REFERENCE.md) - 当前文档（中文API）

## 框架概览

装饰器框架是一个功能强大的异步事件驱动框架，提供以下核心功能：

- **装饰器系统**: 基于装饰器的事件处理机制
- **依赖注入**: 支持构造函数注入和服务生命周期管理
- **调用链**: 支持任务执行的拦截和增强
- **任务管理**: 支持任务取消、状态跟踪和生命周期管理
- **优先级队列**: 支持事件和命令的优先级处理
- **资源控制**: 支持内存和并发数限制

## 快速开始

```python
from nucleus.core import enable_framework_integration
from decorators.on import command_on

# 启用框架集成
enable_framework_integration()

# 使用装饰器注册命令处理器
@command_on("hello", "/hello").execute()
async def hello_command(args: dict = None):
    return "Hello, World!"

# 命令调用
from nucleus.dispatcher import DecisionCommandDispatcher
dispatcher = DecisionCommandDispatcher()
result = await dispatcher.handle("/hello")
print(result)  # 输出: Hello, World!
```

## 装饰器 API

### @on 事件装饰器

处理事件驱动的异步任务。

```python
from decorators.on import on

@on(name: str).execute()  # 注意：必须调用 .execute()
async def handler_function(*args, **kwargs) -> str:
    """事件处理器"""
    return "处理结果"
```

**参数说明:**

- `name`: 事件名称，用于触发和监听

**特性:**
- 支持同步和异步函数
- 支持依赖注入（当框架集成启用时）
- 支持调用链拦截和增强
- 支持任务管理集成

**示例:**

```python
@on("user_login").execute()  # 注意：必须调用 .execute()
async def handle_login(username):
    return f"欢迎 {username}"

# 触发事件
await dispatcher.trigger_event("user_login", "alice")
```

**高级用法（依赖注入）:**

```python
from nucleus.core import service, inject

# 定义服务
@service('singleton')
class UserService:
    async def get_user_info(self, user_id: str):
        return {"id": user_id, "name": f"用户{user_id}"}

# 使用依赖注入
@on("user_login").execute()
@inject  # 依赖注入装饰器
async def handle_login(user_service: UserService, user_id: str):
    user_info = await user_service.get_user_info(user_id)
    return f"欢迎 {user_info['name']}"
```

### @time_on 定时任务装饰器

创建周期性执行的定时任务。

```python
from decorators.on import time_on

@time_on(name: str, priority: int = 1, interval: int = 0).execute()  # 注意：必须调用 .execute()
async def scheduled_task() -> str:
    """定时任务"""
    return "任务执行结果"
```

**参数说明:**

- `name`: 任务唯一标识符
- `priority`: 任务优先级 (1-10，数字越小优先级越高)
- `interval`: 执行间隔时间（秒）

**特性:**
- 支持同步和异步函数
- 支持依赖注入（当框架集成启用时）
- 支持调用链拦截和增强
- 支持任务管理集成

**示例:**

```python
@time_on("backup_task", priority=1, interval=3600).execute()  # 注意：必须调用 .execute()
async def hourly_backup():
    return "数据库备份完成"
```

**高级用法（带依赖注入）:**

```python
from nucleus.core import service, inject

@service('singleton')
class BackupService:
    async def perform_backup(self):
        # 执行备份逻辑
        return "数据库备份完成"

@time_on("backup_task", priority=1, interval=3600).execute()
@inject
async def hourly_backup(backup_service: BackupService):
    return await backup_service.perform_backup()
```

### @command_on 命令装饰器

处理命令行或API调用。

```python
from decorators.on import command_on

@command_on(name: str, command: str, aliases: list = None, cooldown: int = 0).execute()  # 注意：必须调用 .execute()
async def command_handler(args: dict = None) -> str:
    """命令处理器 - args 参数为字典类型，包含解析后的命令参数"""
    return "命令执行结果"
```

**参数说明:**

- `name`: 命令处理器名称
- `command`: 命令匹配模式（必须以 "/" 开头，如 "/start"）
- `aliases`: 命令别名列表（可选）
- `cooldown`: 冷却时间（秒，可选）

**重要提示:** `args` 参数类型为 `dict`，不是 `str`。框架会自动解析命令参数为字典格式。

**参数解析说明:**
框架支持两种参数传递方式：
1. **字典参数**: 直接传入字典对象 `{'key': 'value'}`
2. **字符串解析**: 支持 `key=value` 格式的参数字符串，如 `name=Alice age=25`

参数字符串会自动解析为字典，例如：
- `"name=Alice"` → `{'name': 'Alice'}`
- `"name=Alice age=25"` → `{'name': 'Alice', 'age': '25'}`
- `""` → `{}` (空字典)

**示例:**

```python
@command_on("greet", "/hello").execute()  # 注意：必须调用 .execute()
async def greet_command(args: dict = None):
    if args is None:
        args = {}
    name = args.get('name', 'World')
    return f"Hello, {name}!"

# 或者使用简化的字典访问
@command_on("simple_greet", "/hi").execute()
async def simple_greet_command(args: dict = None):
    name = (args or {}).get('name', 'World')
    return f"Hi, {name}!"
```

# 执行命令（传入参数字典）
`result = await dispatcher.handle("/hello", args={'name': 'Alice'})`

# 或者使用命令字符串解析（如果启用了参数解析）
`result = await dispatcher.handle("/hello name=Alice")`

### @re_on 正则表达式装饰器

基于正则表达式匹配处理文本内容。

```python
import re
from decorators.on import re_on

@re_on(name: str, content: str, pattern: re.Pattern, priority: int = 1).execute()  # 注意：必须调用 .execute()
async def regex_handler(content: str, match: re.Match) -> str:
    """正则表达式处理器"""
    return f"匹配结果: {match.group(1)}"
```

**参数说明:**

- `name`: 模式名称
- `content`: 要匹配的文本内容参数名
- `pattern`: 正则表达式模式对象（使用 `re.compile()` 创建）
- `priority`: 优先级（可选，默认为1）

**示例:**

```python
import re
from decorators.on import re_on

@re_on("error_pattern", "content", re.compile(r"ERROR:(\w+)")).execute()  # 注意：必须调用 .execute()
async def handle_error(content, match):
    error_type = match.group(1)
    return f"检测到错误: {error_type}"

# 触发匹配
await dispatcher.trigger_event("error_detector", "ERROR:database_timeout")
```

## 🔧 调度器 API

### EventDispatcher 事件调度器

管理事件的注册和触发，支持优先级队列。

```python
from nucleus.dispatcher import EventDispatcher

dispatcher = EventDispatcher()

# 触发事件（支持优先级）
await dispatcher.trigger_event(event_name: str, priority: int = 5, data: dict = None) -> Any

# 注册事件处理器
dispatcher.register_event(event_name: str, handler_class)

# 获取事件队列统计
stats = dispatcher.get_event_queue_stats()

# 获取注册的事件
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

**方法说明:**

- `trigger_event()`: 触发事件并执行注册的处理器
- `register_event()`: 注册事件处理器
- `get_event_queue_stats()`: 获取事件队列统计信息
- `ClassNucleus.get_registry()`: 返回所有注册的类

### DecisionCommandDispatcher 命令调度器

处理命令的解析和执行，支持优先级队列和决策树。

```python
from nucleus.dispatcher import DecisionCommandDispatcher
from nucleus.data.tree import Tree

dispatcher = DecisionCommandDispatcher()

# 设置决策树
dispatcher.tree = Tree()

# 注册命令处理器
dispatcher.register_command(command_name: str, handler_class)

# 处理命令（支持优先级）
await dispatcher.handle(message: str, priority: int = 5) -> str

# 获取命令队列统计
stats = dispatcher.get_command_queue_stats()

# 获取注册的命令
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

### TimeTaskScheduler 定时任务调度器

管理定时任务的执行，支持优先级队列和资源控制。

```python
from nucleus.dispatcher import TimeTaskScheduler

scheduler = TimeTaskScheduler()

# 启动调度器
await scheduler.start()

# 停止调度器
await scheduler.stop()

# 获取任务队列统计
stats = scheduler.get_queue_stats()

# 获取任务列表
scheduler.time_tasks -> list

# 访问内部优先级队列
scheduler.task_queue -> PriorityQueue
```

## 📊 优先级队列 API

### PriorityQueue 优先级队列

线程安全的优先级队列实现，支持任务优先级管理和资源限制。

```python
from nucleus.data.priority_queue import PriorityQueue, ResourceController

# 创建优先级队列
queue = PriorityQueue(maxsize=100, resource_limit=50)

# 添加任务（优先级：1最高，10最低）
success = queue.put(item, priority=5)

# 获取任务
item = queue.get()

# 获取队列统计
stats = queue.get_stats()
```

**参数说明:**

- `maxsize`: 队列最大容量（可选）
- `resource_limit`: 资源限制数量（可选）

**方法说明:**

- `put(item, priority=5)`: 添加任务到队列
- `get()`: 获取优先级最高的任务
- `get_stats()`: 返回队列统计信息
- `qsize()`: 返回队列大小

### ResourceController 资源控制器

管理队列资源使用，防止资源耗尽。

```python
from nucleus.data.priority_queue import ResourceController

# 创建资源控制器
controller = ResourceController(limit=100)

# 申请资源
if controller.acquire_resource():
    try:
        # 执行任务
        pass
    finally:
        # 释放资源
        controller.release_resource()
```

## 📊 日志配置

### 基础配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

# 获取模块日志器

logger = logging.getLogger(__name__)

```

### 生产级配置

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## 🎯 最佳实践

### 1. 错误处理

```python
import asyncio

@on("user_action").execute()
async def safe_handler(user_data):
    try:
        # 业务逻辑
        result = await process_user_action(user_data)
        return f"成功: {result}"
    except Exception as e:
        logger.error(f"处理用户动作失败: {e}")
        return f"错误: {str(e)}"
```

### 2. 超时控制

```python
import asyncio

@time_on("api_call", priority=1, interval=30).execute()
async def api_with_timeout():
    try:
        # 设置5秒超时
        result = await asyncio.wait_for(
            external_api_call(), 
            timeout=5.0
        )
        return f"API调用成功: {result}"
    except asyncio.TimeoutError:
        return "API调用超时"
```

### 3. 资源管理

```python
import aiohttp
from contextlib import asynccontextmanager

class HttpClient:
    def __init__(self):
        self.session = None
  
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
  
    async def close(self):
        if self.session:
            await self.session.close()

client = HttpClient()

@on("http_request").execute()
async def make_request(request_data):
    session = await client.get_session()
    async with session.get(request_data['url']) as response:
        return await response.text()
```

## 🧪 测试验证

### 测试环境验证

```bash
# 运行框架测试（44个测试用例）
python -m pytest tests/ -v
# 预期输出: 44 passed, 0 failed

# 运行特定模块测试
python -m pytest tests/test_basic.py -v        # 基础功能测试
python -m pytest tests/test_core_integration.py -v  # 核心集成测试
python -m pytest tests/test_priority_queue.py -v    # 优先级队列测试

# 验证API文档示例
python examples/quick_start_example.py
python examples/core_integration_demo.py
```

### 框架状态验证

```python
import asyncio
from nucleus.core.integration import enable_framework_integration
from nucleus.core.di import get_dependency_container
from nucleus.core.task import get_task_manager
from nucleus.core.priority_queue import PriorityQueue

async def validate_framework():
    """验证框架核心功能"""
    try:
        # 启用框架集成
        integration = enable_framework_integration()
        print("✅ 框架集成启用成功")
      
        # 验证依赖注入
        container = get_dependency_container()
        print(f"✅ 依赖注入容器就绪 (服务数: {len(container.services)})")
      
        # 验证任务管理
        task_manager = get_task_manager()
        print("✅ 任务管理器就绪")
      
        # 验证优先级队列
        queue = PriorityQueue(maxsize=100)
        print("✅ 优先级队列就绪")
      
        print("\n🎉 框架验证通过！所有核心组件正常工作。")
        return True
      
    except Exception as e:
        print(f"❌ 框架验证失败: {e}")
        return False

# 运行验证
asyncio.run(validate_framework())
```

## 📋 调试技巧

### 1. 查看注册信息

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.Myclass import ClassNucleus

# 查看所有注册的类
registry = ClassNucleus.get_registry()
print("注册的所有类:", registry)

# 查看特定类型的处理器
for name, cls in registry.items():
    if hasattr(cls, 'fun_name'):
        print(f"处理器: {name} -> {cls.fun_name}")
```

### 2. 手动触发

```python
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher

async def debug():
    dispatcher = EventDispatcher()
  
    # 手动触发事件
    result = await dispatcher.trigger_event("user_login", "debug_user")
    print("事件结果:", result)
  
    # 手动执行命令
    cmd_dispatcher = DecisionCommandDispatcher()
    result = await cmd_dispatcher.handle("/hello debug")
    print("命令结果:", result)

asyncio.run(debug())
```

## 📚 完整示例

### 生产级应用结构

```
my_app/
├── app.py              # 主应用
├── handlers/           # 事件处理器
│   ├── user_handlers.py
│   └── system_handlers.py
├── commands/           # 命令处理器
│   ├── admin_commands.py
│   └── user_commands.py
├── tasks/             # 定时任务
│   ├── maintenance.py
│   └── monitoring.py
├── config.py          # 配置
└── requirements.txt   # 依赖
```

### 主应用示例

```python
# app.py
import asyncio
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler
from decorators.on import on, time_on, command_on

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # 初始化各个调度器
    event_dispatcher = EventDispatcher()
    command_dispatcher = DecisionCommandDispatcher()
    task_scheduler = TimeTaskScheduler()
  
    try:
        # 启动定时任务调度器
        await task_scheduler.start()
      
        # 运行主循环
        logger.info("框架已启动，按 Ctrl+C 停止")
        while True:
            await asyncio.sleep(1)
          
    except KeyboardInterrupt:
        logger.info("收到停止信号")
    finally:
        await task_scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
```