#!/usr/bin/env python3
"""
正确的装饰器框架快速入门示例
完全基于实际的 production_final.py 和 decorators/on.py
"""

import asyncio
import logging
from datetime import datetime
import sys
import os
import re

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志 - 与 production_final.py 相同
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quick_start.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("装饰器框架快速入门")
print("=" * 50)

# 导入正确的模块 - 与 production_final.py 完全一致
from decorators.on import on, time_on, command_on, re_on
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler

# =============================================================================
# 1. 事件处理器 - 使用正确的装饰器语法
# =============================================================================

@on("user_login").execute()
async def handle_user_login(user_data: dict):
    """处理用户登录事件"""
    logger.info(f"用户登录: {user_data.get('username')}")
    return f"欢迎 {user_data.get('username')}"

@on("user_registration").execute()
async def handle_user_registration(user_data: dict):
    """处理用户注册"""
    user_id = f"USER{hash(user_data.get('email', '')) % 1000:03d}"
    return f"用户注册成功: ID={user_id}, 邮箱={user_data.get('email')}"

# =============================================================================
# 2. 定时任务 - 使用正确的语法
# =============================================================================

@time_on("heartbeat", priority=1, interval=2).execute()
async def heartbeat_task():
    """心跳任务"""
    logger.info("💓 心跳检测...")
    return f"心跳正常 - {datetime.now().strftime('%H:%M:%S')}"

@time_on("system_check", priority=2, interval=5).execute()
async def system_check():
    """系统检查任务"""
    logger.info("🔍 系统检查...")
    return "系统运行正常"

# =============================================================================
# 3. 命令处理器 - 使用正确的语法
# =============================================================================

@command_on("hello", "/hello").execute()
async def hello_command(args=None):
    """问候命令"""
    name = args[0] if args else "世界"
    return f"你好, {name}!"

@command_on("time", "/time").execute()
async def time_command(args=None):
    """时间命令"""
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@command_on("status", "/status").execute()
async def status_command(args=None):
    """状态命令"""
    return "框架运行正常 ✅"

# =============================================================================
# 4. 正则表达式处理器 - 使用正确的语法
# =============================================================================

@re_on("error_detector", "content", re.compile(r"ERROR.*")).execute()
async def detect_errors(error_message: str) -> str:
    """错误检测正则处理器"""
    print(f"检测到错误: {error_message}")
    return f"已处理错误: {error_message}"

@re_on("order_pattern", "content", re.compile(r"Order.*Completed")).execute()
async def detect_success(order_message: str) -> str:
    """成功订单检测正则处理器"""
    print(f"检测到成功订单: {order_message}")
    return f"已处理订单: {order_message}"

# =============================================================================
# 5. 演示函数 - 完全复制 production_final.py 的模式
# =============================================================================

async def run_quick_demo():
    """快速演示 - 完全基于 production_final.py"""
    
    print("\n[1] 事件系统演示")
    print("-" * 30)
    
    # 事件处理演示
    event_dispatcher = EventDispatcher()
    
    await event_dispatcher.trigger_event("user_login", {
        "username": "alice",
        "user_id": "U001"
    })
    
    await event_dispatcher.trigger_event("user_registration", {
        "email": "demo@example.com",
        "username": "demo_user"
    })
    
    print("\n[2] 命令系统演示")
    print("-" * 30)
    
    # 命令处理演示
    command_dispatcher = DecisionCommandDispatcher()
    
    health = await command_dispatcher.handle("/health")
    print(f"健康检查: {str(health)}")
    
    hello = await command_dispatcher.handle("/hello Alice")
    print(f"问候命令: {str(hello)}")
    
    time = await command_dispatcher.handle("/time")
    print(f"时间命令: {str(time)}")
    
    print("\n[3] 正则表达式演示")
    print("-" * 30)
    
    # 正则表达式演示
    await event_dispatcher.trigger_event("error_detector", "ERROR:database_connection_failed")
    await event_dispatcher.trigger_event("order_pattern", "Order12345Completed")
    
    print("\n[4] 定时任务演示")
    print("-" * 30)
    
    # 定时任务演示
    time_scheduler = TimeTaskScheduler()
    await time_scheduler.start()
    
    print("定时任务正在运行...")
    await asyncio.sleep(6)  # 让定时任务运行一段时间
    
    await time_scheduler.stop()
    print("定时任务已停止")
    
    print("\n✅ 快速入门演示完成!")
    print("\n框架功能总结:")
    print("- 事件驱动架构 (@on)")
    print("- 定时任务系统 (@time_on)")
    print("- 命令处理 (@command_on)")
    print("- 正则表达式匹配 (@re_on)")

async def main():
    """主函数"""
    try:
        await run_quick_demo()
    except Exception as e:
        logger.error(f"演示运行错误: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())