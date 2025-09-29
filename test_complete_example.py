#!/usr/bin/env python3
"""
测试README.md中的完整示例是否能正常运行
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.core.integration import enable_framework_integration, service, inject
from decorators import on, command_on
from nucleus.dispatcher import EventDispatcher

# 1. 启用框架集成（必须先调用）
framework = enable_framework_integration()

# 注册服务到依赖注入容器
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
@service('singleton')
class UserService:
    def __init__(self, data_service: IDataService):
        self.data_service = data_service
    
    async def get_user_by_id(self, user_id: str):
        name = await self.data_service.get_user_name(user_id)
        return {"id": user_id, "name": name, "email": f"{name}@example.com"}
    
    async def greet_user(self, user_id: str) -> str:
        user_name = await self.data_service.get_user_name(user_id)
        return f"你好，{user_name}！"

# 4. 事件处理（使用依赖注入）
@on("user_login").execute()
async def handle_user_login(user_service: UserService, user_id: str, **kwargs):
    ip = kwargs.get("ip", "未知IP")
    greeting = await user_service.greet_user(user_id)
    print(f"🎉 {greeting} (来自IP: {ip})")

# 5. 命令处理
@command_on("greet", "/greet").execute()
async def handle_greet_command(user_service: UserService, args: list = None):
    """处理问候命令"""
    # 从参数解析用户ID
    if args is None:
        args = []
    user_id = args[0] if args else "1"
    user = await user_service.get_user_by_id(user_id)
    return f"你好，{user['name']}！"

# 6. 主演示函数
async def main():
    print("🚀 装饰器框架演示开始...")
    
    # 通过依赖注入容器获取服务实例
    data_service = DataService()
    user_service = UserService(data_service)
    
    # 测试业务逻辑
    greeting = await user_service.greet_user("1")
    print(f"业务测试: {greeting}")
    
    # 测试事件系统
    dispatcher = EventDispatcher()
    await dispatcher.trigger_event("user_login", user_id="1", ip="192.168.1.100", priority=5)
    
    # 测试命令系统
    from nucleus.dispatcher import DecisionCommandDispatcher
    cmd_dispatcher = DecisionCommandDispatcher()
    result = await cmd_dispatcher.handle("/greet 2")
    print(f"命令结果: {result}")
    
    # 等待命令执行完成
    await asyncio.sleep(2)
    print("等待命令执行完成...")
    
    print("\n✅ 演示完成！")

if __name__ == "__main__":
    asyncio.run(main())