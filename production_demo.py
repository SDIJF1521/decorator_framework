#!/usr/bin/env python3
"""
生产级装饰器框架演示
展示如何在实际生产环境中使用所有功能
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

# 配置生产级日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("🚀 生产级装饰器框架演示开始")
print("=" * 60)

# =============================================================================
# 1. 生产级事件处理系统
# =============================================================================

@on("user_registration").execute()
async def handle_user_registration(user_data: dict):
    """处理用户注册 - 生产级实现"""
    start_time = datetime.now()
    
    try:
        logger.info(f"📝 开始处理用户注册: {user_data.get('email', 'unknown')}")
        
        # 模拟异步数据库写入
        await asyncio.sleep(0.1)
        
        # 模拟发送欢迎邮件
        await asyncio.sleep(0.1)
        
        # 记录处理结果
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ 用户注册处理完成，耗时: {duration:.2f}秒")
        
        return {
            "status": "success",
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email")
        }
        
    except Exception as e:
        logger.error(f"❌ 用户注册处理失败: {e}")
        raise

@on("order_created").execute()
async def process_new_order(order_data: dict):
    """处理新订单 - 生产级实现"""
    logger.info(f"🛒 处理新订单: {order_data.get('order_id')} - ${order_data.get('amount', 0)}")
    
    # 模拟订单处理流程
    await asyncio.sleep(0.2)
    
    # 更新库存
    await asyncio.sleep(0.1)
    
    # 发送通知
    await asyncio.sleep(0.1)
    
    logger.info(f"✅ 订单 {order_data.get('order_id')} 处理完成")

# =============================================================================
# 2. 生产级定时任务系统
# =============================================================================

@time_on("daily_backup", priority=1, interval=5).execute()
async def daily_database_backup():
    """每日数据库备份 - 生产级实现"""
    logger.info("💾 开始每日数据库备份...")
    
    # 模拟备份过程
    await asyncio.sleep(1)
    
    backup_info = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "backup_size": "1.2GB",
        "duration": "45秒"
    }
    
    logger.info(f"✅ 备份完成: {backup_info}")
    return backup_info

@time_on("system_monitor", priority=2, interval=3).execute()
async def monitor_system_health():
    """系统健康监控 - 生产级实现"""
    import psutil
    
    # 获取系统指标
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_available_gb": memory.available / 1024 / 1024 / 1024
    }
    
    if cpu_percent > 80:
        logger.warning(f"⚠️ CPU使用率过高: {cpu_percent}%")
    
    logger.info(f"📊 系统健康: CPU={cpu_percent}%, 内存={memory.percent}%")
    return health_status

# =============================================================================
# 3. 生产级命令处理系统
# =============================================================================

@command_on("health_check", "/health").execute()
async def system_health_check(args=None):
    """系统健康检查命令"""
    try:
        import psutil
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": "running",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "active_processes": len(psutil.pids())
        }
        
        logger.info("🔍 健康检查请求")
        return health_data
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@command_on("get_stats", "/stats").execute()
async def get_system_stats(args=None):
    """获取系统统计信息"""
    stats = {
        "total_users": 12543,
        "total_orders": 8765,
        "revenue_today": 45678.90,
        "active_sessions": 234
    }
    
    logger.info("📈 系统统计信息请求")
    return stats

@command_on("manual_task", "/trigger").execute()
async def trigger_manual_task(args=None):
    """手动触发任务命令"""
    if not args:
        return {"error": "请提供任务类型: /trigger [backup|report|cleanup]"}
    
    task_type = args[0]
    
    if task_type == "backup":
        result = await daily_database_backup()
        return {"status": "success", "task": "backup", "result": result}
    elif task_type == "report":
        return {"status": "success", "task": "report", "data": "每日报告已生成"}
    else:
        return {"status": "error", "message": f"未知任务类型: {task_type}"}

# =============================================================================
# 4. 生产级正则表达式处理
# =============================================================================

@re_on("error_detector", r"ERROR:\s*(\w+)", None, 1).execute()
async def detect_system_errors(match):
    """检测系统错误"""
    error_type = match.group(1)
    logger.error(f"🚨 检测到系统错误: {error_type}")
    
    # 模拟告警
    logger.warning(f"📧 发送告警邮件: {error_type} 错误")

@re_on("order_pattern", r"订单(\d+)已支付", None, 1).execute()
async def handle_order_payment(match):
    """处理订单支付通知"""
    order_id = match.group(1)
    logger.info(f"💰 订单 {order_id} 支付成功")

@re_on("user_activity", r"用户(\w+)登录", None, 1).execute()
async def track_user_login(match):
    """跟踪用户登录活动"""
    username = match.group(1)
    logger.info(f"👤 用户 {username} 登录系统")

# =============================================================================
# 5. 生产级演示运行
# =============================================================================

async def production_demo():
    """完整的生产级演示"""
    
    print("\n📋 生产级功能演示")
    print("-" * 40)
    
    # 初始化调度器
    event_dispatcher = EventDispatcher()
    command_dispatcher = DecisionCommandDispatcher()
    time_scheduler = TimeTaskScheduler()
    re_scheduler = ReTaskScheduler()
    
    # 1. 演示事件处理
    print("\n1️⃣ 事件处理演示")
    print("-" * 20)
    
    await event_dispatcher.trigger_event("user_registration", {
        "user_id": "U001",
        "email": "user@example.com",
        "username": "production_user"
    })
    
    await event_dispatcher.trigger_event("order_created", {
        "order_id": "ORD-2024-001",
        "amount": 299.99,
        "user_id": "U001"
    })
    
    # 2. 演示命令处理
    print("\n2️⃣ 命令处理演示")
    print("-" * 20)
    
    health_result = await command_dispatcher.handle("/health")
    print(f"🏥 健康检查: {health_result}")
    
    stats_result = await command_dispatcher.handle("/stats")
    print(f"📊 系统统计: {stats_result}")
    
    trigger_result = await command_dispatcher.handle("/trigger backup")
    print(f"🎯 手动触发: {trigger_result}")
    
    # 3. 演示正则表达式匹配
    print("\n3️⃣ 正则表达式匹配演示")
    print("-" * 25)
    
    await re_scheduler.match_patterns("ERROR: database_connection")
    await re_scheduler.match_patterns("订单12345已支付")
    await re_scheduler.match_patterns("用户alice登录")
    
    # 4. 演示定时任务（快速演示）
    print("\n4️⃣ 定时任务演示")
    print("-" * 20)
    
    print("⏰ 启动定时任务调度器...")
    time_scheduler.start()
    
    # 让定时任务运行一小段时间
    await asyncio.sleep(6)
    
    print("⏹️  停止定时任务调度器...")
    time_scheduler.stop()
    
    print("\n✅ 生产级演示完成！")
    print("=" * 60)

# =============================================================================
# 6. 运行配置和监控
# =============================================================================

async def main():
    """主函数 - 运行完整的生产级演示"""
    
    print("🎯 装饰器框架生产级演示")
    print("=" * 60)
    print("演示功能包括:")
    print("  • 事件驱动架构 (@on)")
    print("  • 定时任务系统 (@time_on)")
    print("  • 命令处理系统 (@command_on)")
    print("  • 正则表达式处理 (@re_on)")
    print("  • 生产级日志和监控")
    print("=" * 60)
    
    try:
        await production_demo()
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"❌ 演示出错: {e}")
        logger.error(f"演示错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())