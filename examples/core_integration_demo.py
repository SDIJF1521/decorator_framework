#!/usr/bin/env python3
"""
核心功能集成演示 - 调用链 + 依赖注入 + 任务管理 + 任务取消
"""
import asyncio
import time
import random
import sys
import os
from typing import Optional, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入核心功能
from nucleus.core.integration import enable_framework_integration, service, task_with_chain, get_task_manager, get_dependency_container, get_call_chain
from nucleus.core.chain import ChainInterceptor, ChainContext
from nucleus.core.task_manager import TaskCancellationToken


# 1. 定义服务接口和实现
class IDataService:
    """数据服务接口"""
    
    async def fetch_data(self, query: str) -> str:
        """获取数据"""
        raise NotImplementedError


@service('singleton')  # 注册为单例服务
class DataService(IDataService):
    """数据服务实现"""
    
    def __init__(self):
        self.call_count = 0
    
    async def fetch_data(self, query: str) -> str:
        """获取数据"""
        self.call_count += 1
        await asyncio.sleep(0.1)  # 模拟耗时操作
        return f"数据结果: {query} (调用次数: {self.call_count})"


class ICacheService:
    """缓存服务接口"""
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl: int = 60) -> None:
        """设置缓存"""
        raise NotImplementedError


@service('singleton')  # 注册为单例服务
class CacheService(ICacheService):
    """缓存服务实现"""
    
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        return self.cache.get(key)
    
    async def set(self, key: str, value: str, ttl: int = 60) -> None:
        """设置缓存"""
        self.cache[key] = value


# 2. 定义业务服务，使用依赖注入
@service('singleton')
class BusinessService:
    """业务服务"""
    
    def __init__(self, data_service: IDataService, cache_service: ICacheService):
        self.data_service = data_service
        self.cache_service = cache_service
        self.process_count = 0
    
    @task_with_chain(name="处理业务请求", metadata={"type": "business"})
    async def process_request(self, request_id: str, query: str) -> str:
        """处理业务请求"""
        # 检查缓存
        cached_result = await self.cache_service.get(f"request_{request_id}")
        if cached_result:
            return f"[缓存] {cached_result}"
        
        # 获取数据
        data = await self.data_service.fetch_data(query)
        
        # 模拟业务处理
        await asyncio.sleep(0.2)
        result = f"业务处理结果: {data}"
        
        # 缓存结果
        await self.cache_service.set(f"request_{request_id}", result, ttl=300)
        
        return result


# 3. 创建自定义调用链拦截器
class LoggingInterceptor(ChainInterceptor):
    """日志拦截器"""
    
    async def before_execute(self, context: ChainContext) -> None:
        print(f"📝 [调用链] 开始执行: {context.function_name} (ID: {context.chain_id})")
        context.metadata['start_time'] = time.time()
    
    async def after_execute(self, context: ChainContext) -> None:
        duration = time.time() - context.metadata.get('start_time', 0)
        print(f"✅ [调用链] 执行完成: {context.function_name} (耗时: {duration:.3f}s)")
    
    async def on_error(self, context: ChainContext, error: Exception) -> None:
        duration = time.time() - context.metadata.get('start_time', 0)
        print(f"❌ [调用链] 执行失败: {context.function_name} (耗时: {duration:.3f}s, 错误: {error})")


class MetricsInterceptor(ChainInterceptor):
    """指标拦截器"""
    
    def __init__(self):
        self.call_count = 0
        self.total_duration = 0.0
    
    async def before_execute(self, context: ChainContext) -> None:
        context.metadata['metrics_start'] = time.time()
    
    async def after_execute(self, context: ChainContext) -> None:
        duration = time.time() - context.metadata.get('metrics_start', 0)
        self.call_count += 1
        self.total_duration += duration
        
        avg_duration = self.total_duration / self.call_count
        print(f"📊 [指标] 调用统计: 总调用次数={self.call_count}, 平均耗时={avg_duration:.3f}s")


class CancellationInterceptor(ChainInterceptor):
    """取消拦截器"""
    
    def __init__(self):
        self.cancellation_tokens = {}
    
    async def before_execute(self, context: ChainContext) -> None:
        # 为每个调用创建取消令牌
        token = TaskCancellationToken()
        self.cancellation_tokens[context.chain_id] = token
        context.metadata['cancellation_token'] = token
        print(f"🚫 [取消] 创建取消令牌: {context.chain_id}")
    
    async def after_execute(self, context: ChainContext) -> None:
        # 执行完成后清理取消令牌
        if context.chain_id in self.cancellation_tokens:
            del self.cancellation_tokens[context.chain_id]
            print(f"🚫 [取消] 清理取消令牌: {context.chain_id}")
    
    def cancel_chain(self, chain_id: str) -> None:
        """取消调用链"""
        if chain_id in self.cancellation_tokens:
            self.cancellation_tokens[chain_id].cancel()
            print(f"🚫 [取消] 调用链已取消: {chain_id}")


# 4. 演示异步任务取消
async def cancellable_long_task(task_name: str, duration: int, cancellation_token: TaskCancellationToken) -> str:
    """可取消的长耗时任务"""
    print(f"⏳ [任务] 开始执行: {task_name} (预计耗时: {duration}s)")
    
    for i in range(duration):
        # 检查是否已取消
        cancellation_token.throw_if_cancelled()
        
        await asyncio.sleep(1)
        progress = (i + 1) / duration * 100
        print(f"⏳ [任务] {task_name} 进度: {progress:.1f}%")
    
    result = f"任务完成: {task_name}"
    print(f"✅ [任务] {result}")
    return result


async def demo_task_cancellation():
    """演示任务取消功能"""
    print("\n🔄 演示任务取消功能")
    print("=" * 50)
    
    task_manager = get_task_manager()
    
    # 创建可取消的任务
    async def long_task_wrapper():
        return await cancellable_long_task("长耗时任务", 10, TaskCancellationToken())
    
    # 启动任务
    task_id = task_manager.create_task(long_task_wrapper(), name="演示任务取消")
    print(f"📝 任务已创建: {task_id}")
    
    # 等待3秒后取消任务
    await asyncio.sleep(3)
    print(f"🚫 正在取消任务: {task_id}")
    
    success = await task_manager.cancel_task(task_id)
    print(f"✅ 任务取消成功: {success}")
    
    # 获取任务信息
    task_info = task_manager.get_task_info(task_id)
    if task_info:
        print(f"📋 任务状态: {task_info.status.value}")
        if task_info.error:
            print(f"❌ 任务错误: {task_info.error}")


async def demo_dependency_injection():
    """演示依赖注入功能"""
    print("\n🔄 演示依赖注入功能")
    print("=" * 50)
    
    # 获取依赖注入容器
    container = get_dependency_container()
    
    # 解析服务
    business_service = container.resolve(BusinessService)
    data_service = container.resolve(IDataService)
    cache_service = container.resolve(ICacheService)
    
    print(f"✅ 服务解析成功:")
    print(f"  - 业务服务: {type(business_service).__name__}")
    print(f"  - 数据服务: {type(data_service).__name__}")
    print(f"  - 缓存服务: {type(cache_service).__name__}")
    
    # 测试数据服务
    print("📝 测试数据服务:")
    data_result = await data_service.fetch_data("测试查询")
    print(f"✅ 数据结果: {data_result}")
    
    # 测试缓存服务
    print("\n📝 测试缓存服务:")
    await cache_service.set("test_key", "测试缓存值")
    cached_value = await cache_service.get("test_key")
    print(f"✅ 缓存值: {cached_value}")
    
    # 测试业务服务（使用依赖注入）
    print("\n📝 测试业务服务:")
    business_result = await business_service.process_request("req_001", "业务查询")
    print(f"✅ 业务结果: {business_result}")
    
    # 测试缓存命中
    print("\n📝 测试缓存命中:")
    cached_result = await business_service.process_request("req_001", "业务查询")
    print(f"✅ 缓存结果: {cached_result}")


async def demo_call_chain_interceptors():
    """演示调用链拦截器功能"""
    print("\n🔄 演示调用链拦截器功能")
    print("=" * 50)
    
    call_chain = get_call_chain()
    
    # 添加拦截器
    logging_interceptor = LoggingInterceptor()
    metrics_interceptor = MetricsInterceptor()
    cancellation_interceptor = CancellationInterceptor()
    
    call_chain.add_interceptor(logging_interceptor)
    call_chain.add_interceptor(metrics_interceptor)
    call_chain.add_interceptor(cancellation_interceptor)
    
    # 定义测试函数
    async def test_function(name: str, delay: float = 0.1) -> str:
        await asyncio.sleep(delay)
        return f"测试结果: {name}"
    
    # 通过调用链执行
    print("📝 执行调用链测试:")
    result = await call_chain.execute(test_function, "测试1", delay=0.2)
    print(f"✅ 调用链结果: {result}")
    
    # 再次执行以查看指标
    result2 = await call_chain.execute(test_function, "测试2", delay=0.1)
    print(f"✅ 第二次调用结果: {result2}")


async def demo_chained_tasks():
    """演示链式任务功能"""
    print("\n🔄 演示链式任务功能")
    print("=" * 50)
    
    # 定义链式任务
    @task_with_chain(name="数据处理任务链", metadata={"type": "data_processing"})
    async def data_processing_task(data_id: str) -> str:
        print(f"📊 处理数据: {data_id}")
        
        # 模拟数据处理步骤
        await asyncio.sleep(0.1)
        step1 = f"步骤1: 验证数据 {data_id}"
        print(f"✅ {step1}")
        
        await asyncio.sleep(0.1)
        step2 = f"步骤2: 转换数据 {data_id}"
        print(f"✅ {step2}")
        
        await asyncio.sleep(0.1)
        step3 = f"步骤3: 存储数据 {data_id}"
        print(f"✅ {step3}")
        
        return f"数据处理完成: {data_id}"
    
    # 执行链式任务
    print("📝 执行链式任务:")
    result = await data_processing_task("data_001")
    print(f"✅ 最终结果: {result}")
    
    # 获取任务管理器查看任务状态
    task_manager = get_task_manager()
    stats = task_manager.get_statistics()
    print(f"\n📊 任务统计: {stats}")


async def demo_concurrent_tasks():
    """演示并发任务功能"""
    print("\n🔄 演示并发任务功能")
    print("=" * 50)
    
    task_manager = get_task_manager()
    
    # 创建多个并发任务
    async def concurrent_task(task_id: int, duration: float) -> str:
        print(f"🚀 启动并发任务: {task_id} (持续时间: {duration}s)")
        await asyncio.sleep(duration)
        result = f"并发任务完成: {task_id}"
        print(f"✅ {result}")
        return result
    
    # 启动多个任务
    task_ids = []
    for i in range(5):
        duration = random.uniform(0.5, 2.0)
        task_id = task_manager.create_task(
            concurrent_task(i, duration),
            name=f"并发任务-{i}",
            metadata={"type": "concurrent", "duration": duration}
        )
        task_ids.append(task_id)
        print(f"📝 创建任务: {task_id}")
    
    # 等待所有任务完成
    print("⏳ 等待所有任务完成...")
    results = []
    for task_id in task_ids:
        try:
            result = await task_manager.wait_for_task_async(task_id, timeout=3.0)
            results.append(result)
        except asyncio.TimeoutError:
            print(f"⏰ 任务超时: {task_id}")
        except Exception as e:
            print(f"❌ 任务失败: {task_id}, 错误: {e}")
    
    print(f"\n✅ 所有任务完成，结果数量: {len(results)}")
    
    # 查看最终统计
    stats = task_manager.get_statistics()
    print(f"📊 最终任务统计: {stats}")


async def main():
    """主演示函数"""
    print("🚀 框架核心功能集成演示")
    print("=" * 60)
    
    # 启用框架集成
    integration = enable_framework_integration()
    print("✅ 框架集成已启用")
    
    # 手动注册服务以确保它们被正确注册
    container = get_dependency_container()
    
    # 注册数据服务
    container.register_singleton(IDataService, DataService)
    print("✅ 数据服务已注册")
    
    # 注册缓存服务
    container.register_singleton(ICacheService, CacheService)
    print("✅ 缓存服务已注册")
    
    # 注册业务服务
    container.register_singleton(BusinessService, BusinessService)
    print("✅ 业务服务已注册")
    
    try:
        # 演示1: 依赖注入
        await demo_dependency_injection()
        
        # 演示2: 调用链拦截器
        await demo_call_chain_interceptors()
        
        # 演示3: 链式任务
        await demo_chained_tasks()
        
        # 演示4: 并发任务
        await demo_concurrent_tasks()
        
        # 演示5: 任务取消
        await demo_task_cancellation()
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        print("\n🧹 清理资源...")
        task_manager = get_task_manager()
        cancelled = task_manager.cancel_all_tasks()
        print(f"✅ 已取消 {cancelled} 个活跃任务")
        
        stats = task_manager.get_statistics()
        print(f"📊 最终统计: {stats}")
        
        print("\n🎉 演示完成！")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())