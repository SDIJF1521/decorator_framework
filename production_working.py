#!/usr/bin/env python3
"""
生产级装饰器框架 - 完全可运行版本
"""

import asyncio
import logging
from datetime import datetime
import sys
import os
import json

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decorators.on import on, time_on, command_on, re_on
from nucleus.dispatcher import *

# 配置生产级日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_working.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("Production Decorator Framework - Working Demo")
print("=" * 60)

# =============================================================================
# 1. 生产级事件处理系统
# =============================================================================

@on("user_registration").execute()
async def handle_user_registration(user_data):
    """处理用户注册事件"""
    logger.info(f"Processing user registration: {user_data}")
    await asyncio.sleep(0.1)
    
    result = {
        "status": "success",
        "user_id": user_data.get("user_id"),
        "registered_at": datetime.now().isoformat()
    }
    
    logger.info(f"Registration completed: {result}")
    return result

@on("order_created").execute()
async def process_order(order_data):
    """处理订单创建事件"""
    logger.info(f"New order: {order_data}")
    await asyncio.sleep(0.1)
    logger.info(f"Order processed: {order_data.get('order_id')}")

# =============================================================================
# 2. 生产级定时任务系统
# =============================================================================

@time_on("heartbeat", priority=1, interval=2).execute()
async def heartbeat_task():
    """心跳任务"""
    logger.info(f"Heartbeat: {datetime.now().strftime('%H:%M:%S')}")

@time_on("cleanup", priority=2, interval=3).execute()
async def cleanup_task():
    """清理任务"""
    logger.info("Running cleanup task...")
    await asyncio.sleep(0.5)
    logger.info("Cleanup completed")

# =============================================================================
# 3. 生产级命令处理系统
# =============================================================================

@command_on("health", "/health").execute()
async def health_command(args=None):
    """健康检查命令"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

@command_on("info", "/info").execute()
async def info_command(args=None):
    """系统信息命令"""
    return {
        "service": "decorator_framework",
        "version": "2.0.0",
        "features": ["events", "scheduling", "commands", "patterns"]
    }

@command_on("echo", "/echo").execute()
async def echo_command(args=None):
    """回显命令"""
    if args:
        return {"response": f"Echo: {' '.join(args)}"}
    return {"response": "Echo: Hello World"}

# =============================================================================
# 4. 生产级正则表达式处理
# =============================================================================

@re_on("error_pattern", r"ERROR:\s*(\w+)", None, 1).execute()
async def handle_error_pattern(match):
    """处理错误模式"""
    error_type = match.group(1)
    logger.error(f"Detected error type: {error_type}")

@re_on("success_pattern", r"SUCCESS:\s*(\w+)", None, 1).execute()
async def handle_success_pattern(match):
    """处理成功模式"""
    success_type = match.group(1)
    logger.info(f"Detected success: {success_type}")

# =============================================================================
# 5. 生产级演示函数
# =============================================================================

async def demo_events():
    """演示事件系统"""
    print("\n[1] Event System Demo")
    print("-" * 30)
    
    dispatcher = EventDispatcher()
    
    # 触发用户注册事件
    await dispatcher.trigger_event("user_registration", {
        "user_id": "USER123",
        "email": "test@example.com",
        "username": "testuser"
    })
    
    # 触发订单事件
    await dispatcher.trigger_event("order_created", {
        "order_id": "ORD456",
        "amount": 299.99,
        "user_id": "USER123"
    })

async def demo_commands():
    """演示命令系统"""
    print("\n[2] Command System Demo")
    print("-" * 30)
    
    dispatcher = DecisionCommandDispatcher()
    
    # 测试各种命令
    commands = ["health", "info", "echo hello production"]
    
    for cmd in commands:
        try:
            result = await dispatcher.handle(cmd)
            print(f"Command '{cmd}' -> {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Command '{cmd}' failed: {e}")

async def demo_regex():
    """演示正则表达式处理"""
    print("\n[3] Regex Pattern Demo")
    print("-" * 30)
    
    dispatcher = ReTaskScheduler()
    
    # 测试正则匹配
    patterns = [
        "ERROR: database",
        "SUCCESS: payment",
        "ERROR: network",
        "SUCCESS: upload"
    ]
    
    for pattern in patterns:
        await dispatcher.match_patterns(pattern)

async def demo_scheduling():
    """演示定时任务"""
    print("\n[4] Scheduled Tasks Demo")
    print("-" * 30)
    
    scheduler = TimeTaskScheduler()
    scheduler.start()
    
    print("Running scheduled tasks for 5 seconds...")
    await asyncio.sleep(5)
    
    scheduler.stop()
    print("Scheduler stopped")

# =============================================================================
# 6. 生产级最佳实践
# =============================================================================

def print_production_guide():
    """输出生产级指南"""
    guide = {
        "architecture": [
            "事件驱动架构 (@on)",
            "定时任务系统 (@time_on)",
            "命令处理系统 (@command_on)",
            "正则表达式处理 (@re_on)"
        ],
        "features": [
            "异步处理支持",
            "优先级管理",
            "错误处理机制",
            "生产级日志",
            "可扩展架构"
        ],
        "deployment": [
            "Docker容器化",
            "Kubernetes部署",
            "环境变量配置",
            "监控集成",
            "健康检查"
        ]
    }
    
    print("\nProduction Deployment Guide:")
    print("=" * 40)
    
    for category, items in guide.items():
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"  ✓ {item}")

# =============================================================================
# 7. 主函数
# =============================================================================

async def main():
    """主演示函数"""
    try:
        print("Starting Production Framework Demo...")
        
        # 运行各个演示
        await demo_events()
        await demo_commands()
        await demo_regex()
        await demo_scheduling()
        
        # 输出生产指南
        print_production_guide()
        
        print("\n" + "=" * 60)
        print("Production Demo Completed Successfully!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())