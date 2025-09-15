#!/usr/bin/env python3
"""
定时任务演示脚本
运行此脚本可以验证定时任务功能是否正常工作
"""

import asyncio
from decorators.on import time_on
from nucleus.dispatcher import TimeTaskScheduler

# 定义定时任务
@time_on("heartbeat", priority=1, interval=3).execute()
def heartbeat_task():
    """每3秒执行一次的心跳任务"""
    print("💓 心跳检测 - 系统运行正常")

@time_on("log_cleanup", priority=2, interval=5).execute()
def cleanup_logs():
    """每5秒清理一次日志"""
    print("🧹 清理日志文件...")

@time_on("data_backup", priority=3, interval=7).execute()
async def backup_data():
    """每7秒执行一次数据备份（异步函数）"""
    await asyncio.sleep(0.5)  # 模拟异步操作
    print("💾 数据备份完成")

async def main():
    """主函数：演示定时任务功能"""
    print("🚀 启动定时任务演示...")
    
    # 创建调度器
    scheduler = TimeTaskScheduler()
    
    # 启动调度器
    await scheduler.start()
    
    # 运行20秒观察效果
    print("⏰ 运行20秒观察定时任务...")
    await asyncio.sleep(20)
    
    # 停止调度器
    await scheduler.stop()
    print("✅ 演示结束")

if __name__ == "__main__":
    asyncio.run(main())