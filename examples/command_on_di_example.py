#!/usr/bin/env python3
"""
command_on装饰器依赖注入示例
演示如何在命令处理中使用依赖注入和调用链功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nucleus.core import enable_framework_integration, service
from nucleus.dispatcher import DecisionCommandDispatcher
from decorators.on import command_on

# 定义服务接口和实现
class IDataService:
    """数据服务接口"""
    async def get_data(self, key: str) -> str:
        raise NotImplementedError

class SimpleDataService(IDataService):
    """简单的数据服务实现"""
    def __init__(self):
        self.data = {
            "user": "张三",
            "status": "活跃",
            "level": "高级"
        }
    
    async def get_data(self, key: str) -> str:
        """获取数据"""
        await asyncio.sleep(0.1)  # 模拟异步操作
        return self.data.get(key, f"未找到键: {key}")

class ICacheService:
    """缓存服务接口"""
    async def get(self, key: str) -> str:
        raise NotImplementedError
    
    async def set(self, key: str, value: str) -> None:
        raise NotImplementedError

class SimpleCacheService(ICacheService):
    """简单的缓存服务实现"""
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str) -> str:
        """获取缓存"""
        await asyncio.sleep(0.05)
        return self.cache.get(key)
    
    async def set(self, key: str, value: str) -> None:
        """设置缓存"""
        await asyncio.sleep(0.05)
        self.cache[key] = value

# 使用service装饰器注册服务
@service(IDataService)
class DataService(IDataService):
    """数据服务实现"""
    def __init__(self):
        self.data = {
            "user": "李四",
            "status": "在线",
            "level": "VIP"
        }
    
    async def get_data(self, key: str) -> str:
        """获取数据"""
        await asyncio.sleep(0.1)
        return self.data.get(key, f"未找到键: {key}")

@service(ICacheService)
class CacheService(ICacheService):
    """缓存服务实现"""
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str) -> str:
        """获取缓存"""
        await asyncio.sleep(0.05)
        return self.cache.get(key)
    
    async def set(self, key: str, value: str) -> None:
        """设置缓存"""
        await asyncio.sleep(0.05)
        self.cache[key] = value

# 使用command_on装饰器注册命令处理函数
@command_on("user_info", "/user", aliases=["/用户信息"], cooldown=2).execute()
async def handle_user_info(data_service: IDataService, cache_service: ICacheService, args: list = None) -> str:
    """处理用户信息查询命令"""
    if args is None:
        args = []
    args_str = " ".join(args) if args else ""
    print(f"📋 执行用户信息查询命令，参数: {args_str}")
    
    # 尝试从缓存获取
    cache_key = f"user_info_{args_str or 'default'}"
    cached_result = await cache_service.get(cache_key)
    
    if cached_result:
        print(f"💾 从缓存获取数据: {cached_result}")
        return f"用户信息 (缓存): {cached_result}"
    
    # 从数据服务获取
    user_data = await data_service.get_data("user")
    status_data = await data_service.get_data("status")
    
    result = f"用户: {user_data}, 状态: {status_data}"
    
    # 缓存结果
    await cache_service.set(cache_key, result)
    print(f"💾 缓存用户信息: {result}")
    
    return f"用户信息: {result}"

@command_on("data_query", "/data", aliases=["/数据"], cooldown=1).execute()
async def handle_data_query(data_service: IDataService, args: list = None):
    """处理数据查询命令"""
    if args is None:
        args = []
    args_str = " ".join(args) if args else ""
    print(f"📊 执行数据查询命令，参数: {args_str}")
    
    key = args_str.strip() or "user"
    result = await data_service.get_data(key)
    
    return f"查询结果: {result}"

@command_on("help", "/help", aliases=["/帮助", "/?"]).execute()
async def handle_help(args: list = None):
    """处理帮助命令"""
    return """🔧 可用命令:
/user 或 /用户信息 - 查询用户信息
/data <key> 或 /数据 <key> - 查询数据
/help 或 /帮助 或 /? - 显示帮助信息"""

async def main():
    """主函数"""
    print("🚀 启动 command_on 依赖注入示例...")
    
    # 启用框架集成
    enable_framework_integration()
    print("✅ 框架集成已启用")
    
    # 创建命令调度器
    dispatcher = DecisionCommandDispatcher()
    print("✅ 命令调度器已创建")
    
    # 测试命令处理
    test_commands = [
        "/user",
        "/用户信息",
        "/data user",
        "/数据 status",
        "/data level",
        "/help",
        "/?",
        "/user",  # 测试缓存
        "/data nonexistent"
    ]
    
    print("\n🧪 测试命令处理:")
    for cmd in test_commands:
        print(f"\n📤 发送命令: {cmd}")
        try:
            result = await dispatcher.handle(cmd, priority=1)
            print(f"📥 响应: {result}")
        except Exception as e:
            print(f"❌ 命令处理失败: {e}")
        
        # 短暂延迟，避免过快执行
        await asyncio.sleep(0.5)
    
    # 测试冷却时间
    print("\n⏱️  测试冷却时间:")
    for i in range(3):
        print(f"\n第{i+1}次执行 /user 命令:")
        result = await dispatcher.handle("/user", priority=1)
        print(f"📥 响应: {result}")
        await asyncio.sleep(0.8)  # 小于冷却时间2秒
    
    print("\n🎉 command_on 依赖注入示例完成！")

if __name__ == "__main__":
    asyncio.run(main())