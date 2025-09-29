#!/usr/bin/env python3
"""
调试框架启用问题
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 1. 先获取框架集成器，但不启用
from nucleus.core.integration import get_framework_integration, _pending_services

framework = get_framework_integration()
print(f"框架集成状态: {framework._integration_enabled}")
print(f"待处理服务数量: {len(_pending_services)}")

# 2. 启用框架集成
from nucleus.core.integration import enable_framework_integration

enabled_framework = enable_framework_integration()
print(f"启用后的框架集成状态: {enabled_framework._integration_enabled}")
print(f"待处理服务数量: {len(_pending_services)}")

# 3. 现在定义服务（框架已启用）
from nucleus.core.integration import service

class IDataService:
    async def get_user_name(self, user_id: str) -> str:
        raise NotImplementedError

print(f"定义 IDataService 前的待处理服务数量: {len(_pending_services)}")

@service(IDataService)  # 注册接口到实现的映射
class DataService(IDataService):
    def __init__(self):
        self.users = {"1": "张三", "2": "李四"}
    
    async def get_user_name(self, user_id: str) -> str:
        return self.users.get(user_id, "未知用户")

print(f"定义 DataService 后的待处理服务数量: {len(_pending_services)}")

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

print(f"定义 UserService 后的待处理服务数量: {len(_pending_services)}")

# 4. 检查服务注册状态
print("\n=== 服务注册状态 ===")
descriptors = enabled_framework.container._services
for service_type, descriptor in descriptors.items():
    if service_type.__name__ in ['UserService', 'IDataService', 'DataService']:
        print(f"服务: {service_type.__name__} -> {descriptor.implementation_type.__name__ if descriptor.implementation_type else 'None'}")

# 5. 测试解析
try:
    user_service = enabled_framework.container.resolve(UserService)
    print(f"✅ 成功解析 UserService: {type(user_service).__name__}")
except Exception as e:
    print(f"❌ 解析 UserService 失败: {e}")