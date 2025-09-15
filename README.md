# 装饰器框架

一个轻量级、易用的Python装饰器框架，支持事件触发、命令处理、定时任务和正则表达式匹配。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基本使用
框架提供四种核心装饰器：
- `@on()` - 普通事件注册
- `@command_on()` - 命令注册（支持决策树）
- `@time_on()` - 定时任务
- `@re_on()` - 正则表达式任务

### 3. 项目结构
```
decorator_framework/
├── decorators/
│   └── on.py          # 四种装饰器实现
├── nucleus/
│   ├── __init__.py
│   └── dispatcher.py   # 四种调度器
├── test_timer_demo.py  # 定时任务示例
├── test_re_decision_demo.py  # 正则+决策树示例
├── cs.py              # 综合示例
└── README.md
```

## 📋 完整示例

### 1. 事件和命令示例
```python
import asyncio
from decorators.on import on, command_on
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher

# 普通事件
@on("greet").execute()
def say_hello(name):
    return f"Hello, {name}!"

# 命令处理
@command_on("add", "/add").execute()
def add_command(a, b):
    return f"{a} + {b} = {a + b}"

async def main():
    # 事件触发
    dispatcher = EventDispatcher()
    result = await dispatcher.trigger_event("greet", "World")
    print(result)  # 输出: Hello, World!
    
    # 命令处理
    cmd_dispatcher = DecisionCommandDispatcher()
    result = await cmd_dispatcher.handle("/add 10 20")
    print(result)  # 输出: 10 + 20 = 30

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 定时任务示例
```python
import asyncio
from decorators.on import time_on
from nucleus.dispatcher import TimeTaskScheduler

# 定义定时任务
@time_on("heartbeat", priority=1, interval=3).execute()
async def heartbeat_task():
    print("💓 心跳检测：系统运行正常")

@time_on("cleanup", priority=2, interval=5).execute()
async def cleanup_logs():
    print("🧹 清理日志文件...")

async def main():
    scheduler = TimeTaskScheduler()
    await scheduler.start()
    
    print("定时任务已启动，运行20秒...")
    await asyncio.sleep(20)
    
    await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔧 高级用法

### 正则表达式任务 (@re_on)
通过正则表达式匹配文本内容来触发任务：

```python
from decorators.on import re_on
from nucleus.dispatcher import ReTaskScheduler

# 1. 定义正则任务
@re_on("greeting", "问候语", r"你好|您好|hi|hello").execute()
def handle_greeting():
    return "你好！有什么可以帮助您的吗？"

@re_on("weather_query", "天气查询", r"天气|weather|温度").execute()
def handle_weather():
    return "今天天气晴朗，温度25°C"

# 2. 使用调度器
async def test_regex():
    scheduler = ReTaskScheduler()
    
    # 匹配所有相关任务
    results = await scheduler.match_content("你好，今天天气如何？")
    print(results)  # 输出: ['你好！有什么可以帮助您的吗？', '今天天气晴朗，温度25°C']
```

### 决策树命令系统 (@command_on)
基于决策树的智能命令解析系统：

```python
from decorators.on import command_on
from nucleus.dispatcher import DecisionCommandDispatcher

# 1. 定义命令
@command_on("help_cmd", "/help").execute()
def smart_help(args=None):
    return """🤖 智能助手命令列表：
/help - 显示帮助信息
/weather [城市] - 查询天气"""

@command_on("weather_cmd", "/weather").execute()
def weather_command(args=None):
    city = args[0] if args else "北京"
    return f"🌤️ {city}天气：今天天气晴朗，温度25°C"

# 2. 使用命令调度器
async def test_commands():
    dispatcher = DecisionCommandDispatcher()
    
    print(await dispatcher.handle("/help"))
    print(await dispatcher.handle("/weather 上海"))
```

### 命令参数解析
支持复杂的参数解析：

```python
@command_on("add", "/add", 
           arg_parser=lambda s: {"a": int(s.split()[0]), "b": int(s.split()[1])}
).execute()
def add_numbers(a: int, b: int):
    return f"{a} + {b} = {a + b}"

# 使用示例
# /add 10 20  -> 返回 "10 + 20 = 30"
```

### 异步支持
框架完全支持异步函数，所有装饰器都可以用于异步函数：

```python
@on("async_event").execute()
async def async_handler(data):
    await asyncio.sleep(1)
    return f"异步处理完成：{data}"

@time_on("async_task", priority=1, interval=5).execute()
async def async_timed_task():
    await asyncio.sleep(0.5)
    print("异步定时任务执行完成")
```

## 📊 参数说明

### @time_on 装饰器参数
- `name`: 任务名称（必须唯一）
- `priority`: 优先级，数字越小优先级越高（默认：1）
- `interval`: 执行间隔时间（单位：秒）

### @command_on 装饰器参数
- `name`: 命令名称
- `command`: 命令字符串（必须以"/"开头）
- `aliases`: 命令别名列表（可选）
- `cooldown`: 冷却时间（秒，可选）
- `arg_parser`: 参数解析函数（可选）

### @re_on 装饰器参数
- `name`: 任务名称
- `content`: 任务描述
- `pattern`: 正则表达式模式
- `priority`: 优先级（默认：1）

## 🧪 测试

### 运行所有测试
```bash
# 运行定时任务演示
python test_timer_demo.py

# 运行正则和决策树演示
python test_re_decision_demo.py

# 运行综合示例
python cs.py
```

### 手动测试
```python
import asyncio
from nucleus.dispatcher import *

async def test_all():
    # 测试事件系统
    ed = EventDispatcher()
    print(await ed.trigger_event("greet", "Python"))
    
    # 测试命令系统
    cd = DecisionCommandDispatcher()
    print(await cd.handle("/help"))
    
    # 测试正则系统
    rd = ReTaskScheduler()
    print(await rd.match_content("你好世界"))

asyncio.run(test_all())
```

## 📝 调试技巧

1. **查看注册的任务**：启动调度器时会显示已加载的任务列表
2. **任务执行日志**：每个任务执行时会输出执行信息
3. **错误处理**：框架会捕获并显示任务执行中的异常
4. **优先级调试**：通过设置不同的priority值观察任务执行顺序

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License