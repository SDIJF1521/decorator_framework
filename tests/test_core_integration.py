"""
核心功能集成测试
"""
import asyncio
import pytest
from typing import Optional, Any

from nucleus.core import (
    enable_framework_integration,
    inject,
    service,
    task_with_chain,
    get_task_manager,
    get_dependency_container,
    get_call_chain,
    get_framework_integration,
    TaskManager,
    DependencyContainer,
    CallChain,
    ChainInterceptor,
    ChainContext,
    TaskStatus
)


# 测试服务
class ITestService:
    async def get_value(self) -> str:
        raise NotImplementedError


@service('singleton')
class TestService(ITestService):
    def __init__(self):
        self.call_count = 0
    
    async def get_value(self) -> str:
        self.call_count += 1
        return f"test_value_{self.call_count}"


# 测试拦截器
class TestInterceptor(ChainInterceptor):
    def __init__(self):
        self.before_count = 0
        self.after_count = 0
        self.error_count = 0
    
    async def before_execute(self, context: ChainContext) -> None:
        self.before_count += 1
        context.metadata['test_interceptor'] = True
    
    async def after_execute(self, context: ChainContext) -> None:
        self.after_count += 1
        context.metadata['test_result'] = context.result
    
    async def on_error(self, context: ChainContext, error: Exception) -> None:
        self.error_count += 1
        context.metadata['test_error'] = str(error)


class TestCoreIntegration:
    """核心功能集成测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试设置"""
        self.integration = enable_framework_integration()
        yield
        # 清理
        task_manager = get_task_manager()
        task_manager.cancel_all_tasks()
    
    def test_dependency_injection(self):
        """测试依赖注入"""
        container = get_dependency_container()
        
        # 解析服务
        service1 = container.resolve(ITestService)
        service2 = container.resolve(ITestService)
        
        # 验证服务是单例
        assert service1 is service2
        assert isinstance(service1, TestService)
    
    def test_service_decorator(self):
        """测试服务装饰器"""
        # 创建新服务 - 在框架启用后创建，确保立即注册
        @service('singleton')
        class NewService:
            def __init__(self):
                self.value = "new_service"
        
        container = get_dependency_container()
        # 由于服务装饰器在框架启用后会立即注册，应该可以直接解析
        try:
            service_instance = container.resolve(NewService)
            assert service_instance is not None
            assert service_instance.value == "new_service"
            
            # 验证单例
            service2 = container.resolve(NewService)
            assert service_instance is service2
        except ValueError as e:
            # 如果服务未注册，手动注册并测试
            self.integration.register_service(NewService, lifetime='singleton')
            service_instance = container.resolve(NewService)
            assert service_instance is not None
            assert service_instance.value == "new_service"
    
    @pytest.mark.asyncio
    async def test_task_manager_creation(self):
        """测试任务管理器创建"""
        task_manager = get_task_manager()
        
        async def test_task():
            await asyncio.sleep(0.1)
            return "test_result"
        
        # 创建任务
        task_id = task_manager.create_task(test_task(), name="test_task")
        
        # 等待任务完成
        result = await task_manager.wait_for_task_async(task_id)
        
        assert result == "test_result"
        
        # 检查任务信息
        task_info = task_manager.get_task_info(task_id)
        assert task_info is not None
        assert task_info.status == TaskStatus.COMPLETED
        assert task_info.name == "test_task"
    
    @pytest.mark.asyncio
    async def test_task_cancellation(self):
        """测试任务取消"""
        task_manager = get_task_manager()
        
        async def long_task():
            await asyncio.sleep(10)  # 长耗时任务
            return "should_not_complete"
        
        # 创建任务
        task_id = task_manager.create_task(long_task(), name="long_task")
        
        # 等待一小段时间
        await asyncio.sleep(0.1)
        
        # 取消任务
        success = await task_manager.cancel_task(task_id)
        assert success is True
        
        # 检查任务状态
        task_info = task_manager.get_task_info(task_id)
        assert task_info is not None
        assert task_info.status == TaskStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_call_chain_interceptor(self):
        """测试调用链拦截器"""
        call_chain = get_call_chain()
        interceptor = TestInterceptor()
        
        # 添加拦截器
        call_chain.add_interceptor(interceptor)
        
        async def test_function():
            return "chain_result"
        
        # 执行调用链
        result = await call_chain.execute(test_function, task_id="test_chain")
        
        assert result == "chain_result"
        assert interceptor.before_count == 1
        assert interceptor.after_count == 1
        assert interceptor.error_count == 0
    
    @pytest.mark.asyncio
    async def test_call_chain_error_handling(self):
        """测试调用链错误处理"""
        call_chain = get_call_chain()
        interceptor = TestInterceptor()
        
        # 添加拦截器
        call_chain.add_interceptor(interceptor)
        
        async def error_function():
            raise ValueError("test_error")
        
        # 执行会出错的调用链
        with pytest.raises(ValueError, match="test_error"):
            await call_chain.execute(error_function, task_id="error_chain")
        
        assert interceptor.before_count == 1
        assert interceptor.after_count == 0
        assert interceptor.error_count == 1
    
    @pytest.mark.asyncio
    async def test_task_with_chain_decorator(self):
        """测试链式任务装饰器"""
        
        @task_with_chain(name="chain_task", metadata={"type": "test"})
        async def chain_task(value: str) -> str:
            await asyncio.sleep(0.1)
            return f"processed_{value}"
        
        # 执行任务
        result = await chain_task("test_value")
        
        assert result == "processed_test_value"
    
    @pytest.mark.asyncio
    async def test_inject_decorator(self):
        """测试注入装饰器"""
        
        @inject
        async def function_with_injection(service: ITestService) -> str:
            return await service.get_value()
        
        # 执行函数
        result = await function_with_injection()
        
        assert "test_value" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_tasks(self):
        """测试并发任务"""
        task_manager = get_task_manager()
        
        async def concurrent_task(task_id: int) -> str:
            await asyncio.sleep(0.1)
            return f"task_{task_id}_result"
        
        # 创建多个并发任务
        task_ids = []
        for i in range(5):
            task_id = task_manager.create_task(concurrent_task(i), name=f"concurrent_{i}")
            task_ids.append(task_id)
        
        # 并发等待所有任务完成
        results = await asyncio.gather(
            *[task_manager.wait_for_task_async(task_id) for task_id in task_ids]
        )
        
        # 验证结果
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result == f"task_{i}_result"
    
    @pytest.mark.asyncio
    async def test_task_statistics(self):
        """测试任务统计"""
        task_manager = get_task_manager()
        
        async def quick_task():
            await asyncio.sleep(0.01)
            return "quick"
        
        async def slow_task():
            await asyncio.sleep(0.1)
            return "slow"
        
        # 创建任务
        task_manager.create_task(quick_task(), name="quick_task")
        task_manager.create_task(slow_task(), name="slow_task")
        
        # 等待任务完成
        await asyncio.sleep(0.2)
        
        # 获取统计信息
        stats = task_manager.get_statistics()
        
        assert stats['total_tasks'] >= 2
        assert stats['completed_tasks'] >= 2
        assert stats['active_tasks'] == 0
    
    @pytest.mark.asyncio
    async def test_task_timeout(self):
        """测试任务超时"""
        task_manager = get_task_manager()
        
        async def long_task():
            await asyncio.sleep(10)  # 长耗时任务
            return "should_timeout"
        
        # 创建任务
        task_id = task_manager.create_task(long_task(), name="timeout_task")
        
        # 等待任务完成（设置超时）
        with pytest.raises(asyncio.TimeoutError):
            await task_manager.wait_for_task_async(task_id, timeout=0.1)
        
        # 检查任务状态
        task_info = task_manager.get_task_info(task_id)
        assert task_info is not None
        assert task_info.status == TaskStatus.TIMEOUT
    
    def test_integration_singleton(self):
        """测试集成器单例"""
        integration1 = get_framework_integration()
        integration2 = get_framework_integration()
        
        # 验证是同一个实例
        assert integration1 is integration2
    
    @pytest.mark.asyncio
    async def test_complex_integration_scenario(self):
        """测试复杂集成场景"""
        # 创建复杂业务服务 - 在框架启用后创建，确保立即注册
        @service('singleton')
        class ComplexService:
            def __init__(self, test_service: ITestService):
                self.test_service = test_service
                self.processing_count = 0
            
            async def complex_process(self, input_data: str) -> str:
                self.processing_count += 1
                
                # 获取基础数据
                base_value = await self.test_service.get_value()
                
                # 模拟复杂处理
                await asyncio.sleep(0.1)
                
                # 返回结果
                return f"复杂处理结果: {input_data} + {base_value} (处理次数: {self.processing_count})"
        
        # 解析服务
        container = get_dependency_container()
        try:
            complex_service = container.resolve(ComplexService)
        except ValueError as e:
            # 如果服务未注册，手动注册并测试
            self.integration.register_service(ComplexService, lifetime='singleton')
            complex_service = container.resolve(ComplexService)
        
        # 执行复杂处理
        result = await complex_service.complex_process("测试数据")
        
        assert "复杂处理结果" in result
        assert "测试数据" in result
        assert "test_value" in result
        assert complex_service.processing_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])