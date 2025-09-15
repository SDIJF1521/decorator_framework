"""
装饰器框架测试套件
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
from nucleus.dispatcher import EventDispatcher


class TestDecoratorFramework:
    """测试装饰器框架的核心功能"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.dispatcher = EventDispatcher()
        self.events_received = []
    
    def test_basic_decorator(self):
        """测试基本装饰器功能"""
        
        @on("test_event")
        def handler(data):
            self.events_received.append(data)
        
        # 触发事件
        asyncio.run(self.dispatcher.emit("test_event", "test_data"))
        
        assert len(self.events_received) == 1
        assert self.events_received[0] == "test_data"
    
    def test_multiple_handlers(self):
        """测试多个处理器"""
        
        @on("multi_event")
        def handler1(data):
            self.events_received.append(f"handler1: {data}")
        
        @on("multi_event")
        def handler2(data):
            self.events_received.append(f"handler2: {data}")
        
        asyncio.run(self.dispatcher.emit("multi_event", "shared"))
        
        assert len(self.events_received) == 2
        assert "handler1: shared" in self.events_received
        assert "handler2: shared" in self.events_received
    
    @pytest.mark.asyncio
    async def test_async_handler(self):
        """测试异步处理器"""
        
        result = []
        
        @on("async_event")
        async def async_handler(data):
            await asyncio.sleep(0.1)
            result.append(data)
        
        await self.dispatcher.emit("async_event", "async_data")
        await asyncio.sleep(0.2)  # 等待异步完成
        
        assert result == ["async_data"]
    
    def test_event_not_found(self):
        """测试未注册事件的处理"""
        
        # 触发未注册的事件应该不报错
        asyncio.run(self.dispatcher.emit("nonexistent_event", "data"))
        
        # 应该正常完成，没有异常
        assert True
    
    def test_handler_parameters(self):
        """测试处理器参数传递"""
        
        received_args = []
        
        @on("param_test")
        def handler(a, b, c=None):
            received_args.extend([a, b, c])
        
        asyncio.run(self.dispatcher.emit("param_test", "arg1", "arg2", c="arg3"))
        
        assert received_args == ["arg1", "arg2", "arg3"]


if __name__ == "__main__":
    pytest.main([__file__])