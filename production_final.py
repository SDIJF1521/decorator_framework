#!/usr/bin/env python3
"""
生产级装饰器框架最终演示
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decorators.on import on, time_on, command_on, re_on
from nucleus.dispatcher import *

# 配置生产级日志（避免编码问题）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_final.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("Production Decorator Framework Demo")
print("=" * 50)

# =============================================================================
# 1. 生产级事件处理
# =============================================================================

@on("user_registration").execute()
async def handle_user_registration(user_data: dict):
    """处理用户注册"""
    logger.info(f"Processing user registration: {user_data.get('email', 'unknown')}")
    
    # 模拟异步处理
    await asyncio.sleep(0.1)
    
    result = {
        "status": "success",
        "user_id": user_data.get("user_id"),
        "email": user_data.get("email")
    }
    
    logger.info(f"User registration completed: {result}")
    return result

@on("order_created").execute()
async def process_new_order(order_data: dict):
    """处理新订单"""
    logger.info(f"Processing new order: {order_data.get('order_id')} - ${order_data.get('amount', 0)}")
    
    await asyncio.sleep(0.2)
    logger.info(f"Order {order_data.get('order_id')} processed successfully")

# =============================================================================
# 2. 生产级定时任务
# =============================================================================

@time_on("system_monitor", priority=1, interval=3).execute()
async def monitor_system():
    """系统监控任务"""
    try:
        import psutil
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        logger.info(f"System Health: CPU={cpu}%, Memory={memory.percent}%")
        return {"cpu": cpu, "memory": memory.percent}
    except ImportError:
        logger.info("System monitoring: psutil not available")
        return {"status": "monitoring"}

@time_on("cleanup_task", priority=2, interval=5).execute()
async def cleanup_old_data():
    """数据清理任务"""
    logger.info("Starting data cleanup task...")
    await asyncio.sleep(1)
    logger.info("Data cleanup completed")

# =============================================================================
# 3. 生产级命令处理
# =============================================================================

@command_on("health", "/health").execute()
async def health_check(args=None):
    """健康检查命令"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "decorator_framework"
    }

@command_on("stats", "/stats").execute()
async def system_stats(args=None):
    """系统统计命令"""
    return {
        "total_users": 1000,
        "total_orders": 500,
        "uptime": "running",
        "version": "1.0.0"
    }

@command_on("trigger", "/trigger").execute()
async def trigger_task(args=None):
    """触发任务命令"""
    if not args:
        return {"error": "Usage: /trigger [backup|report]"}
    
    task = args[0]
    if task == "backup":
        return {"status": "success", "task": "backup", "message": "Backup started"}
    elif task == "report":
        return {"status": "success", "task": "report", "message": "Report generated"}
    else:
        return {"error": f"Unknown task: {task}"}

# =============================================================================
# 4. 生产级正则表达式处理
# =============================================================================

@re_on("error_detector", r"ERROR:\s*(\w+)", None, 1).execute()
async def detect_errors(match):
    """错误检测"""
    error_type = match.group(1)
    logger.error(f"System error detected: {error_type}")

@re_on("order_pattern", r"Order(\d+)Completed", None, 1).execute()
async def handle_order_completion(match):
    """订单完成处理"""
    order_id = match.group(1)
    logger.info(f"Order {order_id} completed successfully")

# =============================================================================
# 5. 生产级演示运行
# =============================================================================

async def run_production_demo():
    """完整的生产级演示"""
    
    print("\n[1] Event System Demo")
    print("-" * 30)
    
    # 事件处理演示
    event_dispatcher = EventDispatcher()
    
    await event_dispatcher.trigger_event("user_registration", {
        "user_id": "USER001",
        "email": "demo@example.com",
        "username": "demo_user"
    })
    
    await event_dispatcher.trigger_event("order_created", {
        "order_id": "ORD001",
        "amount": 99.99,
        "user_id": "USER001"
    })
    
    print("\n[2] Command System Demo")
    print("-" * 30)
    
    # 命令处理演示
    command_dispatcher = DecisionCommandDispatcher()
    
    health = await command_dispatcher.handle("/health")
    print(f"Health Check: {health}")
    
    stats = await command_dispatcher.handle("/stats")
    print(f"System Stats: {stats}")
    
    trigger = await command_dispatcher.handle("/trigger backup")
    print(f"Trigger Result: {trigger}")
    
    print("\n[3] Regex Pattern Demo")
    print("-" * 30)
    
    # 正则表达式演示
    re_dispatcher = ReTaskScheduler()
    
    await re_dispatcher.match_patterns("ERROR: database_connection")
    await re_dispatcher.match_patterns("Order12345Completed")
    
    print("\n[4] Scheduled Tasks Demo")
    print("-" * 30)
    
    # 定时任务演示
    time_scheduler = TimeTaskScheduler()
    time_scheduler.start()
    
    print("Scheduled tasks running...")
    await asyncio.sleep(7)  # 让定时任务运行一段时间
    
    time_scheduler.stop()
    print("Scheduled tasks stopped.")
    
    print("\n[5] Production Features Summary")
    print("-" * 40)
    print("✅ Event-driven architecture (@on)")
    print("✅ Scheduled task system (@time_on)")
    print("✅ Command processing (@command_on)")
    print("✅ Pattern matching (@re_on)")
    print("✅ Production logging")
    print("✅ Error handling")
    print("✅ Async/await support")

# =============================================================================
# 6. 生产级最佳实践总结
# =============================================================================

def print_best_practices():
    """输出生产级最佳实践"""
    practices = [
        "1. 使用生产级日志配置",
        "2. 实现完整的错误处理",
        "3. 使用异步处理提高性能",
        "4. 添加监控和告警",
        "5. 实现任务重试机制",
        "6. 使用连接池管理资源",
        "7. 添加健康检查端点",
        "8. 实现优雅关闭",
        "9. 使用配置管理",
        "10. 添加性能监控"
    ]
    
    print("\nProduction Best Practices:")
    print("=" * 40)
    for practice in practices:
        print(f"  {practice}")

async def main():
    """主函数"""
    try:
        await run_production_demo()
        print_best_practices()
        
        print("\n" + "=" * 50)
        print("Production Demo Completed Successfully!")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())