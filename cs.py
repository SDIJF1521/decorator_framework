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