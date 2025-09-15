#!/usr/bin/env python3
"""
装饰器框架快速入门示例
基于实际的 production_final.py 和 decorators/on.py 结构
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入框架
from decorators.on import on, time_on, command_on, re_on
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher
from nucleus.scheduler import TimeTaskScheduler, ReTaskScheduler

class QuickStartFramework:
    """快速入门框架"""
    
    def __init__(self):
        self.event_dispatcher = EventDispatcher()
        self.command_dispatcher = DecisionCommandDispatcher()
        self.time_scheduler = TimeTaskScheduler()
    
    async def start(self):
        """启动框架"""
        logger.info("🚀 启动快速入门框架...")
        await self.time_scheduler.start()
        
    async def stop(self):
        """停止框架"""
        logger.info("🛑 停止框架...")
        await self.time_scheduler.stop()
    
    async def demo(self):
        """运行演示"""
        await self.start()
        
        try:
            # 1. 演示事件系统
            logger.info("📢 演示事件系统...")
            await self.event_dispatcher.trigger_event("user_login", {
                "username": "alice",
                "user_id": "U001"
            })
            
            # 2. 演示命令系统
            logger.info("⚡ 演示命令系统...")
            result = await self.command_dispatcher.handle("/hello")
            logger.info(f"命令结果: {result}")
            
            # 3. 演示正则表达式
            logger.info("🔍 演示正则表达式...")
            re_scheduler = ReTaskScheduler()
            await re_scheduler.match_content("ERROR:database_connection_failed")
            await re_scheduler.match_content("Order12345Completed")
            
            # 等待定时任务执行
            await asyncio.sleep(5)
            
        finally:
            await self.stop()

# ===== 定义事件处理器 =====

@on("user_login").execute()
async def handle_user_login(user_data):
    """处理用户登录事件"""
    logger.info(f"用户 {user_data['username']} 登录成功")
    return f"欢迎 {user_data['username']}"

@on("user_registration").execute()
async def handle_user_registration(user_data):
    """处理用户注册事件"""
    logger.info(f"新用户注册: {user_data['email']}")
    return f"用户注册成功: {user_data['email']}"

# ===== 定义定时任务 =====

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

# ===== 定义命令处理器 =====

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

# ===== 定义正则表达式处理器 =====

@re_on("error_detector", r"ERROR:(\w+)", None, 1).execute()
async def detect_errors(match):
    """错误检测"""
    error_type = match.group(1)
    logger.error(f"检测到错误: {error_type}")
    return f"错误类型: {error_type}"

@re_on("success_detector", r"SUCCESS:(\w+)", None, 1).execute()
async def detect_success(match):
    """成功检测"""
    success_type = match.group(1)
    logger.info(f"操作成功: {success_type}")
    return f"成功类型: {success_type}"

async def main():
    """主函数"""
    print("🎉 装饰器框架快速入门")
    print("=" * 50)
    
    framework = QuickStartFramework()
    await framework.demo()
    
    print("\n✅ 快速入门演示完成!")
    print("\n可用命令:")
    print("  /hello [name] - 问候")
    print("  /time - 显示当前时间")
    print("  /status - 检查状态")

if __name__ == "__main__":
    asyncio.run(main())