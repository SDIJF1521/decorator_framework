---
**版本**: 2.1.0  
**最后更新**: 2025-01-15  
**文档状态**: ✅ API文档已修正 - 基于实际代码框架
**⚠️ 重要**: 所有装饰器都必须使用 `.execute()` 方法！
---

# 装饰器框架 API 参考

## 🌐 文档语言
- [English Version](API_REFERENCE_EN.md) - 英文API文档
- [中文版本](API_REFERENCE.md) - 当前文档（中文API）

## 📋 装饰器 API

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

**示例:**
```python
@on("user_login").execute()  # 注意：必须调用 .execute()
async def handle_login(username):
    return f"欢迎 {username}"

# 触发事件
await dispatcher.trigger_event("user_login", "alice")
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

**示例:**
```python
@time_on("backup_task", priority=1, interval=3600).execute()  # 注意：必须调用 .execute()
async def hourly_backup():
    return "数据库备份完成"
```

### @command_on 命令装饰器

处理命令行或API调用。

```python
from decorators.on import command_on

@command_on(name: str, command: str, aliases: list = None, cooldown: int = 0).execute()  # 注意：必须调用 .execute()
async def command_handler(args: str = "") -> str:
    """命令处理器"""
    return "命令执行结果"
```

**参数说明:**
- `name`: 命令处理器名称
- `command`: 命令匹配模式（必须以 "/" 开头，如 "/start"）
- `aliases`: 命令别名列表（可选）
- `cooldown`: 冷却时间（秒，可选）

**示例:**
```python
@command_on("greet", "/hello").execute()  # 注意：必须调用 .execute()
async def greet_command(args=""):
    name = args.strip() if args.strip() else "World"
    return f"Hello, {name}!"

# 执行命令
result = await dispatcher.handle("/hello Alice")
```

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

管理事件的注册和触发。

```python
from nucleus.dispatcher import EventDispatcher

dispatcher = EventDispatcher()

# 触发事件
await dispatcher.trigger_event(event_name: str, *args, **kwargs) -> Any

# 获取注册的事件
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

**方法说明:**
- `trigger_event()`: 触发事件并执行注册的处理器
- `ClassNucleus.get_registry()`: 返回所有注册的类

### DecisionCommandDispatcher 命令调度器

处理命令的解析和执行。

```python
from nucleus.dispatcher import DecisionCommandDispatcher

dispatcher = DecisionCommandDispatcher()

# 处理命令
await dispatcher.handle(message: str) -> str

# 获取注册的命令
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

### TimeTaskScheduler 定时任务调度器

管理定时任务的执行。

```python
from nucleus.dispatcher import TimeTaskScheduler

scheduler = TimeTaskScheduler()

# 启动调度器
await scheduler.start()

# 停止调度器
await scheduler.stop()

# 获取任务列表
scheduler.time_tasks -> list
```

## 📊 日志配置

### 基础配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

## 🧪 测试示例

### 单元测试

```python
import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decorators.on import on
from nucleus.dispatcher import EventDispatcher

@pytest.mark.asyncio
async def test_event_handler():
    dispatcher = EventDispatcher()
    
    @on("test_event").execute()
    async def test_handler(value):
        return f"处理: {value}"
    
    result = await dispatcher.trigger_event("test_event", "test")
    assert "处理: test" == result
```

### 集成测试

```python
import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler

@pytest.mark.asyncio
async def test_full_workflow():
    # 初始化各个调度器
    event_dispatcher = EventDispatcher()
    command_dispatcher = DecisionCommandDispatcher()
    task_scheduler = TimeTaskScheduler()
    
    # 测试事件系统
    @on("test_event").execute()
    async def test_handler(data):
        return f"测试: {data}"
    
    result = await event_dispatcher.trigger_event("test_event", "data")
    assert "测试: data" == result
    
    # 测试定时任务调度器初始化
    task_scheduler.load_time_tasks()
    assert isinstance(task_scheduler.time_tasks, list)
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