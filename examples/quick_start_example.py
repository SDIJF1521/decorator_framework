"""
快速入门示例 - 5分钟上手框架
展示框架的核心功能和基本用法
"""
import asyncio
from typing import Optional

# 导入核心功能
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nucleus.core.integration import enable_framework_integration, service
from nucleus.core.di import DependencyContainer, ServiceLifetime
from nucleus.core import inject, get_task_manager

# 1. 定义服务接口
class IDataService:
    """数据服务接口"""
    
    async def get_data(self, key: str) -> str:
        """获取数据"""
        raise NotImplementedError


class ICacheService:
    """缓存服务接口"""
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """设置缓存"""
        raise NotImplementedError


# 2. 实现服务（使用@service装饰器注册）
@service('singleton')  # 注册为单例服务
class SimpleDataService(IDataService):
    """简单的数据服务实现"""
    
    def __init__(self):
        self.data_store = {
            "user:1": "张三",
            "user:2": "李四",
            "user:3": "王五",
            "config:app_name": "我的应用"
        }
    
    async def get_data(self, key: str) -> str:
        """获取数据"""
        await asyncio.sleep(0.1)  # 模拟网络延迟
        return self.data_store.get(key, "未知用户")


@service('singleton')
class SimpleCacheService(ICacheService):
    """简单的缓存服务实现"""
    
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        return self.cache.get(key)
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """设置缓存"""
        self.cache[key] = value


# 3. 创建业务服务（依赖注入）
@service('singleton')
class UserService:
    """用户服务"""
    
    def __init__(self, data_service: IDataService):
        """通过依赖注入获取数据服务"""
        self.data_service = data_service
    
    async def get_user_info(self, user_id: str) -> dict:
        """获取用户信息（使用调用链包装）"""
        # 获取用户数据
        user_name = await self.data_service.get_data(f"user:{user_id}")
        app_name = await self.data_service.get_data("config:app_name")
        
        return {
            "user_id": user_id,
            "user_name": user_name,
            "app_name": app_name,
            "timestamp": "2024-01-01 12:00:00"
        }


# 4. 异步任务示例
async def data_processing_task(data: str) -> str:
    """数据处理任务"""
    # 步骤1: 数据验证
    if not data:
        raise ValueError("数据不能为空")
    
    # 步骤2: 数据处理
    processed_data = data.upper()
    
    # 步骤3: 结果返回
    return f"处理结果: {processed_data}"

async def simple_async_task(task_name: str, delay: float) -> str:
    """简单的异步任务"""
    print(f"🚀 启动任务: {task_name} (预计耗时: {delay}s)")
    
    await asyncio.sleep(delay)
    
    result = f"✅ 任务完成: {task_name}"
    print(result)
    return result


# 5. 主演示函数
async def main():
    """主函数"""
    print("🚀 框架快速入门演示")
    print("=" * 50)
    
    # 步骤1: 启用框架集成
    enable_framework_integration()
    print("✅ 框架集成已启用")
    
    # 步骤2: 获取依赖注入容器
    container = get_dependency_container()
    print("📦 依赖注入容器已获取")
    
    # 步骤3: 解析基础服务（@service装饰器已自动注册）
    data_service = container.resolve(IDataService)
    cache_service = container.resolve(ICacheService)
    print("✅ 基础服务已解析")
    
    # 步骤4: 解析用户服务
    try:
        user_service = container.resolve(UserService)
        print("✅ 用户服务已解析")
    except ValueError:
        # 如果服务未注册，手动注册
        from nucleus.core.integration import get_framework_integration
        integration = get_framework_integration()
        integration.register_service(UserService, lifetime='singleton')
        user_service = container.resolve(UserService)
        print("✅ 用户服务已手动注册并解析")
    
    # 步骤5: 异步任务演示
    print("\n=== 异步任务演示 ===")
    task_result = await data_processing_task("hello world")
    print(f"异步任务结果: {task_result}")
    
    # 步骤6: 使用服务
    print("\n📋 测试数据服务:")
    user_name = await data_service.get_data("user:1")
    print(f"用户1名称: {user_name}")
    
    # 步骤7: 使用业务服务（自动依赖注入）
    print("\n📋 测试用户服务:")
    user_info = await user_service.get_user_info("1")
    print(f"用户信息: {user_info}")
    
    # 步骤8: 使用任务管理器
    print("\n⚡ 测试任务管理器:")
    task_manager = get_task_manager()
    
    # 创建多个并发任务
    task_ids = []
    for i in range(3):
        task_id = task_manager.create_task(
            simple_async_task(f"任务-{i+1}", 0.5 + i * 0.2),
            name=f"快速任务-{i+1}"
        )
        task_ids.append(task_id)
        print(f"📝 创建任务: {task_id}")
    
    # 等待所有任务完成
    print("\n⏳ 等待所有任务完成...")
    results = []
    for task_id in task_ids:
        try:
            result = await task_manager.wait_for_task_async(task_id, timeout=3.0)
            results.append(result)
        except asyncio.TimeoutError:
            print(f"⏰ 任务超时: {task_id}")
        except Exception as e:
            print(f"❌ 任务失败: {task_id}, 错误: {e}")
    
    print(f"\n✅ 任务完成统计: {len(results)}/{len(task_ids)}")
    
    # 步骤9: 查看统计信息
    stats = task_manager.get_statistics()
    print(f"📊 任务统计: {stats}")
    
    print("\n🎉 快速入门演示完成！")
    print("\n💡 提示:")
    print("• 使用 @service 装饰器注册服务")
    print("• 使用 @task_with_chain 装饰器创建调用链任务")
    print("• 使用 get_task_manager() 获取任务管理器")
    print("• 使用 container.resolve() 解析依赖")


# 6. 辅助函数（简化访问）
def get_dependency_container():
    """获取依赖注入容器"""
    from nucleus.core import get_dependency_container as get_container
    return get_container()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())