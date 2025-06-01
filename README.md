# 🌟 基于 decorator_framework 的事件与命令注册调度系统 使用文档

## 1. 项目简介

- 本项目实现了基于 Python 元类 ClassNucleus 的事件与命令注册调度系统。
  - 通过装饰器自动注册事件和命令处理函数。
  - 支持同步/异步执行。
  - 命令系统内置冷却机制和别名支持。
  - 采用决策树设计简化命令流程控制。
- 采用决策树设计简化命令流程控制。

## 2.环境依赖

- Python 3.8 及以上版本
- 标准库依赖（ `asyncio` 、 `uuid` 、 `dataclasses` 、`typing` 等）
- 无需额外第三方库

## 3. 代码结构说明

- ```text
    project_root/
                │
                ├── decorators/
                │   └── on.py               # 装饰器模块，定义 @on 和 @command_on
                │
                ├── nucleus/
                │   ├── Myclass.py          # 元类 ClassNucleus 定义和注册管理
                │   └── dispatcher.py       # 事件与命令调度器实现
                │
                └── your_script.py          # 用户自定义事件或命令处理函数示例
  ```

## 4. 装饰器详解

### 4.1 @on 普通事件注册

- 用于注册普通事件处理函数，支持同步或异步函数。

  - ```python
        from decorators.on import on
        @on("user_login").execute()
        async def handle_login(user_id: int):
            print(f"用户 {user_id} 登录事件触发")
      ```

    - 参数
      - `name`：事件名称，唯一标识。
    - 工作原理
      - 注册时自动创建内部类并加入 ClassNucleus 注册表。

### 4.2 @command_on 命令注册

- 用于注册命令处理函数，支持异步/同步，具备冷却与别名功能。

  - ```python
      from decorators.on import command_on

      @command_on(
          name="greet_cmd",
          command="/greet",
          aliases=["/hello", "/hi"],
          cooldown=10,
          arg_parser=lambda arg_str: {"name": arg_str.strip()}
      ).execute()
      async def greet_command(name: str):
          return f"Hello, {name}!"
      ```

    - 参数说明

      - | 参数           | 类型         | 说明                       |
        | ------------ | ---------- | ------------------------ |
        | `name`       | `str`      | 命令处理器唯一名称                |
        | `command`    | `str`      | 命令文本，必须以 `/` 开头          |
        | `aliases`    | `list`     | 命令别名列表（可选）               |
        | `cooldown`   | `int`      | 命令冷却时间（秒），防止频繁调用（默认0）    |
        | `arg_parser` | `Callable` | 自定义参数解析函数，将字符串转为字典参数（可选） |

### 4.3 @time_on 定时事件注册

- ```python
    from decorators.on import time_on
    # 定时任务（使用interval参数）
    @time_on(
        name="heartbeat",
        priority=2,
        interval=5  # 每5秒执行
    ).execute()
    async def heartbeat():
        print("系统心跳: 正常运行中...")


    @time_on(
        name="cleanup",
        priority=1,
        interval=10  # 每10秒执行
    ).execute()
    async def cleanup():
        print("执行临时文件清理...")
    ```

  - 用于注册定时事件处理函数，支持异步执行。

    - 参数说明
      - `name`：事件名称，唯一标识。
      - `priority`：优先级，整数值，数值越小优先级越高。
      - `interval`：定时间隔（秒），每隔指定时间触发一次。

    - 工作原理
      - 定时器会在后台循环检查时间间隔，并触发对应事件。

## 5. 事件触发器 EventDispatcher 使用

- 用于触发已注册的普通事件。

  - ```python
      import asyncio
      from nucleus.dispatcher import EventDispatcher
      
      dispatcher = EventDispatcher()
      
      async def main():
          result = await dispatcher.trigger_event("user_login", user_id=123)
          print(result)
      
      asyncio.run(main())
    ```

    - 说明
      - 根据事件名查找对应处理函数执行。
      - 支持异步或同步函数，自动处理。

## 6. 命令调度器 DecisionCommandDispatcher 使用

- 用于处理用户输入的命令字符串，支持冷却、别名和参数解析。

  - ```python
      import asyncio
      from nucleus.dispatcher import DecisionCommandDispatcher
      
      cmd_dispatcher = DecisionCommandDispatcher()
      
      async def main():
          # 模拟接收命令输入
          result = await cmd_dispatcher.handle("/greet Alice")
          print(result)
      
      asyncio.run(main())
    ```

    - 处理流程
      1. 解析命令及参数
      2. 验证命令是否注册
      3. 检查冷却时间
      4. 调用命令执行函数
      5. 返回结果

## 7定时事件调度器 TimeTaskScheduler 使用

- 启动定时事件调度器，自动触发注册的定时任务

- ```python
    from nucleus.dispatcher import TimeTaskScheduler
    
    # 启动定时任务调度器
    scheduler = TimeTaskScheduler()
    
    async def main():
        await scheduler.start()  # 启动定时任务调度器
    
    asyncio.run(main())
    ```

  - 说明
    - 定时任务会在后台循环执行，触发注册的定时事件。
    - 支持异步函数，自动处理。

- 停止调度器

- ```python
    await scheduler.stop()  # 停止定时任务调度器
    ```

  - 注意
    - 定时任务会在后台线程中运行，建议在应用退出前调用 `stop()` 方法停止调度器。

    - 可以通过设置 `interval` 参数来控制任务执行频率。

## 8. 完整示例

- ``` python
    import asyncio
    from decorators.on import on, command_on, time_on
    from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher,  TimeTaskScheduler

    time_scheduler = TimeTaskScheduler()
    
    # 注册普通事件
    @on("say_hello").execute()
    def say_hello_event(name: str):
        return f"Hello, {name}!"
    
    # 注册命令
    @command_on(
        name="add_cmd",
        command="/add",
        cooldown=3,
        arg_parser=lambda s: {"a": int(s.split()[0]), "b": int(s.split()[1])}
    ).execute()
    async def add_command(a: int, b: int):
        return f"结果是: {a + b}"
    # 定时任务（使用interval参数）
    @time_on(
        name="heartbeat",
        priority=2,
        interval=5  # 每5秒执行
    ).execute()
    async def heartbeat():
        print("系统心跳: 正常运行中...")


    @time_on(
        name="cleanup",
        priority=1,
        interval=10  # 每10秒执行
    ).execute()
    async def cleanup():
        print("执行临时文件清理...")
    
    async def main():
        await time_scheduler.start()
        # 触发事件
        ed = EventDispatcher()
        print(await ed.trigger_event("say_hello", "ChatGPT"))
    
        # 处理命令
        cd = DecisionCommandDispatcher()
        print(await cd.handle("/add 10 20"))
         # 运行30秒观察定时任务
        print("\n运行中，观察定时任务...")
        await asyncio.sleep(30)

        # 停止调度器
        await time_scheduler.stop()
    
    asyncio.run(main())
  ```

- 输出：

  - ```
    已加载 2 个定时任务
    定时任务调度器已启动
    注册的任务: ['cleanup', 'heartbeat']
    Hello, ChatGPT!
    结果是: 30

    运行中，观察定时任务...
    系统心跳: 正常运行中...
    任务执行成功: heartbeat
    执行临时文件清理...
    任务执行成功: cleanup
    系统心跳: 正常运行中...
    任务执行成功: heartbeat
    系统心跳: 正常运行中...
    任务执行成功: heartbeat
    执行临时文件清理...
    任务执行成功: cleanup
    系统心跳: 正常运行中...
    任务执行成功: heartbeat
    系统心跳: 正常运行中...
    任务执行成功: heartbeat
    定时任务调度器已停止
    ```

## 8. 注意事项与扩展建议

- 命令必须以 / 开头，否则注册时会抛异常。

- 冷却时间单位为秒，0表示无冷却。

- arg_parser 必须返回字典，作为命令执行函数的关键字参数。

- 异步命令和事件均支持，系统自动检测函数类型。

- 决策树结构可根据业务需求扩展复杂逻辑。

- 建议添加异常捕获和日志以提升稳定性。
