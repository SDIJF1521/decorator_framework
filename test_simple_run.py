#!/usr/bin/env python3
"""
简单的框架功能测试
直接运行验证框架是否正常工作
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from decorators.on import on
from nucleus.dispatcher import EventDispatcher


def test_basic_functionality():
    """测试基本功能"""
    print("=== 框架功能测试 ===")
    
    # 创建调度器
    dispatcher = EventDispatcher()
    
    # 测试1：基本事件注册和触发
    print("\n1. 测试基本事件:")
    
    @on("hello")
    def greet(name):
        return f"Hello, {name}!"
    
    result = asyncio.run(dispatcher.trigger_event("hello", "World"))
    print(f"   结果: {result}")
    
    # 测试2：异步函数支持
    print("\n2. 测试异步函数:")
    
    @on("async_test")
    async def async_handler(data):
        await asyncio.sleep(0.1)
        return f"Async processed: {data}"
    
    result = asyncio.run(dispatcher.trigger_event("async_test", "test_data"))
    print(f"   结果: {result}")
    
    # 测试3：未注册事件
    print("\n3. 测试未注册事件:")
    result = asyncio.run(dispatcher.trigger_event("unknown_event", "data"))
    print(f"   结果: {result}")
    
    print("\n=== 所有测试完成 ===")


async def test_async_functionality():
    """异步测试"""
    print("=== 异步测试 ===")
    
    dispatcher = EventDispatcher()
    
    # 测试多个事件
    events_triggered = []
    
    @on("event1")
    def handler1(data):
        events_triggered.append(f"handler1_{data}")
        return f"result1_{data}"
    
    @on("event2")
    async def handler2(data):
        await asyncio.sleep(0.05)
        events_triggered.append(f"handler2_{data}")
        return f"result2_{data}"
    
    # 并发触发事件
    results = await asyncio.gather(
        dispatcher.trigger_event("event1", "A"),
        dispatcher.trigger_event("event2", "B")
    )
    
    print(f"   触发的事件: {events_triggered}")
    print(f"   返回结果: {results}")
    
    print("=== 异步测试完成 ===")


if __name__ == "__main__":
    # 运行基本测试
    test_basic_functionality()
    
    # 运行异步测试
    asyncio.run(test_async_functionality())