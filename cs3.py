import asyncio
from decorators.on import time_on
from nucleus.dispatcher import TimeTaskScheduler

@time_on("backup", priority=1, interval=3600).execute()
async def auto_backup():
    """每小时自动备份"""
    print("执行数据备份...")
    # 备份逻辑

# 启动调度器
scheduler = TimeTaskScheduler()
asyncio.run(scheduler.start())