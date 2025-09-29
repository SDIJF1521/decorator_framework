#!/usr/bin/env python3
"""
测试文档中的错误示例
验证文档中提到的错误用法是否确实存在
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleus.core.integration import enable_framework_integration, service
from decorators import on

# 启用框架集成
enable_framework_integration()

print("=== 测试文档中提到的错误用法 ===")

# 测试1: 服务装饰器错误用法（文档说不需要.execute()）
print("\n1. 测试服务装饰器 - 文档说不需要.execute()")
try:
    @service('singleton')  # 文档说不需要.execute()
    class TestService:
        def test_method(self):
            return "测试成功"
    
    # 尝试使用服务
    # 注意：服务装饰器实际上不需要.execute()，文档是正确的
    print("✅ 服务装饰器不需要.execute() - 文档正确")
except Exception as e:
    print(f"❌ 服务装饰器错误: {e}")

# 测试2: 事件装饰器错误用法（文档说必须需要.execute()）
print("\n2. 测试事件装饰器错误用法 - 文档说必须需要.execute()")

# ❌ 错误用法 - 缺少.execute()（文档说这样会注册失败）
try:
    @on("test_event")  # 没有.execute()
    def bad_handler():
        pass
    print("❌ 事件装饰器没有.execute()也应该失败 - 但似乎成功了？")
except Exception as e:
    print(f"✅ 事件装饰器没有.execute()失败: {e}")

# ✅ 正确用法 - 使用.execute()
try:
    @on("test_event").execute()
    def good_handler():
        print("事件处理成功")
    print("✅ 事件装饰器使用.execute()成功")
except Exception as e:
    print(f"❌ 事件装饰器使用.execute()失败: {e}")

# 测试3: 验证事件触发
print("\n3. 测试事件触发")
from nucleus.dispatcher import EventDispatcher

dispatcher = EventDispatcher()

async def test_events():
    try:
        # 触发事件
        await dispatcher.trigger_event("test_event")
        print("✅ 事件触发成功")
    except Exception as e:
        print(f"❌ 事件触发失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_events())