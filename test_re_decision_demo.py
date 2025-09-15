#!/usr/bin/env python3
"""
正则表达式和决策树功能演示
展示 @re_on 装饰器和 ReTaskScheduler 的完整用法
"""

import asyncio
import re
from decorators.on import re_on, command_on, on
from nucleus.dispatcher import ReTaskScheduler, DecisionCommandDispatcher, EventDispatcher

# 正则表达式任务示例
@re_on(
    name="greeting",
    content="用户问候",
    pattern=r"你好|您好|hi|hello|hey",
    priority=1
).execute()
def handle_greeting():
    """处理问候语"""
    return "你好！有什么可以帮助您的吗？"

@re_on(
    name="weather_query",
    content="天气查询",
    pattern=r".*天气.*",
    priority=2
).execute()
def handle_weather_query():
    """处理天气查询"""
    return "今天天气晴朗，温度25°C"

@re_on(
    name="math_calc",
    content="数学计算",
    pattern=r"\d+[+\-*/]\d+",
    priority=3
).execute()
def handle_math_calc():
    """处理数学计算"""
    return "我可以帮您计算数学表达式"

@re_on(
    name="email_pattern",
    content="邮箱匹配",
    pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    priority=4
).execute()
def handle_email_found():
    """发现邮箱地址"""
    return "检测到邮箱地址"

# 决策树命令示例
@command_on("help_command", "/help").execute()
def smart_help(args=None):
    """智能帮助命令"""
    return """🤖 智能助手命令列表：
/help - 显示帮助信息
/weather [城市] - 查询天气
/calc [表达式] - 数学计算"""

@command_on("weather_cmd", "/weather").execute()
def weather_command(args=None):
    """天气命令"""
    city = args[0] if args and len(args) > 0 else "北京"
    return f"🌤️ {city}天气：今天天气晴朗，温度25°C"

@command_on("calculate", "/calc").execute()
def calculate_command(args=None):
    """计算命令"""
    if not args:
        return "❌ 请提供计算表达式，例如：/calc 10*2+5"
    expr = " ".join(args)
    try:
        result = eval(expr)
        return f"🧮 计算结果：{expr} = {result}"
    except:
        return f"❌ 计算表达式错误：{expr}"

async def test_regex_features():
    """测试正则功能"""
    print("🔍 测试正则表达式功能...")
    
    scheduler = ReTaskScheduler()
    
    # 测试各种文本匹配
    test_cases = [
        "你好，请问今天天气如何？",
        "今天天气真不错！",
        "5+3等于多少？",
        "我的邮箱是user@example.com",
        "Hello World!",
        "您好，今天天气怎么样？",
        "计算：10*2+5",
        "联系邮箱：test@gmail.com"
    ]
    
    for text in test_cases:
        print(f"\n📄 测试文本：{text}")
        results = await scheduler.match_content(text)
        if results:
            for result in results:
                print(f"   ✅ 匹配成功：{result}")
        else:
            print("   ❌ 无匹配")

async def test_decision_tree():
    """测试决策树命令系统"""
    print("\n🌳 测试决策树命令系统...")
    
    dispatcher = DecisionCommandDispatcher()
    
    # 测试各种命令
    commands = [
        "/help",
        "/weather 上海",
        "/w 北京",
        "/calc 15*2+3",
        "/calc (10+5)*2",
        "/help me",
        "invalid_command",  # 无效命令
        "/weather"  # 不带参数
    ]
    
    for cmd in commands:
        print(f"\n⚡ 测试命令：{cmd}")
        result = await dispatcher.handle(cmd)
        print(f"   🎯 结果：{result}")

async def test_specific_regex():
    """测试特定正则任务触发"""
    print("\n🎯 测试特定正则任务触发...")
    
    scheduler = ReTaskScheduler()
    
    # 按名称触发特定任务
    test_cases = [
        ("greeting", "你好"),
        ("weather_query", "今天天气如何"),
        ("math_calc", "5+3"),
        ("email_pattern", "contact@company.com")
    ]
    
    for task_name, text in test_cases:
        print(f"\n📋 任务：{task_name}，文本：{text}")
        results = await scheduler.trigger(task_name, text)
        if results:
            for result in results:
                print(f"   ✅ 触发结果：{result}")
        else:
            print("   ❌ 未触发")

async def main():
    """主演示函数"""
    print("🚀 正则表达式和决策树功能演示")
    print("=" * 50)
    
    # 1. 测试正则表达式
    await test_regex_features()
    
    # 2. 测试决策树命令
    await test_decision_tree()
    
    # 3. 测试特定正则触发
    await test_specific_regex()
    
    print("\n✅ 演示完成！")

if __name__ == "__main__":
    asyncio.run(main())