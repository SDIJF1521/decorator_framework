#!/usr/bin/env python3
"""
on装饰器依赖注入示例
演示如何在事件处理中使用依赖注入和调用链功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nucleus.core import enable_framework_integration, service
from nucleus.dispatcher import EventDispatcher
from decorators.on import on

# 定义服务接口和实现
class ILogService:
    """日志服务接口"""
    async def log(self, message: str, level: str = "INFO") -> None:
        raise NotImplementedError

class ConsoleLogService(ILogService):
    """控制台日志服务实现"""
    async def log(self, message: str, level: str = "INFO") -> None:
        """记录日志"""
        await asyncio.sleep(0.01)  # 模拟异步操作
        print(f"[{level}] {message}")

class IMetricsService:
    """指标服务接口"""
    async def increment(self, metric: str, value: int = 1) -> None:
        raise NotImplementedError
    
    async def get_count(self, metric: str) -> int:
        raise NotImplementedError

class SimpleMetricsService(IMetricsService):
    """简单的指标服务实现"""
    def __init__(self):
        self.metrics = {}
    
    async def increment(self, metric: str, value: int = 1) -> None:
        """增加指标"""
        await asyncio.sleep(0.01)
        if metric not in self.metrics:
            self.metrics[metric] = 0
        self.metrics[metric] += value
    
    async def get_count(self, metric: str) -> int:
        """获取指标计数"""
        await asyncio.sleep(0.01)
        return self.metrics.get(metric, 0)

# 使用service装饰器注册服务
@service(ILogService)
class LogService(ILogService):
    """日志服务实现"""
    async def log(self, message: str, level: str = "INFO") -> None:
        """记录日志"""
        await asyncio.sleep(0.01)
        print(f"📝 [{level}] {message}")

@service(IMetricsService)
class MetricsService(IMetricsService):
    """指标服务实现"""
    def __init__(self):
        self.metrics = {}
    
    async def increment(self, metric: str, value: int = 1) -> None:
        """增加指标"""
        await asyncio.sleep(0.01)
        if metric not in self.metrics:
            self.metrics[metric] = 0
        self.metrics[metric] += value
        print(f"📊 指标 {metric} 增加到: {self.metrics[metric]}")
    
    async def get_count(self, metric: str) -> int:
        """获取指标计数"""
        await asyncio.sleep(0.01)
        return self.metrics.get(metric, 0)

# 使用on装饰器注册事件处理函数
@on("user_login").execute()
async def handle_user_login(log_service: ILogService, metrics_service: IMetricsService, user_id: str, **kwargs):
    """处理用户登录事件"""
    print(f"事件处理中 - 指标服务实例ID: {id(metrics_service)}")
    print(f"事件处理中 - 指标服务类型: {type(metrics_service)}")
    # 立即检查指标数据
    current_count = await metrics_service.get_count("user_login_count")
    print(f"事件处理中 - 当前user_login_count: {current_count}")
    await log_service.log(f"用户 {user_id} 登录成功", "INFO")
    await metrics_service.increment("user_login_count")
    # 增加后立即检查
    new_count = await metrics_service.get_count("user_login_count")
    print(f"事件处理中 - 增加后user_login_count: {new_count}")
    print(f"🎉 处理用户登录事件: {user_id}")

@on("user_logout").execute()
async def handle_user_logout(log_service: ILogService, metrics_service: IMetricsService, user_id: str, **kwargs):
    """处理用户登出事件"""
    await log_service.log(f"用户 {user_id} 登出", "INFO")
    await metrics_service.increment("user_logout_count")
    print(f"👋 处理用户登出事件: {user_id}")

@on("data_processed").execute()
async def handle_data_processed(log_service: ILogService, metrics_service: IMetricsService, data_type: str, count: int, **kwargs):
    """处理数据处理完成事件"""
    await log_service.log(f"处理了 {count} 条 {data_type} 数据", "INFO")
    await metrics_service.increment(f"{data_type}_processed", count)
    print(f"📈 处理数据处理事件: {data_type} x{count}")

@on("system_error").execute()
async def handle_system_error(log_service: ILogService, error_code: str, error_message: str, **kwargs):
    """处理系统错误事件"""
    await log_service.log(f"系统错误 [{error_code}]: {error_message}", "ERROR")
    print(f"❌ 处理系统错误事件: {error_code} - {error_message}")

async def main():
    """主函数"""
    print("🚀 启动 on 装饰器依赖注入示例...")
    
    # 启用框架集成
    framework = enable_framework_integration()
    print("✅ 框架集成已启用")
    
    # 调试：检查服务注册状态
    container = framework.get_dependency_container()
    print(f"启用后容器中的服务: {list(container._services.keys())}")
    print(f"启用后单例缓存: {list(container._singletons.keys())}")
    
    # 检查具体的服务描述符
    for service_type in [ILogService, IMetricsService, LogService, MetricsService]:
        if service_type in container._services:
            descriptor = container._services[service_type]
            print(f"服务 {service_type.__name__}: lifetime={descriptor.lifetime}, implementation={descriptor.implementation_type}")
        else:
            print(f"服务 {service_type.__name__}: 未找到")
    
    # 检查待处理服务列表
    from nucleus.core.integration import _pending_services
    print(f"待处理服务数量: {len(_pending_services)}")
    
    # 创建事件调度器
    dispatcher = EventDispatcher()
    print("✅ 事件调度器已创建")
    
    # 测试事件处理
    test_events = [
        ("user_login", {"user_id": "user123", "ip": "192.168.1.1"}),
        ("user_logout", {"user_id": "user123"}),
        ("data_processed", {"data_type": "order", "count": 50}),
        ("system_error", {"error_code": "DB001", "error_message": "数据库连接超时"}),
        ("user_login", {"user_id": "user456", "ip": "192.168.1.2"}),
        ("data_processed", {"data_type": "user", "count": 10}),
    ]
    
    print("\n🧪 测试事件处理:")
    for event_name, event_data in test_events:
        print(f"\n📤 触发事件: {event_name}")
        try:
            # 触发事件
            await dispatcher.trigger_event(event_name, priority=5, **event_data)
            print(f"✅ 事件 {event_name} 已触发")
        except Exception as e:
            print(f"❌ 事件处理失败: {e}")
        
        # 短暂延迟，避免过快执行
        await asyncio.sleep(0.2)
    
    # 等待所有事件处理完成
    await asyncio.sleep(1)
    
    # 显示最终指标
    print("\n📊 最终指标统计:")
    # 从框架集成获取指标服务实例
    from nucleus.core import get_framework_integration
    framework = get_framework_integration()
    
    # 调试：检查容器中的服务
    container = framework.get_dependency_container()
    print(f"容器中的服务: {list(container._services.keys())}")
    
    # 检查服务描述符
    if IMetricsService in container._services:
        descriptor = container._services[IMetricsService]
        print(f"IMetricsService 服务描述符: lifetime={descriptor.lifetime}, implementation={descriptor.implementation_type}")
    
    # 检查单例缓存
    print(f"单例缓存: {list(container._singletons.keys())}")
    print(f"单例缓存内容: {container._singletons}")
    
    # 从接口解析服务
    print("正在解析 IMetricsService...")
    metrics_service = framework.resolve_service(IMetricsService)
    print(f"从接口解析的指标服务实例: {metrics_service}")
    print(f"从接口解析的指标服务实例ID: {id(metrics_service)}")
    
    # 再次检查单例缓存
    print(f"解析后单例缓存: {list(container._singletons.keys())}")
    print(f"解析后单例缓存内容: {container._singletons}")
    
    # 直接从单例缓存中获取服务进行对比
    if IMetricsService in container._singletons:
        cached_service = container._singletons[IMetricsService]
        print(f"缓存中的指标服务实例ID: {id(cached_service)}")
        print(f"缓存中的指标数据: {getattr(cached_service, 'metrics', {})}")
        print(f"解析的实例与缓存实例是否相同: {metrics_service is cached_service}")
    else:
        print("IMetricsService 不在单例缓存中！")
    
    # 使用解析的服务进行统计
    metrics = ["user_login_count", "user_logout_count", "order_processed", "user_processed"]
    for metric in metrics:
        count = await metrics_service.get_count(metric)
        print(f"  {metric}: {count}")
    
    print("\n🎉 on 装饰器依赖注入示例完成！")

if __name__ == "__main__":
    asyncio.run(main())