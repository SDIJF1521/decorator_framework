#!/usr/bin/env python3
"""
装饰器框架基础使用示例
"""

import asyncio
from decorators.on import on
from nucleus.dispatcher import EventDispatcher

# 创建事件调度器
ed = EventDispatcher()

# 示例1：基本事件监听
@on("user_login")
def handle_user_login(username: str):
    """处理用户登录事件"""
    print(f"用户 {username} 登录成功")

# 示例2：异步事件处理
@on("data_processing")
async def process_data_async(data: dict):
    """异步处理数据"""
    print(f"开始处理数据: {data}")
    await asyncio.sleep(1)  # 模拟耗时操作
    print("数据处理完成")

# 示例3：带参数的事件
@on("order_created")
def handle_order(order_id: str, amount: float):
    """处理订单创建"""
    print(f"新订单: {order_id}, 金额: ${amount}")

# 示例4：错误处理
@on("error_occurred")
def handle_error(error: Exception):
    """全局错误处理"""
    print(f"发生错误: {error}")

async def main():
    """主函数示例"""
    print("=== 装饰器框架使用示例 ===")
    
    # 触发事件
    await ed.emit("user_login", "alice")
    await ed.emit("order_created", "order_123", 99.99)
    await ed.emit("data_processing", {"key": "value"})
    
    # 等待事件处理完成
    await asyncio.sleep(2)
    
    print("=== 示例完成 ===")

if __name__ == "__main__":
    asyncio.run(main())