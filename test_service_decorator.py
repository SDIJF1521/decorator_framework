#!/usr/bin/env python3
"""
调试服务装饰器问题
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.core.integration import enable_framework_integration, service, get_framework_integration

# 1. 启用框架集成
framework = enable_framework_integration()
print(f"框架启用状态: {framework._integration_enabled}")

# 2. 定义服务接口和实现
class IDataService:
    async def get_user_name(self, user_id: str) -> str:
        raise NotImplementedError

print(f"IDataService 基类: {IDataService.__bases__}")

@service(IDataService)  # 注册接口到实现的映射
class DataService(IDataService):
    def __init__(self):
        self.users = {"1": "张三", "2": "李四"}
    
    async def get_user_name(self, user_id: str) -> str:
        return self.users.get(user_id, "未知用户")

print(f"DataService 基类: {DataService.__bases__}")

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

print(f"UserService 基类: {UserService.__bases__}")
print(f"UserService 是否有非object基类: {hasattr(UserService, '__bases__') and UserService.__bases__ and UserService.__bases__[0] != object}")

# 4. 检查服务注册状态
print("\n=== 服务注册状态 ===")
descriptors = framework.container._services
for service_type, descriptor in descriptors.items():
    print(f"服务: {service_type.__name__} -> {descriptor.implementation_type.__name__ if descriptor.implementation_type else 'None'}")

# 5. 手动注册 UserService 进行测试
print("\n=== 手动注册 UserService ===")
from nucleus.core.di import ServiceLifetime
framework.container.register(UserService, lifetime=ServiceLifetime.SINGLETON)

# 再次检查
print("手动注册后的服务状态:")
for service_type, descriptor in framework.container._services.items():
    if service_type.__name__ in ['UserService', 'IDataService']:
        print(f"服务: {service_type.__name__} -> {descriptor.implementation_type.__name__ if descriptor.implementation_type else 'None'}")

# 6. 测试解析
try:
    user_service = framework.container.resolve(UserService)
    print(f"✅ 成功解析 UserService: {type(user_service).__name__}")
except Exception as e:
    print(f"❌ 解析 UserService 失败: {e}")