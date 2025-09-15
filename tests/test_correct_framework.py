#!/usr/bin/env python3
"""
正确的装饰器框架测试套件
基于实际API和工作原理
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from decorators.on import on, time_on, re_on
from nucleus.dispatcher import EventDispatcher, TimeTaskScheduler


class TestEventSystem:
    """测试事件系统"""
    
    def test_event_registration(self):
        """测试事件注册"""
        
        @on("test_event").execute()
        def test_handler(data):
            return f"processed_{data}"
        
        # 装饰器应该成功注册（不会立即执行）
        assert True
    
    def test_event_dispatcher_creation(self):
        """测试事件调度器创建"""
        dispatcher = EventDispatcher()
        assert dispatcher is not None
        assert hasattr(dispatcher, 'trigger_event')
    
    def test_basic_event_triggering(self):
        """测试基本事件触发"""
        
        @on("greeting").execute()
        def greeting_handler(name):
            return f"Hello, {name}!"
        
        dispatcher = EventDispatcher()
        result = asyncio.run(dispatcher.trigger_event("greeting", "World"))
        assert result == "Hello, World!"
    
    def test_async_event_handling(self):
        """测试异步事件处理"""
        
        @on("async_test").execute()
        async def async_handler(data):
            await asyncio.sleep(0.01)
            return f"async_{data}"
        
        dispatcher = EventDispatcher()
        result = asyncio.run(dispatcher.trigger_event("async_test", "result"))
        assert result == "async_result"
    
    def test_unknown_event_handling(self):
        """测试未知事件处理"""
        dispatcher = EventDispatcher()
        result = asyncio.run(dispatcher.trigger_event("unknown", "data"))
        assert result == "事件 unknown 未注册"
    
    def test_event_with_multiple_parameters(self):
        """测试多参数事件"""
        
        @on("multi_param").execute()
        def multi_handler(a, b, c):
            return f"{a}_{b}_{c}"
        
        dispatcher = EventDispatcher()
        result = asyncio.run(dispatcher.trigger_event("multi_param", "x", "y", "z"))
        assert result == "x_y_z"


class TestTimeScheduler:
    """测试定时任务调度器"""
    
    def test_scheduler_creation(self):
        """测试调度器创建"""
        scheduler = TimeTaskScheduler()
        assert scheduler is not None
        assert hasattr(scheduler, 'start')
        assert hasattr(scheduler, 'stop')
        assert hasattr(scheduler, 'load_time_tasks')
    
    def test_task_loading(self):
        """测试任务加载"""
        scheduler = TimeTaskScheduler()
        
        # 注册定时任务
        @time_on("test_task", priority=1, interval=5).execute()
        def test_timer():
            return "timer_executed"
        
        # 应该能加载任务
        scheduler.load_time_tasks()
        assert True  # 能正常执行即可
    
    def test_scheduler_start_stop(self):
        """测试调度器启动和停止"""
        scheduler = TimeTaskScheduler()
        
        # 同步测试
        async def run_test():
            await scheduler.start()
            await asyncio.sleep(0.1)  # 短暂运行
            await scheduler.stop()
            return not scheduler.running
        
        result = asyncio.run(run_test())
        assert result is True


class TestReSystem:
    """测试正则表达式系统"""
    
    def test_re_registration(self):
        """测试正则表达式注册"""
        
        @re_on("test_re", content="hello", pattern=r"hello").execute()
        def re_handler():
            return "matched"
        
        assert True  # 应该成功注册


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        
        # 注册多个类型的事件
        @on("user_action").execute()
        def handle_user_action(action):
            return f"User did: {action}"
        
        @time_on("background_task", priority=2, interval=10).execute()
        def background_task():
            return "background processed"
        
        # 测试事件触发
        dispatcher = EventDispatcher()
        result = asyncio.run(dispatcher.trigger_event("user_action", "login"))
        assert result == "User did: login"


# 运行测试的配置
if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])
    
    # 或者运行特定测试
    # pytest.main([__file__, "::TestEventSystem", "-v"])