#!/usr/bin/env python3
"""
调试依赖注入问题
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.core.integration import enable_framework_integration, service, get_framework_integration
from nucleus.core.di import ServiceLifetime

# 1. 启用框架集成
framework = enable_framework_integration()

# 2. 定义服务接口和实现
class IDataService:
    async def get_user_name(self, user_id: str) -> str:
        raise NotImplementedError

@service(IDataService)  # 注册接口到实现的映射
class DataService(IDataService):
    def __init__(self):
        self.users = {"1": "张三", "2": "李四"}
    
    async def get_user_name(self, user_id: str) -> str:
        return self.users.get(user_id, "未知用户")

# 3. 定义业务服务（自动依赖注入）
@service()  # 使用默认单例生命周期
class UserService:
    def __init__(self, data_service: IDataService):
        self.data_service = data_service
    
    async def get_user_by_id(self, user_id: str):
        name = await self.data_service.get_user_name(user_id)
        return {"id": user_id, "name": name, "email": f"{name}@example.com"}
    
    async def greet_user(self, user_id: str) -> str:
        user_name = await self.data_service.get_user_name(user_id)
        return f"你好，{user_name}！"

# 4. 检查服务注册状态
print("=== 依赖注入调试信息 ===")
print(f"框架集成状态: {framework._integration_enabled}")

# 检查容器中的服务
descriptors = framework.container._services
print(f"已注册的服务数量: {len(descriptors)}")
for service_type, descriptor in descriptors.items():
    print(f"服务类型: {service_type.__name__}")
    print(f"  实现类型: {descriptor.implementation_type.__name__ if descriptor.implementation_type else 'None'}")
    print(f"  生命周期: {descriptor.lifetime}")
    print(f"  实例: {descriptor.instance is not None}")

# 5. 尝试解析服务
print("\n=== 服务解析测试 ===")
try:
    data_service = framework.container.resolve(IDataService)
    print(f"✅ 成功解析 IDataService: {type(data_service).__name__}")
except Exception as e:
    print(f"❌ 解析 IDataService 失败: {e}")

try:
    user_service = framework.container.resolve(UserService)
    print(f"✅ 成功解析 UserService: {type(user_service).__name__}")
except Exception as e:
    print(f"❌ 解析 UserService 失败: {e}")

# 6. 检查单例实例
print(f"\n单例实例数量: {len(framework.container._singletons)}")
for service_type, instance in framework.container._singletons.items():
    print(f"  {service_type.__name__}: {type(instance).__name__}")