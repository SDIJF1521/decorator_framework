# 🎭 装饰器框架 - Python企业级开发框架

一个功能强大的Python装饰器框架，提供**依赖注入**、**调用链拦截**、**任务管理**和**优先级队列**等高级功能。支持事件触发、命令处理、定时任务和正则表达式匹配。

## 📋 目录

- [🎭 装饰器框架 - Python企业级开发框架](#-装饰器框架---python企业级开发框架)
  - [📋 目录](#-目录)
  - [✅ 框架状态](#-框架状态)
  - [🎯 核心特性](#-核心特性)
  - [🌐 文档语言](#-文档语言)
  - [🚀 快速开始](#-快速开始)
    - [0. 环境准备](#0-环境准备)
    - [1. 安装框架](#1-安装框架)
    - [2. 基础概念](#2-基础概念)
      - [框架集成启用](#框架集成启用)
      - [服务装饰器用法](#服务装饰器用法)
      - [事件装饰器用法](#事件装饰器用法)
    - [3. 基础示例](#3-基础示例)
    - [4. 高级参数解析示例](#4-高级参数解析示例)
    - [6. 调用链系统](#6-调用链系统)
      - [自动调用链集成](#自动调用链集成)
      - [自定义拦截器](#自定义拦截器)
    - [📊 任务管理系统](#-任务管理系统)
      - [基本任务管理](#基本任务管理)
      - [任务统计和监控](#任务统计和监控)
    - [8. 事件装饰器系统](#8-事件装饰器系统)
      - [普通事件处理 (@on)](#普通事件处理-on)
      - [命令处理 (@command\_on)](#命令处理-command_on)
      - [定时任务 (@time\_on)](#定时任务-time_on)
      - [正则表达式匹配 (@re\_on)](#正则表达式匹配-re_on)
    - [9. 优先级队列系统](#9-优先级队列系统)
      - [基本使用](#基本使用)
      - [资源控制](#资源控制)
  - [10. 架构设计](#10-架构设计)
    - [核心组件](#核心组件)
    - [设计原则](#设计原则)
  - [11. 最佳实践](#11-最佳实践)
    - [1. 服务设计](#1-服务设计)
    - [2. 错误处理](#2-错误处理)
    - [3. 性能优化](#3-性能优化)
  - [12. 高级用法](#12-高级用法)
    - [1. 自定义参数解析器](#1-自定义参数解析器)
      - [智能参数解析器实现](#智能参数解析器实现)
    - [2. 多事件监听器模式](#2-多事件监听器模式)
    - [3. 条件事件处理](#3-条件事件处理)
    - [4. 动态服务注册](#4-动态服务注册)
    - [5. 任务流水线](#5-任务流水线)
    - [6. 事件驱动架构](#6-事件驱动架构)
  - [13. 框架核心功能详解](#13-框架核心功能详解)
    - [参数解析系统](#参数解析系统)
      - [基础参数解析](#基础参数解析)
      - [高级参数解析](#高级参数解析)
      - [智能参数解析器](#智能参数解析器)
      - [参数解析器特性](#参数解析器特性)
  - [14. 参数参考](#14-参数参考)
    - [@service 装饰器参数](#service-装饰器参数)
    - [@on 装饰器参数](#on-装饰器参数)
    - [@command\_on 装饰器参数](#command_on-装饰器参数)
    - [@time\_on 装饰器参数](#time_on-装饰器参数)
    - [@re\_on 装饰器参数](#re_on-装饰器参数)
  - [15. 测试验证](#15-测试验证)
    - [运行所有测试](#运行所有测试)
    - [运行特定示例](#运行特定示例)
    - [性能测试](#性能测试)
  - [16. 故障排除](#16-故障排除)
    - [常见问题](#常见问题)
      - [1. ModuleNotFoundError: No module named 'nucleus'](#1-modulenotfounderror-no-module-named-nucleus)
      - [2. 装饰器不生效](#2-装饰器不生效)
      - [3. 依赖注入失败](#3-依赖注入失败)
    - [4. 命令参数类型错误](#4-命令参数类型错误)
    - [5. 自定义参数解析器错误](#5-自定义参数解析器错误)
    - [6. 事件不触发](#6-事件不触发)
    - [7. 参数解析器类型错误](#7-参数解析器类型错误)
    - [调试技巧](#调试技巧)
      - [1. 检查服务注册状态](#1-检查服务注册状态)
      - [2. 检查事件处理器](#2-检查事件处理器)
      - [3. 任务状态检查](#3-任务状态检查)
  - [17. 相关文档](#17-相关文档)
  - [18. 贡献指南](#18-贡献指南)
  - [19. 许可证](#19-许可证)
  - [20. 支持](#20-支持)
  - [18. 贡献指南](#18-贡献指南-1)
    - [🎯 贡献方式](#-贡献方式)
    - [📝 贡献步骤](#-贡献步骤)
    - [📋 代码规范](#-代码规范)
  - [21. 更新日志](#21-更新日志)
    - [v2.4.0 (当前版本)](#v240-当前版本)
    - [v2.3.0](#v230)
    - [v2.2.0](#v220)
    - [v2.1.0](#v210)
  - [19. 许可证](#19-许可证-1)
    - [📞 联系方式](#-联系方式)
    - [🙏 致谢](#-致谢)

## ✅ 框架状态

**测试状态**: ✅ 所有测试通过 (44/44) - 框架功能完整且稳定  
**文档状态**: ✅ 文档已更新 - 基于实际源码验证  
**依赖状态**: ✅ 零第三方依赖 - 仅使用Python标准库  
**兼容性**: ✅ Python 3.8+  

## 🎯 核心特性

- **🔧 零依赖**: 仅使用Python标准库，无第三方依赖
- **⚡ 高性能**: 异步支持，优先级队列，资源控制
- **🏗️ 企业级**: 依赖注入，服务生命周期管理，接口映射
- **🔗 调用链**: 拦截器模式，上下文传递，性能监控
- **📊 任务管理**: 定时任务，并发控制，任务统计
- **🎨 装饰器API**: 简洁优雅，类型安全，易于使用

## 🌐 文档语言
- [English Version](EN_README.md) - 英文文档
- [中文版本](README.md) - 当前文档（中文）

## 🚀 快速开始

### 0. 环境准备

确保Python版本 >= 3.7，安装框架依赖：

```bash
pip install asyncio
```

### 1. 安装框架

```bash
# 克隆项目
git clone https://github.com/your-repo/decorator_framework.git
cd decorator_framework

# 运行示例
python examples/basic_example.py
```

**验证安装:**
```bash
# 运行测试验证框架功能
python -m pytest tests/ -v
# 预期输出: 44 passed, 0 failed

# 运行快速开始示例
python examples/quick_start_example.py
```

### 2. 基础概念

#### 框架集成启用
在任何装饰器使用前，必须先启用框架集成：

```python
from nucleus.core.integration import enable_framework_integration

# 启用框架集成（必须先调用）
enable_framework_integration()
```

#### 服务装饰器用法
**重要**: `@service`装饰器**不需要**`.execute()`方法！

```python
from nucleus.core.integration import service

# ✅ 正确用法 - 直接装饰类
@service('singleton')  # 或 @service() 默认为单例
class MyService:
    def do_something(self):
        return "Hello World"

# ✅ 也支持接口映射
@service(IMyService)  # 注册接口到实现的映射
class MyServiceImpl(IMyService):
    def do_something(self):
        return "Hello World"
```

#### 事件装饰器用法
**重要**: `@on`、`@command_on`、`@time_on`、`@re_on`装饰器**必须**使用`.execute()`方法！

```python
from decorators import on, command_on

# ✅ 正确用法 - 必须使用.execute()
@on("user_login").execute()
async def handle_login(user_id: str):
    print(f"用户 {user_id} 登录了")

# ✅ 命令装饰器也需要.execute()
@command_on("bot", "/hello").execute()
async def handle_hello_command():
    return "Hello!"

# ❌ 错误用法 - 缺少.execute()
@on("user_login")  # 这样会注册失败
def handle_login():
    pass
```

### 3. 基础示例

下面是一个完整的入门示例，展示框架的正确用法：

```python
import asyncio
import sys
import os

# 添加项目根目录到Python路径（如果在项目外运行）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.core.integration import enable_framework_integration, service, inject
from decorators import on, command_on
from nucleus.dispatcher import EventDispatcher

# 1. 启用框架集成（必须先调用）
enable_framework_integration()

# 2. 定义服务接口和实现
class IDataService:
    async def get_user_name(self, user_id: str) -> str:
        raise NotImplementedError

@service(IDataService)  # 注册接口到实现的映射
class DataService(IDataService):
    def __init__(self):
        self.users = {"1": "张三", "2": "李四"}
    
    async def get_user_name(self, user_id: str) -> str:
        return self.users.get(user_id, "未知用户")

# 3. 定义业务服务（自动依赖注入）
@service('singleton')
class UserService:
    def __init__(self, data_service: IDataService):
        self.data_service = data_service
    
    async def greet_user(self, user_id: str) -> str:
        user_name = await self.data_service.get_user_name(user_id)
        return f"你好，{user_name}！"

# 4. 事件处理（使用依赖注入）
@on("user_login").execute()
async def handle_user_login(user_service: UserService, user_id: str, ip: str):
    greeting = await user_service.greet_user(user_id)
    print(f"🎉 {greeting} (来自IP: {ip})")

# 5. 命令处理
@command_on("bot", "/greet").execute()
async def handle_greet_command(user_service: UserService, user_id: str = "1"):
    greeting = await user_service.greet_user(user_id)
    return greeting

# 6. 主演示函数
async def main():
    print("🚀 装饰器框架演示开始...")
    
    # 获取服务实例
    user_service = UserService(DataService())
    
    # 测试业务逻辑
    greeting = await user_service.greet_user("1")
    print(f"业务测试: {greeting}")
    
    # 测试事件系统
    dispatcher = EventDispatcher()
    await dispatcher.trigger_event("user_login", user_id="1", ip="192.168.1.1")
    
    # 测试命令系统
    from nucleus.dispatcher import DecisionCommandDispatcher
    cmd_dispatcher = DecisionCommandDispatcher()
    result = await cmd_dispatcher.handle("/greet", user_id="2")
    print(f"命令结果: {result}")
    
    print("\n✅ 演示完成！")

if __name__ == "__main__":
    asyncio.run(main())
```

**预期输出:**
```
🚀 装饰器框架演示开始...
业务测试: 你好，张三！
🎉 你好，张三！ (来自IP: 192.168.1.1)
命令结果: 你好，李四！

✅ 演示完成！
```

### 4. 高级参数解析示例

```python
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.core.integration import enable_framework_integration, service
from decorators import command_on
from nucleus.dispatcher import DecisionCommandDispatcher

# 启用框架集成
enable_framework_integration()

# 智能参数解析器
def smart_arg_parser(args_str: str) -> dict:
    """智能参数解析器 - 支持多种参数格式"""
    result = {}
    
    # 1. JSON格式解析
    if args_str.strip().startswith('{'):
        try:
            import json
            return json.loads(args_str)
        except json.JSONDecodeError:
            pass
    
    # 2. key=value 格式解析
    if '=' in args_str:
        pairs = args_str.split()
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                # 自动类型推断
                if value.lower() in ('true', 'false'):
                    result[key] = value.lower() == 'true'
                elif value.isdigit():
                    result[key] = int(value)
                elif value.replace('.', '').isdigit():
                    result[key] = float(value)
                elif value.startswith('"') and value.endswith('"'):
                    result[key] = value[1:-1]  # 移除引号
                else:
                    result[key] = value
        return result
    
    # 3. 位置参数解析
    parts = args_str.strip().split()
    if parts:
        result['args'] = parts
    
    return result

# 用户服务
@service('singleton')
class UserService:
    def __init__(self):
        self.users = {
            "1": {"name": "张三", "age": 25, "active": True},
            "2": {"name": "李四", "age": 30, "active": False},
            "3": {"name": "王五", "age": 28, "active": True}
        }
    
    async def get_user(self, user_id: str):
        return self.users.get(user_id)
    
    async def search_users(self, **filters):
        """根据条件搜索用户"""
        results = []
        for user_id, user in self.users.items():
            match = True
            for key, value in filters.items():
                if key in user and user[key] != value:
                    match = False
                    break
            if match:
                results.append({"id": user_id, **user})
        return results

# 智能命令处理 - 支持JSON格式参数
@command_on("smart", "/user", arg_parser=smart_arg_parser).execute()
async def handle_user_command(user_service: UserService, **kwargs):
    """处理智能参数解析命令"""
    # kwargs包含了解析后的参数
    if 'id' in kwargs:
        user = await user_service.get_user(kwargs['id'])
        if user:
            return f"用户信息: {user['name']}, 年龄: {user['age']}, 状态: {'活跃' if user['active'] else '非活跃'}"
        return "用户不存在"
    elif 'active' in kwargs or 'age' in kwargs:
        # 搜索用户
        users = await user_service.search_users(**kwargs)
        if users:
            user_list = ", ".join([f"{u['name']}({u['id']})" for u in users])
            return f"找到 {len(users)} 个用户: {user_list}"
        return "没有找到匹配的用户"
    else:
        return f"收到参数: {kwargs}，支持参数: id=<用户ID>, active=<true|false>, age=<年龄>"

# 主演示函数
async def main():
    print("🚀 高级参数解析演示开始...")
    
    dispatcher = DecisionCommandDispatcher()
    
    # 测试不同的参数格式
    test_commands = [
        '/user {"id": "1"}',                    # JSON格式
        '/user id=2',                           # key=value格式
        '/user active=true',                    # 布尔值自动推断
        '/user age=25',                         # 数值类型
        '/user active=true age=28',             # 多条件组合
        '/user id="3"',                         # 带引号字符串
    ]
    
    for cmd in test_commands:
        print(f"\n执行命令: {cmd}")
        result = await dispatcher.handle(cmd)
        print(f"结果: {result}")
    
    print("\n✅ 高级参数解析演示完成！")

if __name__ == "__main__":
    asyncio.run(main())

## 📖 核心功能详解

### 5. 依赖注入系统



#### 服务注册方式



```python
from nucleus.core.integration import service, enable_framework_integration

enable_framework_integration()

# 1. 基本服务注册（单例）
@service('singleton')
class DatabaseService:
    def __init__(self):
        self.connection = "数据库连接"

# 2. 接口映射注册
class IDatabaseService:
    def query(self, sql: str): pass

@service(IDatabaseService)  # 自动注册接口到实现的映射
class MySQLService(IDatabaseService):
    def query(self, sql: str):
        return f"执行SQL: {sql}"

# 3. 生命周期选项
@service('transient')  # 每次请求创建新实例
class TransientService:
    pass

@service('scoped')     # 作用域内单例
class ScopedService:
    pass
```

### 6. 调用链系统

框架内置调用链机制，支持拦截器模式和上下文传递。

#### 自动调用链集成

所有使用框架装饰器的函数都会自动通过调用链执行：

```python
from decorators import on

@on("data_processing").execute()
async def process_data(data_service: IDataService, raw_data: str):
    # 这个函数会自动通过调用链执行
    # 支持依赖注入、日志记录、性能监控等
    processed = await data_service.process(raw_data)
    return processed
```

#### 自定义拦截器

```python
from nucleus.core.chain import ChainInterceptor, ChainContext

class CustomInterceptor(ChainInterceptor):
    async def before_execute(self, context: ChainContext):
        print(f"开始执行: {context.function_name}")
    
    async def after_execute(self, context: ChainContext):
        print(f"执行完成: {context.function_name}")
    
    async def on_error(self, context: ChainContext, error: Exception):
        print(f"执行错误: {context.function_name}, 错误: {error}")

# 添加自定义拦截器
from nucleus.core.integration import get_framework_integration
integration = get_framework_integration()
integration.add_chain_interceptor(CustomInterceptor())
```

### 📊 任务管理系统

框架提供强大的任务管理功能，支持异步任务调度和监控。

#### 基本任务管理

```python
from nucleus.core.integration import get_task_manager, enable_framework_integration

enable_framework_integration()
task_manager = get_task_manager()

# 创建异步任务
async def long_running_task(task_name: str, duration: float):
    print(f"开始任务: {task_name}")
    await asyncio.sleep(duration)
    print(f"完成任务: {task_name}")
    return f"任务 {task_name} 完成"

# 使用任务管理器创建任务
task_id = task_manager.create_task(
    long_running_task("数据处理", 2.0),
    name="数据处理任务",
    metadata={"user_id": "123", "priority": "high"}
)

# 等待任务完成
result = await task_manager.wait_for_task_async(task_id)
print(f"任务结果: {result}")
```

#### 任务统计和监控

```python
# 获取任务统计信息
stats = task_manager.get_statistics()
print(f"总任务数: {stats['total_tasks']}")
print(f"活跃任务: {stats['active_tasks']}")
print(f"完成任务: {stats['completed_tasks']}")
print(f"失败任务: {stats['failed_tasks']}")

# 获取具体任务信息
task_info = task_manager.get_task_info(task_id)
if task_info:
    print(f"任务状态: {task_info['status']}")
    print(f"执行时间: {task_info['duration']}秒")
    print(f"等待时间: {task_info['wait_time']}秒")
```

### 8. 事件装饰器系统

框架提供多种事件装饰器，支持不同类型的事件处理。

#### 普通事件处理 (@on)

```python
from decorators import on

@on("user_login").execute()
async def handle_login(user_id: str, ip: str, user_service: UserService):
    # 支持依赖注入
    user = await user_service.get_user(user_id)
    print(f"用户 {user.name} 从 {ip} 登录")

# 触发事件
from nucleus.dispatcher import EventDispatcher
dispatcher = EventDispatcher()
await dispatcher.trigger_event("user_login", user_id="123", ip="192.168.1.1")
```

#### 命令处理 (@command_on)

```python
from decorators import command_on

@command_on("bot", "/start", aliases=["/begin"], cooldown=5).execute()
async def handle_start_command(user_id: str):
    return "欢迎使用机器人！"

@command_on("bot", "/help").execute()
async def handle_help_command():
    return "可用命令: /start, /help, /status"

# 带参数的命令处理
@command_on("greet", "/greet").execute()
async def handle_greet_command(user_service: UserService, args: list = None):
    """处理问候命令 - args参数必须是list类型"""
    if args is None:
        args = []
    user_id = args[0] if args else "1"
    user = await user_service.get_user_by_id(user_id)
    return f"你好，{user['name']}！"

# 执行命令
from nucleus.dispatcher import DecisionCommandDispatcher
cmd_dispatcher = DecisionCommandDispatcher()
result = await cmd_dispatcher.execute_command("/start", user_id="123")
print(result)  # 输出: 欢迎使用机器人！

# 执行带参数的命令
result = await cmd_dispatcher.execute_command("/greet 2")
print(result)  # 输出: 你好，李四！
```

#### 定时任务 (@time_on)

```python
from decorators import time_on

@time_on("heartbeat", interval=60, priority=1).execute()
async def heartbeat_task():
    print("心跳检测...")
    # 执行健康检查逻辑

@time_on("cleanup", interval=3600, priority=2).execute()
async def cleanup_task(cache_service: ICacheService):
    print("清理过期缓存...")
    await cache_service.cleanup()
```

#### 正则表达式匹配 (@re_on)

```python
import re
from decorators import re_on

@re_on("message", r"^\d+$", re.IGNORECASE).execute()
async def handle_number_message(content: str):
    number = int(content)
    return f"你输入了数字: {number}"

@re_on("message", r"^[A-Za-z]+$").execute()
async def handle_text_message(content: str):
    return f"你输入了文本: {content}"
```

### 9. 优先级队列系统

框架内置高性能优先级队列，支持资源控制和并发管理。

#### 基本使用

```python
from nucleus import PriorityQueue, ResourceController

# 创建优先级队列
queue = PriorityQueue(maxsize=100)

# 添加任务（优先级越高越先执行）
await queue.put("低优先级任务", priority=1)
await queue.put("高优先级任务", priority=10)
await queue.put("中等优先级任务", priority=5)

# 获取任务（按优先级排序）
task1 = await queue.get()  # 高优先级任务
task2 = await queue.get()  # 中等优先级任务
task3 = await queue.get()  # 低优先级任务
```

#### 资源控制

```python
# 创建带资源控制的队列
resource_controller = ResourceController(
    max_memory_mb=100,      # 最大内存使用
    max_concurrent=10,      # 最大并发数
    cleanup_threshold=0.8   # 清理阈值
)

queue = PriorityQueue(
    maxsize=1000,
    resource_controller=resource_controller
)

# 队列会自动管理资源使用
await queue.put("大数据处理任务", priority=8, size_estimate=50)  # 预估50MB
```

## 10. 架构设计

### 核心组件

```
nucleus/
├── __init__.py              # 主要导出
├── core/                    # 核心功能
│   ├── integration.py      # 框架集成
│   ├── di.py               # 依赖注入
│   ├── chain.py            # 调用链
│   └── task_manager.py     # 任务管理
├── data/                    # 数据结构
│   ├── priority_queue.py   # 优先级队列
│   └── tree.py             # 树结构
├── dispatcher.py           # 调度器
└── Myclass.py             # 类核心

decorators/
├── __init__.py            # 装饰器导出
└── on.py                  # 所有装饰器实现
```

### 设计原则

1. **零依赖**: 仅使用Python标准库
2. **异步优先**: 完全支持异步编程
3. **类型安全**: 支持类型注解和检查
4. **模块化**: 组件可独立使用
5. **可扩展**: 支持自定义拦截器和服务

## 11. 最佳实践

### 1. 服务设计

```python
# ✅ 好的实践 - 基于接口的设计
class IRepository:
    async def get_by_id(self, id: str): pass

@service(IRepository)
class UserRepository(IRepository):
    async def get_by_id(self, id: str):
        # 实现获取用户逻辑
        pass

# ✅ 好的实践 - 构造函数注入
@service('singleton')
class UserService:
    def __init__(self, repository: IRepository):
        self.repository = repository
```

### 2. 错误处理

```python
# ✅ 好的实践 - 在事件处理中添加错误处理
@on("data_processing").execute()
async def handle_data_processing(data_service: IDataService, raw_data: str):
    try:
        result = await data_service.process(raw_data)
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"数据处理失败: {e}")
        return {"status": "error", "message": str(e)}
```

### 3. 性能优化

```python
# ✅ 好的实践 - 使用单例服务减少对象创建
@service('singleton')
class CacheService:
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str):
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any):
        self.cache[key] = value

# ✅ 好的实践 - 合理使用任务管理
async def batch_process(items: List[str]):
    task_manager = get_task_manager()
    tasks = []
    
    for item in items:
        task_id = task_manager.create_task(
            process_item(item),
            name=f"处理_{item}"
        )
        tasks.append(task_id)
    
    # 等待所有任务完成
    results = await asyncio.gather(*[
        task_manager.wait_for_task_async(task_id)
        for task_id in tasks
    ])
    
    return results
```

## 12. 高级用法

### 1. 自定义参数解析器

为命令处理添加自定义参数解析逻辑：

```python
from decorators import command_on

def custom_arg_parser(args_str: str) -> dict:
    """自定义参数解析器 - 将参数字符串解析为字典"""
    if not args_str.strip():
        return {"action": "help"}
    
    # 解析 key=value 格式的参数
    args_dict = {}
    for pair in args_str.split():
        if "=" in pair:
            key, value = pair.split("=", 1)
            args_dict[key] = value
    
    return args_dict if args_dict else {"action": "default"}

@command_on("advanced", "/advanced", arg_parser=custom_arg_parser).execute()
async def handle_advanced_command(user_service: UserService, parsed_args: dict):
    """处理带自定义参数解析的高级命令"""
    action = parsed_args.get("action", "default")
    
    if action == "help":
        return "可用参数: action=help|create|delete name=<用户名>"
    elif action == "create":
        name = parsed_args.get("name", "新用户")
        return f"创建用户: {name}"
    elif action == "delete":
        name = parsed_args.get("name")
        if name:
            return f"删除用户: {name}"
        return "错误: 删除操作需要指定 name 参数"
    else:
        return f"执行默认操作: {action}"

# 使用示例
# /advanced action=create name=张三  -> 创建用户: 张三
# /advanced action=help               -> 显示帮助信息
# /advanced                           -> 执行默认操作: default
```

#### 智能参数解析器实现

框架支持多种参数格式的智能解析：

```python
def smart_arg_parser(args_str: str) -> dict:
    """智能参数解析器 - 支持多种参数格式"""
    result = {}
    
    # 1. JSON格式解析
    if args_str.strip().startswith('{'):
        try:
            import json
            return json.loads(args_str)
        except json.JSONDecodeError:
            pass
    
    # 2. key=value 格式解析
    if '=' in args_str:
        pairs = args_str.split()
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                # 自动类型推断
                if value.lower() in ('true', 'false'):
                    result[key] = value.lower() == 'true'
                elif value.isdigit():
                    result[key] = int(value)
                elif value.replace('.', '').isdigit():
                    result[key] = float(value)
                elif value.startswith('"') and value.endswith('"'):
                    result[key] = value[1:-1]  # 移除引号
                else:
                    result[key] = value
        return result
    
    # 3. 位置参数解析
    parts = args_str.strip().split()
    if parts:
        result['args'] = parts
    
    return result

@command_on("smart", "/smart", arg_parser=smart_arg_parser).execute()
async def handle_smart_command(user_service: UserService, **kwargs):
    """处理智能参数解析命令"""
    # kwargs包含了解析后的参数
    if 'user_id' in kwargs:
        user = await user_service.get_user(kwargs['user_id'])
        return f"用户: {user['name']}"
    elif 'args' in kwargs:
        return f"收到参数: {kwargs['args']}"
    else:
        return f"收到参数: {kwargs}"

# 使用示例
# /smart {"user_id": "123", "action": "get"}     -> JSON格式
# /smart user_id=123 action=get                   -> key=value格式
# /smart 123 get                                  -> 位置参数格式
# /smart user_id=123 active=true count=5        -> 自动类型推断
```

### 2. 多事件监听器模式

实现发布-订阅模式，一个事件触发多个处理器：

```python
from decorators import on

# 用户登录事件的不同处理器
@on("user_login").execute()
async def log_user_login(user_id: str, ip: str):
    """记录用户登录日志"""
    print(f"[日志] 用户 {user_id} 从 {ip} 登录")

@on("user_login").execute()
async def update_user_status(user_id: str, user_service: UserService):
    """更新用户在线状态"""
    await user_service.update_status(user_id, "online")
    print(f"[状态] 用户 {user_id} 状态更新为在线")

@on("user_login").execute()
async def send_welcome_notification(user_id: str, notification_service: NotificationService):
    """发送欢迎通知"""
    await notification_service.send(user_id, "欢迎回来！")
    print(f"[通知] 向用户 {user_id} 发送欢迎消息")

# 触发一个事件，三个处理器都会执行
await dispatcher.trigger_event("user_login", user_id="123", ip="192.168.1.1")
```

### 3. 条件事件处理

使用正则表达式装饰器实现智能事件匹配：

```python
import re
from decorators import re_on

# 智能消息处理系统
@re_on("message", r"^订单_(\d+)$", re.IGNORECASE).execute()
async def handle_order_message(order_id: str, order_service: OrderService):
    """处理订单相关消息"""
    order_info = await order_service.get_order(order_id)
    return f"订单 {order_id} 状态: {order_info['status']}"

@re_on("message", r"^投诉_(.+)$").execute()
async def handle_complaint_message(content: str, complaint_service: ComplaintService):
    """处理投诉消息"""
    complaint_text = content.split("_", 1)[1]
    complaint_id = await complaint_service.create_complaint(complaint_text)
    return f"投诉已创建，编号: {complaint_id}"

@re_on("message", r"^\d+$").execute()
async def handle_number_message(number_str: str):
    """处理纯数字消息"""
    number = int(number_str)
    return f"收到数字: {number}，平方是: {number**2}"

# 使用示例
# dispatcher.trigger_event("message", content="订单_12345")  -> 返回订单状态
# dispatcher.trigger_event("message", content="投诉_服务不好") -> 创建投诉
# dispatcher.trigger_event("message", content="42")         -> 返回数字信息
```

### 4. 动态服务注册

在运行时动态注册和管理服务：

```python
from nucleus.core.integration import get_framework_integration

async def register_dynamic_services():
    """动态注册服务"""
    integration = get_framework_integration()
    container = integration.get_dependency_container()
    
    # 根据配置动态选择实现
    config = {"db_type": "mysql", "cache_type": "redis"}
    
    if config["db_type"] == "mysql":
        @service(IDatabaseService)
        class MySQLService(IDatabaseService):
            async def query(self, sql: str):
                return f"MySQL执行: {sql}"
    else:
        @service(IDatabaseService)
        class PostgreSQLService(IDatabaseService):
            async def query(self, sql: str):
                return f"PostgreSQL执行: {sql}"
    
    # 注册缓存服务
    if config["cache_type"] == "redis":
        @service(ICacheService)
        class RedisCacheService(ICacheService):
            def __init__(self):
                self.cache = {}
            async def get(self, key: str):
                return self.cache.get(key)
            async def set(self, key: str, value: str):
                self.cache[key] = value
    
    print("动态服务注册完成")

# 在应用启动时调用
await register_dynamic_services()
```

### 5. 任务流水线

使用任务管理器创建复杂的处理流水线：

```python
from nucleus.core.integration import get_task_manager

async def create_processing_pipeline(data: dict):
    """创建数据处理流水线"""
    task_manager = get_task_manager()
    
    # 步骤1: 数据验证
    validation_task = task_manager.create_task(
        validate_data(data),
        name="数据验证",
        priority=10
    )
    
    # 等待验证完成
    validation_result = await task_manager.wait_for_task_async(validation_task)
    
    if not validation_result["valid"]:
        return {"error": "数据验证失败", "details": validation_result["errors"]}
    
    # 步骤2: 数据清洗
    cleaning_task = task_manager.create_task(
        clean_data(validation_result["data"]),
        name="数据清洗",
        priority=8
    )
    
    # 步骤3: 数据转换（与清洗并行）
    transformation_task = task_manager.create_task(
        transform_data(validation_result["data"]),
        name="数据转换",
        priority=7
    )
    
    # 步骤4: 数据存储（依赖前两步完成）
    cleaned_data = await task_manager.wait_for_task_async(cleaning_task)
    transformed_data = await task_manager.wait_for_task_async(transformation_task)
    
    storage_task = task_manager.create_task(
        store_data(cleaned_data, transformed_data),
        name="数据存储",
        priority=5
    )
    
    # 等待最终结果
    final_result = await task_manager.wait_for_task_async(storage_task)
    
    return {
        "status": "success",
        "result": final_result,
        "pipeline_stats": task_manager.get_statistics()
    }

# 使用流水线
result = await create_processing_pipeline({"raw_data": "原始数据"})
```

### 6. 事件驱动架构

构建完整的事件驱动微服务架构：

```python
# 领域事件定义
class DomainEvents:
    USER_REGISTERED = "user.registered"
    ORDER_CREATED = "order.created"
    PAYMENT_COMPLETED = "payment.completed"
    INVENTORY_UPDATED = "inventory.updated"

# 事件处理器 - 用户服务
@on(DomainEvents.USER_REGISTERED).execute()
async def handle_user_registered(user_id: str, email: str, user_service: UserService):
    """处理用户注册事件"""
    # 创建用户档案
    await user_service.create_profile(user_id, email)
    
    # 触发后续事件
    await dispatcher.trigger_event("notification.send_welcome", user_id=user_id, email=email)

# 事件处理器 - 订单服务
@on(DomainEvents.ORDER_CREATED).execute()
async def handle_order_created(order_id: str, user_id: str, amount: float, order_service: OrderService):
    """处理订单创建事件"""
    # 验证库存
    inventory_result = await order_service.check_inventory(order_id)
    
    if inventory_result["available"]:
        # 触发支付流程
        await dispatcher.trigger_event(DomainEvents.PAYMENT_COMPLETED, order_id=order_id, amount=amount)
    else:
        # 库存不足，取消订单
        await order_service.cancel_order(order_id, "库存不足")

# 事件处理器 - 支付服务
@on(DomainEvents.PAYMENT_COMPLETED).execute()
async def handle_payment_completed(order_id: str, payment_service: PaymentService):
    """处理支付完成事件"""
    # 更新订单状态
    await payment_service.confirm_payment(order_id)
    
    # 触发库存更新
    await dispatcher.trigger_event(DomainEvents.INVENTORY_UPDATED, order_id=order_id)
    
    # 发送确认邮件
    await dispatcher.trigger_event("notification.send_confirmation", order_id=order_id)

# 事件处理器 - 库存服务
@on(DomainEvents.INVENTORY_UPDATED).execute()
async def handle_inventory_updated(order_id: str, inventory_service: InventoryService):
    """处理库存更新事件"""
    await inventory_service.deduct_inventory(order_id)
    
    # 触发物流流程
    await dispatcher.trigger_event("shipping.process_order", order_id=order_id)

# 使用示例 - 完整的电商流程
await dispatcher.trigger_event(DomainEvents.USER_REGISTERED, user_id="user123", email="user@example.com")
await dispatcher.trigger_event(DomainEvents.ORDER_CREATED, order_id="order456", user_id="user123", amount=99.99)
# 系统会自动处理整个流程链
```

## 13. 框架核心功能详解

框架提供企业级的核心功能系统，包括依赖注入、调用链拦截、任务管理和高级参数解析等完整解决方案。

### 参数解析系统

框架提供强大的参数解析功能，支持多种参数格式和自定义解析器。

#### 基础参数解析

默认情况下，框架会将命令参数按空格分割成列表：

```python
@command_on("basic", "/hello").execute()
async def handle_hello_command(args: list = None):
    """基础参数处理 - args是list类型"""
    if args is None:
        args = []
    return f"收到 {len(args)} 个参数: {args}"

# 使用示例
# /hello world python           -> 收到 2 个参数: ['world', 'python']
# /hello                        -> 收到 0 个参数: []
```

#### 高级参数解析

通过`arg_parser`参数，可以实现复杂的参数解析逻辑：

```python
def json_arg_parser(args_str: str) -> dict:
    """JSON格式参数解析器"""
    if not args_str.strip():
        return {}
    
    try:
        import json
        return json.loads(args_str)
    except json.JSONDecodeError:
        return {"error": "无效的JSON格式"}

@command_on("api", "/api", arg_parser=json_arg_parser).execute()
async def handle_api_command(**kwargs):
    """处理JSON格式参数"""
    if "error" in kwargs:
        return f"错误: {kwargs['error']}"
    
    # kwargs包含了解析后的JSON数据
    action = kwargs.get("action", "unknown")
    data = kwargs.get("data", {})
    return f"执行操作: {action}, 数据: {data}"

# 使用示例
# /api {"action": "create", "data": {"name": "张三"}}
# 返回: 执行操作: create, 数据: {'name': '张三'}
```

#### 智能参数解析器

框架支持自动类型推断和多种参数格式：

```python
def smart_arg_parser(args_str: str) -> dict:
    """智能参数解析器 - 支持多种参数格式"""
    result = {}
    
    # 1. JSON格式解析
    if args_str.strip().startswith('{'):
        try:
            import json
            return json.loads(args_str)
        except json.JSONDecodeError:
            pass
    
    # 2. key=value 格式解析
    if '=' in args_str:
        pairs = args_str.split()
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                # 自动类型推断
                if value.lower() in ('true', 'false'):
                    result[key] = value.lower() == 'true'
                elif value.isdigit():
                    result[key] = int(value)
                elif value.replace('.', '').isdigit():
                    result[key] = float(value)
                elif value.startswith('"') and value.endswith('"'):
                    result[key] = value[1:-1]  # 移除引号
                else:
                    result[key] = value
        return result
    
    # 3. 位置参数解析
    parts = args_str.strip().split()
    if parts:
        result['args'] = parts
    
    return result

@command_on("smart", "/smart", arg_parser=smart_arg_parser).execute()
async def handle_smart_command(user_service: UserService, **kwargs):
    """处理智能参数解析命令"""
    # kwargs包含了解析后的参数
    if 'user_id' in kwargs:
        user = await user_service.get_user(kwargs['user_id'])
        return f"用户: {user['name']}"
    elif 'args' in kwargs:
        return f"收到参数: {kwargs['args']}"
    else:
        return f"收到参数: {kwargs}"

# 使用示例
# /smart {"user_id": "123", "action": "get"}     -> JSON格式
# /smart user_id=123 action=get                   -> key=value格式
# /smart 123 get                                  -> 位置参数格式
# /smart user_id=123 active=true count=5        -> 自动类型推断
```

#### 参数解析器特性

1. **类型自动推断**: 自动识别布尔值、整数、浮点数、带引号字符串
2. **多格式支持**: 支持JSON、key=value、位置参数等多种格式
3. **错误处理**: 提供友好的错误提示和回退机制
4. **灵活扩展**: 支持自定义解析逻辑，满足特定业务需求
5. **依赖注入兼容**: 解析结果可以直接用于依赖注入

## 14. 参数参考

### @service 装饰器参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| lifetime_or_interface | str/Type | 'singleton' | 生命周期('singleton'/'transient'/'scoped')或接口类型 |

### @on 装饰器参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| name | str | 必填 | 事件名称 |

### @command_on 装饰器参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| name | str | 必填 | 处理器名称 |
| command | str | 必填 | 命令字符串（必须以/开头） |
| aliases | List[str] | None | 命令别名列表 |
| cooldown | int | 0 | 冷却时间（秒） |
| arg_parser | Callable[[str], Dict[str, Any]] | None | 自定义参数解析函数，将参数字符串解析为字典 |

**重要提示**: 
1. 命令处理函数的`args`参数必须是`list`类型，不是`str`类型。框架会自动将命令参数分割成列表传入。
2. `arg_parser`参数支持自定义参数解析逻辑，可以解析复杂格式的参数，如`key=value`格式、JSON格式等。
3. 如果提供了`arg_parser`，框架会使用自定义解析器处理参数，否则使用默认的空格分割方式。

### @time_on 装饰器参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| name | str | 必填 | 任务名称 |
| interval | int | 0 | 执行间隔（秒） |
| priority | int | 1 | 任务优先级 |

### @re_on 装饰器参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| name | str | 必填 | 处理器名称 |
| content | str | 必填 | 匹配内容 |
| pattern | object | 必填 | 正则表达式模式 |
| priority | int | 1 | 处理器优先级 |

## 15. 测试验证

### 运行所有测试

```bash
# 运行完整测试套件
python -m pytest tests/ -v

# 预期输出:
# =========== test session starts ===========
# collected 44 items
# tests/test_basic.py ..............    [32%]
# tests/test_core_integration.py ..............    [64%]
# tests/test_priority_queue.py ..............    [100%]
# =========== 44 passed in 1.50s ===========
```

### 运行特定示例

```bash
# 快速开始示例
python examples/quick_start_example.py

# 依赖注入示例
python examples/on_di_example.py

# 命令调度示例
python examples/command_on_di_example.py

# 优先级队列示例
python examples/priority_queue_example.py

# 完整演示
python complete_demo.py
```

### 性能测试

```bash
# 优先级队列性能测试
python examples/priority_queue_example.py
# 预期性能: >100,000 任务/秒

# 完整框架性能测试
python complete_demo.py
# 包含事件处理、任务调度、依赖注入等综合测试
```

## 16. 故障排除

### 常见问题

#### 1. ModuleNotFoundError: No module named 'nucleus'

**问题**: 导入模块失败
**解决**: 确保在项目根目录运行，或添加路径：
```python
import sys
sys.path.insert(0, '.')  # 添加当前目录到Python路径
```

#### 2. 装饰器不生效

**问题**: 使用了`@on("event")`但没有`.execute()`
**解决**: 所有事件装饰器都必须使用`.execute()`：
```python
# ❌ 错误
@on("event")
def handler(): pass

# ✅ 正确
@on("event").execute()
def handler(): pass
```

#### 3. 依赖注入失败

**问题**: 服务无法解析
**解决**: 确保：
1. 先调用`enable_framework_integration()`
2. 服务已用`@service`装饰器注册
3. 接口和实现类关系正确

```python
# ✅ 正确顺序
enable_framework_integration()  # 先启用集成

@service(IMyService)  # 再注册服务
class MyService(IMyService):
    pass
```

### 4. 命令参数类型错误

**问题**: 命令处理函数参数类型不匹配，导致`TypeError`
**解决**: `@command_on`装饰器的命令处理函数必须使用`list`类型接收参数：

```python
# ❌ 错误 - 使用str类型参数
@command_on("greet", "/greet").execute()
async def handle_greet_command(user_service: UserService, args: str = ""):
    user_id = args  # 这里会出错，因为args实际是list
    
# ✅ 正确 - 使用list类型参数
@command_on("greet", "/greet").execute()
async def handle_greet_command(user_service: UserService, args: list = None):
    if args is None:
        args = []
    user_id = args[0] if args else "1"  # 正确处理list参数
```

### 5. 自定义参数解析器错误

**问题**: 使用`arg_parser`参数时，解析器函数返回类型不正确
**解决**: 确保自定义参数解析器返回`dict`类型：

```python
# ❌ 错误 - 解析器返回非dict类型
def bad_parser(args_str: str):
    return args_str.split()  # 返回list，会导致错误

# ✅ 正确 - 解析器返回dict类型
def good_parser(args_str: str) -> dict:
    return {"args": args_str.split()}  # 返回dict

@command_on("test", "/test", arg_parser=good_parser).execute()
async def handle_test_command(parsed_args: dict):
    # parsed_args是dict类型，包含解析后的参数
    return f"收到参数: {parsed_args}"
```

### 6. 事件不触发

**问题**: 事件触发但没有响应
**解决**: 检查事件名称是否匹配：
```python
@on("user_login").execute()  # 注册事件
async def handle_login():
    pass

# 触发时使用相同名称
await dispatcher.trigger_event("user_login")  # ✅ 匹配
await dispatcher.trigger_event("login")       # ❌ 不匹配
```

### 7. 参数解析器类型错误

**问题**: 自定义参数解析器函数签名不正确
**解决**: 确保参数解析器符合`Callable[[str], Dict[str, Any]]`类型：

```python
# ❌ 错误 - 函数签名不正确
def bad_parser(arg1: str, arg2: str) -> dict:  # 参数太多
    return {}

# ✅ 正确 - 函数签名正确
def good_parser(args_str: str) -> dict:
    """正确的参数解析器签名"""
    return {"parsed": args_str}

@command_on("correct", "/correct", arg_parser=good_parser).execute()
async def handle_correct_command(parsed: dict):
    return f"解析结果: {parsed}"
```

### 调试技巧

#### 1. 检查服务注册状态

```python
from nucleus.core.integration import get_framework_integration

integration = get_framework_integration()
container = integration.get_dependency_container()

# 查看已注册的服务
print("已注册服务:", list(container._services.keys()))

# 查看单例实例
print("单例实例:", list(container._singletons.keys()))
```

#### 2. 检查事件处理器

```python
from nucleus import Myclass

# 查看所有注册的类
all_classes = Myclass.get_all_classes()
print("注册的类:", list(all_classes.keys()))

# 查看特定事件处理器
login_handlers = [name for name in all_classes.keys() if "user_login" in str(all_classes[name])]
print("登录事件处理器:", login_handlers)
```

#### 3. 任务状态检查

```python
task_manager = get_task_manager()

# 获取所有任务状态
all_tasks = task_manager.get_all_tasks_info()
for task in all_tasks:
    print(f"任务 {task['task_id']}: {task['status']}")

# 获取统计信息
stats = task_manager.get_statistics()
print(f"任务统计: {stats}")
```

## 17. 相关文档

- [API参考文档](API_REFERENCE.md) - 完整的API文档
- [最佳实践指南](BEST_PRACTICES.md) - 高级使用技巧
- [生产部署指南](PRODUCTION_DEPLOYMENT_GUIDE.md) - 部署和运维指南
- [测试运行指南](RUN_TESTS.md) - 测试执行说明

## 18. 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 19. 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE.txt) 文件了解详情。

## 20. 支持

如果遇到问题：

1. 查看本文档的故障排除部分
2. 检查 [API参考文档](API_REFERENCE.md)
3. 运行测试验证框架状态
4. 在GitHub Issues中寻求帮助

---

**⭐ 如果这个项目对你有帮助，请给个Star！**

---

## 18. 贡献指南

我们欢迎所有形式的贡献！

### 🎯 贡献方式
- 🐛 **报告Bug**: 在Issues中报告发现的问题
- 💡 **功能建议**: 提出新功能或改进建议  
- 📝 **文档改进**: 改进文档或添加示例
- 🔧 **代码贡献**: 提交Pull Request修复问题或添加功能

### 📝 贡献步骤
1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 📋 代码规范
- 遵循PEP 8编码规范
- 添加适当的类型注解
- 编写单元测试
- 更新相关文档

---

## 21. 更新日志

### v2.4.0 (当前版本)
- ✅ **新增**: 完整的参数解析系统文档
- ✅ **新增**: 智能参数解析器实现和示例
- ✅ **新增**: 高级参数解析用法和故障排除指南
- ✅ **增强**: @command_on装饰器文档，详细说明arg_parser参数
- ✅ **增强**: 快速开始示例，添加参数解析演示
- ✅ **修复**: 文档编号和格式问题

### v2.3.0 
- ✅ **新增**: 依赖注入系统完整实现
- ✅ **新增**: 调用链拦截器模式
- ✅ **新增**: 任务管理和优先级队列
- ✅ **新增**: 框架集成和生命周期管理
- ✅ **新增**: 44个完整测试用例

### v2.2.0
- ✅ **新增**: 事件装饰器系统 (@on, @command_on, @time_on, @re_on)
- ✅ **新增**: 冷却时间和命令别名支持
- ✅ **新增**: 正则表达式事件匹配
- ✅ **新增**: 异步/同步函数统一支持

### v2.1.0
- ✅ **新增**: 服务注册和生命周期管理
- ✅ **新增**: 单例模式支持
- ✅ **新增**: 接口映射系统
- ✅ **新增**: 基础装饰器功能

---

## 19. 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

### 📞 联系方式
- **项目主页**: [https://github.com/your-repo/decorator_framework](https://github.com/your-repo/decorator_framework)
- **问题反馈**: [Issues](https://github.com/your-repo/decorator_framework/issues)
- **文档支持**: [Wiki](https://github.com/your-repo/decorator_framework/wiki)

### 🙏 致谢
感谢所有贡献者和使用者的支持！特别感谢以下贡献者：
- 框架核心开发团队
- 文档编写和维护人员
- 测试和反馈提供者

**让我们一起打造更好的Python企业级开发框架！** 🚀