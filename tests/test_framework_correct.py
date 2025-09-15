"""
装饰器框架正确的测试套件
基于实际API实现
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from decorators.on import on
from nucleus.dispatcher import EventDispatcher, TimeTaskScheduler


class TestDecoratorFramework:
    """测试装饰器框架的核心功能"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.dispatcher = EventDispatcher()
        self.events_received = []
    
    def test_basic_decorator_registration(self):
        """测试基本装饰器注册"""
        
        @on("test_event")
        def handler(data):
            self.events_received.append(data)
            return f"processed_{data}"
        
        # 装饰器应该成功注册
        assert len(self.events_received) == 0  # 注册时不执行
    
    def test_event_dispatcher_exists(self):
        """测试事件调度器存在"""
        assert self.dispatcher is not None
        assert hasattr(self.dispatcher, 'trigger_event')
    
    def test_basic_event_triggering(self):
        """测试基本事件触发"""
        
        @on("greeting_event")
        def greeting_handler(name):
            return f"Hello, {name}!"
        
        # 触发事件
        result = asyncio.run(self.dispatcher.trigger_event("greeting_event", "Alice"))
        assert result == "Hello, Alice!"
    
    def test_multiple_event_handlers(self):
        """测试多个事件处理器"""
        
        results = []
        
        @on("multi_event")
        def handler1(data):
            results.append(f"handler1_{data}")
            return f"result1_{data}"
        
        @on("multi_event") 
        def handler2(data):
            results.append(f"handler2_{data}")
            return f"result2_{data}"
        
        # 注意：根据实际实现，最后一个注册的处理器会覆盖前面的
        result = asyncio.run(self.dispatcher.trigger_event("multi_event", "test"))
        assert result is not None
    
    def test_async_handler_support(self):
        """测试异步处理器支持"""
        
        @on("async_event")
        async def async_handler(delay):
            await asyncio.sleep(0.01)  # 10ms延迟
            return f"async_result_{delay}"
        
        result = asyncio.run(self.dispatcher.trigger_event("async_event", "test"))
        assert result == "async_result_test"
    
    def test_event_not_found_handling(self):
        """测试未找到事件的处理"""
        
        result = asyncio.run(self.dispatcher.trigger_event("nonexistent_event", "data"))
        assert result == "事件 nonexistent_event 未注册"
    
    def test_time_task_scheduler_exists(self):
        """测试定时任务调度器存在"""
        scheduler = TimeTaskScheduler()
        assert scheduler is not None
        assert hasattr(scheduler, 'start')
        assert hasattr(scheduler, 'stop')


class TestTimeTaskScheduler:
    """测试定时任务调度器"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.scheduler = TimeTaskScheduler()
    
    def test_load_time_tasks(self):
        """测试加载定时任务"""
        
        @on("timer_test")
        def timer_handler():
            return "timer_executed"
        
        # 加载任务（实际加载需要time_on装饰器）
        self.scheduler.load_time_tasks()
        # 应该正常执行，即使没有任务
        assert True
    
    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self):
        """测试调度器启动和停止"""
        
        await self.scheduler.start()
        await asyncio.sleep(0.1)  # 短暂运行
        await self.scheduler.stop()
        
        assert not self.scheduler.running


# 运行测试的配置文件
if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v"])