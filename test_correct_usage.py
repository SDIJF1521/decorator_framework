#!/usr/bin/env python3
"""
正确的框架功能测试
基于实际API使用方式
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from decorators.on import on, time_on
from nucleus.dispatcher import EventDispatcher, TimeTaskScheduler


def test_basic_functionality():
    """测试基本功能"""
    print("=== 框架功能测试 ===")
    
    # 测试1：基本事件注册和触发
    print("\n1. 测试基本事件:")
    
    @on("hello").execute()
    def greet(name):
        return f"Hello, {name}!"
    
    dispatcher = EventDispatcher()
    result = asyncio.run(dispatcher.trigger_event("hello", "World"))
    print(f"   结果: {result}")
    
    # 测试2：异步函数支持
    print("\n2. 测试异步函数:")
    
    @on("async_test").execute()
    async def async_handler(data):
        await asyncio.sleep(0.1)
        return f"Async processed: {data}"
    
    result = asyncio.run(dispatcher.trigger_event("async_test", "test_data"))
    print(f"   结果: {result}")
    
    # 测试3：未注册事件
    print("\n3. 测试未注册事件:")
    result = asyncio.run(dispatcher.trigger_event("unknown_event", "data"))
    print(f"   结果: {result}")
    
    print("\n=== 所有基本测试完成 ===")


async def test_time_scheduler():
    """测试定时任务调度器"""
    print("\n=== 定时任务测试 ===")
    
    scheduler = TimeTaskScheduler()
    
    # 注册定时任务
    @time_on("test_timer", priority=1, interval=2).execute()
    def test_timer():
        print("   定时任务执行")
        return "timer_executed"
    
    # 加载任务
    scheduler.load_time_tasks()
    
    # 启动调度器
    await scheduler.start()
    
    # 运行3秒观察
    print("   运行3秒观察定时任务...")
    await asyncio.sleep(3)
    
    # 停止调度器
    await scheduler.stop()
    
    print("=== 定时任务测试完成 ===")


async def test_multiple_events():
    """测试多个事件"""
    print("\n=== 多事件测试 ===")
    
    dispatcher = EventDispatcher()
    
    # 注册多个事件
    @on("event_a").execute()
    def handler_a(data):
        return f"A处理: {data}"
    
    @on("event_b").execute()
    async def handler_b(data):
        await asyncio.sleep(0.05)
        return f"B处理: {data}"
    
    # 并发触发事件
    results = await asyncio.gather(
        dispatcher.trigger_event("event_a", "数据A"),
        dispatcher.trigger_event("event_b", "数据B")
    )
    
    print(f"   返回结果: {results}")
    
    print("=== 多事件测试完成 ===")


if __name__ == "__main__":
    # 运行基本测试
    test_basic_functionality()
    
    # 运行异步测试
    asyncio.run(test_time_scheduler())
    asyncio.run(test_multiple_events())