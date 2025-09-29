#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装饰器框架完整使用案例演示
展示所有核心功能和高级用法
"""

import asyncio
import re
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

# 导入框架核心组件
from decorators.on import on, command_on, time_on, re_on
from nucleus.dispatcher import (
    EventDispatcher, 
    DecisionCommandDispatcher, 
    TimeTaskScheduler, 
    ReTaskScheduler
)
from nucleus.data.priority_queue import PriorityQueue
from nucleus.Myclass import ClassNucleus

# ==========================================
# 1. 基础事件处理示例
# ==========================================

@on("user_login").execute()
def handle_user_login(username: str, ip_address: str = "unknown") -> str:
    """用户登录事件 - 同步处理"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] 👋 用户 '{username}' 从 {ip_address} 登录成功"

@on("user_logout").execute()
async def handle_user_logout(username: str, session_duration: int) -> str:
    """用户登出事件 - 异步处理"""
    await asyncio.sleep(0.1)  # 模拟异步数据库操作
    return f"🚪 用户 '{username}' 登出，在线时长: {session_duration}分钟"

@on("system_alert").execute()
def handle_system_alert(level: str, message: str, component: str = "system") -> str:
    """系统告警事件 - 多参数处理"""
    alert_icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🚨"
    }
    icon = alert_icons.get(level, "❓")
    return f"{icon} [{level.upper()}] {component}: {message}"

# ==========================================
# 2. 命令系统高级示例
# ==========================================

@command_on("help", "/help", aliases=["h", "?"]).execute()
def show_help(args: List[str] = None) -> str:
    """帮助命令 - 支持别名"""
    return """
🤖 智能助手命令列表：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基础命令：
  /help, /h, /?     - 显示帮助信息
  /time             - 显示当前时间
  /status           - 系统状态信息

数学计算：
  /add a b          - 数字相加 (/add 10 20)
  /multiply a b     - 数字相乘 (/multiply 3 4)
  /calculate expr   - 计算表达式 (/calculate "2+3*4")

实用工具：
  /weather city     - 查询天气 (/weather 北京)
  /remind msg time  - 设置提醒 (/remind "开会" 30)
  /random min max   - 随机数生成 (/random 1 100)
"""

@command_on("time", "/time").execute()
def show_time(args: List[str] = None) -> str:
    """时间命令 - 显示多种格式"""
    now = datetime.now()
    formats = {
        "标准": now.strftime("%Y-%m-%d %H:%M:%S"),
        "中文": now.strftime("%Y年%m月%d日 %H时%M分%S秒"),
        "时间戳": str(int(now.timestamp())),
        "星期": now.strftime("%A")
    }
    
    result = "🕐 当前时间信息：\n"
    for key, value in formats.items():
        result += f"  {key}: {value}\n"
    return result.strip()

@command_on("add", "/add").execute()
def add_numbers(args: List[str]) -> str:
    """加法命令 - 参数验证"""
    if not args or len(args) < 2:
        return "❌ 用法: /add <数字1> <数字2> [数字3...]"
    
    try:
        numbers = [float(arg) for arg in args]
        total = sum(numbers)
        equation = " + ".join(args) + f" = {total}"
        return f"🧮 计算结果: {equation}"
    except ValueError as e:
        return f"❌ 输入错误: {e}"

@command_on("calculate", "/calculate").execute()
def calculate_expression(args: List[str]) -> str:
    """计算器命令 - 安全表达式计算"""
    if not args:
        return "❌ 用法: /calculate <数学表达式>"
    
    expression = " ".join(args)
    try:
        # 安全计算 - 只允许基本数学运算
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "❌ 表达式包含非法字符"
        
        result = eval(expression)
        return f"📊 表达式 '{expression}' = {result}"
    except Exception as e:
        return f"❌ 计算错误: {e}"

@command_on("weather", "/weather").execute()
def weather_command(args: List[str]) -> str:
    """天气命令 - 模拟天气API"""
    city = args[0] if args else "北京"
    
    # 模拟天气数据
    weather_data = {
        "北京": {"temp": 25, "condition": "晴朗", "wind": "微风2级"},
        "上海": {"temp": 28, "condition": "多云", "wind": "东南风3级"},
        "广州": {"temp": 32, "condition": "雷阵雨", "wind": "南风4级"},
        "深圳": {"temp": 30, "condition": "晴转多云", "wind": "东风2级"}
    }
    
    if city in weather_data:
        data = weather_data[city]
        return f"🌤️ {city}天气：{data['condition']}，温度{data['temp']}°C，{data['wind']}"
    else:
        return f"🌍 {city}天气：今天天气晴朗，温度25°C，微风2级（模拟数据）"

# ==========================================
# 3. 定时任务系统示例
# ==========================================

@time_on("heartbeat", priority=1, interval=5).execute()
async def heartbeat_monitor():
    """心跳监控 - 最高优先级"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"💓 [{timestamp}] 系统心跳检测：一切正常")
    return "heartbeat_ok"

@time_on("metrics", priority=2, interval=10).execute()
async def collect_metrics():
    """性能指标收集"""
    # 模拟系统指标收集
    cpu_usage = random.randint(20, 80)
    memory_usage = random.randint(40, 90)
    active_users = random.randint(10, 100)
    
    print(f"📊 系统指标: CPU:{cpu_usage}% 内存:{memory_usage}% 活跃用户:{active_users}")
    return f"metrics_collected"

@time_on("cleanup", priority=3, interval=15).execute()
async def cleanup_temp_files():
    """临时文件清理"""
    print("🧹 执行临时文件清理任务...")
    await asyncio.sleep(0.5)  # 模拟清理操作
    print("✅ 临时文件清理完成")
    return "cleanup_completed"

@time_on("backup", priority=4, interval=30).execute()
async def data_backup():
    """数据备份任务"""
    print("💾 开始数据备份...")
    await asyncio.sleep(2)  # 模拟备份过程
    print("✅ 数据备份完成")
    return "backup_completed"

# ==========================================
# 4. 正则表达式匹配示例
# ==========================================

@re_on("greeting", "text", re.compile(r"你好|您好|hello|hi|hey|早上好|下午好|晚上好"), priority=1).execute()
def handle_greeting(text: str, match: re.Match) -> str:
    """问候语匹配 - 智能回复"""
    greetings = {
        "你好": "你好！很高兴为您服务！",
        "您好": "您好！有什么可以帮助您的吗？",
        "hello": "Hello! How can I help you?",
        "hi": "Hi there! What can I do for you?",
        "早上好": "早上好！今天心情怎么样？",
        "下午好": "下午好！工作辛苦了！",
        "晚上好": "晚上好！今天过得怎么样？"
    }
    
    matched_text = match.group()
    response = greetings.get(matched_text.lower(), "您好！很高兴见到您！")
    return f"👋 {response}"

@re_on("weather_query", "text", re.compile(r"天气|weather|温度|temperature|下雨|下雪|晴天"), priority=2).execute()
def handle_weather_query(text: str, match: re.Match) -> str:
    """天气查询匹配"""
    if "下雨" in text:
        return "🌧️ 今天有雨，记得带伞哦！"
    elif "下雪" in text:
        return "❄️ 今天有雪，注意保暖！"
    elif "晴天" in text or "晴朗" in text:
        return "☀️ 今天天气晴朗，适合外出！"
    else:
        return "🌤️ 今天天气不错，温度适宜，记得关注天气变化！"

@re_on("emotion", "text", re.compile(r"开心|高兴|难过|伤心|生气|愤怒|紧张|焦虑"), priority=3).execute()
def handle_emotion(text: str, match: re.Match) -> str:
    """情绪识别匹配"""
    emotion = match.group()
    responses = {
        "开心": "😊 感受到您的开心，快乐是会传染的！",
        "高兴": "🎉 真为您高兴，保持这份美好心情！",
        "难过": "😢 感受到您的难过，一切都会好起来的。",
        "伤心": "💔 伤心的时候记得找人倾诉，不要独自承受。",
        "生气": "😠 生气对身体不好，深呼吸，让心情平静下来。",
        "愤怒": "🔥 愤怒的时候先冷静下来，理性处理问题。",
        "紧张": "😰 紧张是正常的，相信自己，您一定可以！",
        "焦虑": "😟 焦虑的时候试着做些放松的事情，一切都会过去的。"
    }
    return responses.get(emotion, "🤗 我感受到了您的情绪，希望您能感觉好一些。")

@re_on("question", "text", re.compile(r"什么|怎么|为什么|哪里|什么时候|谁|多少"), priority=4).execute()
def handle_question(text: str, match: re.Match) -> str:
    """问题识别匹配"""
    question_word = match.group()
    responses = {
        "什么": "🤔 这是个很好的问题，让我想想...",
        "怎么": "📖 关于如何操作，我可以为您提供详细指导。",
        "为什么": "💭 探究原因很重要，这能帮助您更好地理解。",
        "哪里": "📍 位置信息很重要，让我帮您查找相关信息。",
        "什么时候": "⏰ 时间安排很关键，您有什么具体需求吗？",
        "谁": "👤 关于相关人员的信息，我可以为您提供帮助。",
        "多少": "🔢 数量信息很重要，让我为您计算一下。"
    }
    return responses.get(question_word, "❓ 您的问题很有价值，我会尽力帮助您。")

# ==========================================
# 5. 高级功能示例
# ==========================================

class SmartAssistant:
    """智能助手类 - 展示框架的高级用法"""
    
    def __init__(self):
        self.event_dispatcher = EventDispatcher()
        self.command_dispatcher = DecisionCommandDispatcher()
        self.regex_scheduler = ReTaskScheduler()
        self.task_scheduler = None
        self.user_context = {}
    
    async def process_message(self, message: str, user_id: str = "default") -> List[str]:
        """处理用户消息 - 综合处理"""
        results = []
        
        # 1. 正则表达式匹配
        regex_results = await self.regex_scheduler.match_content(message)
        if regex_results:
            results.extend(regex_results)
        
        # 2. 命令识别
        if message.startswith('/'):
            command_result = await self.command_dispatcher.handle(message)
            if command_result:
                results.append(command_result)
        
        # 3. 事件触发（基于消息内容）
        if "登录" in message:
            event_result = await self.event_dispatcher.trigger_event("user_login", 1, user_id, "192.168.1.1")
            if event_result:
                results.append(event_result)
        
        return results if results else ["🤖 我没有理解您的意思，试试 /help 查看可用命令。"]
    
    async def start_background_tasks(self):
        """启动后台任务"""
        self.task_scheduler = TimeTaskScheduler()
        await self.task_scheduler.start()
        print("🚀 智能助手后台任务已启动")
    
    async def stop_background_tasks(self):
        """停止后台任务"""
        if self.task_scheduler:
            await self.task_scheduler.stop()
            print("🛑 智能助手后台任务已停止")

# ==========================================
# 6. 优先级队列高级示例
# ==========================================

async def demonstrate_advanced_priority_queue():
    """高级优先级队列演示"""
    print("\n=== 高级优先级队列演示 ===")
    
    # 创建多个不同类型的队列
    task_queue = PriorityQueue(max_size=20, max_memory_mb=10, name="任务队列")
    alert_queue = PriorityQueue(max_size=10, max_memory_mb=5, name="告警队列")
    log_queue = PriorityQueue(max_size=50, max_memory_mb=20, name="日志队列")
    
    # 模拟不同类型的任务
    tasks = [
        # 紧急任务
        ("🚨 系统崩溃：数据库连接失败", 0, "task_queue"),
        ("🚨 安全警告：检测到异常登录", 0, "alert_queue"),
        
        # 高优先级任务
        ("⚡ 性能优化：缓存重建", 1, "task_queue"),
        ("⚡ 数据同步：主从复制", 1, "task_queue"),
        
        # 中等优先级任务
        ("📊 报表生成：月度统计", 3, "task_queue"),
        ("🔍 日志分析：错误统计", 3, "log_queue"),
        
        # 低优先级任务
        ("📝 数据备份：每日归档", 5, "task_queue"),
        ("🧹 清理任务：临时文件", 7, "task_queue"),
        ("📈 性能监控：指标收集", 8, "log_queue"),
    ]
    
    # 添加任务到相应队列
    for task, priority, queue_type in tasks:
        if queue_type == "task_queue":
            success = task_queue.put(task, priority=priority)
        elif queue_type == "alert_queue":
            success = alert_queue.put(task, priority=priority)
        else:
            success = log_queue.put(task, priority=priority)
        
        status = "✅" if success else "❌"
        print(f"{status} 添加任务: {task} (优先级: {priority}) -> {queue_type}")
    
    # 处理队列任务
    queues = [("任务队列", task_queue), ("告警队列", alert_queue), ("日志队列", log_queue)]
    
    for queue_name, queue in queues:
        if not queue.empty():
            print(f"\n📋 处理 {queue_name}:")
            while not queue.empty():
                task = queue.get(timeout=0.1)
                if task:
                    print(f"  🏃 执行: {task}")
                    await asyncio.sleep(0.1)  # 模拟任务执行时间
    
    # 显示统计信息
    for queue_name, queue in queues:
        stats = queue.get_stats()
        print(f"\n📊 {queue_name} 统计: {stats}")

# ==========================================
# 7. 综合演示函数
# ==========================================

async def demonstrate_all_features():
    """完整的框架功能演示"""
    print("🚀 装饰器框架完整功能演示")
    print("=" * 60)
    
    # 创建智能助手实例
    assistant = SmartAssistant()
    
    try:
        # 1. 启动后台任务
        await assistant.start_background_tasks()
        await asyncio.sleep(2)  # 让定时任务运行一会儿
        
        # 2. 测试用户消息处理
        print("\n=== 智能消息处理演示 ===")
        test_messages = [
            "你好，今天天气怎么样？",
            "/weather 北京",
            "/add 15 25 35",
            "我今天感觉很开心！",
            "什么时候开会？",
            "系统出现错误，请检查日志",
            "/help",
            "登录系统成功"
        ]
        
        for message in test_messages:
            print(f"\n👤 用户消息: {message}")
            results = await assistant.process_message(message)
            for result in results:
                print(f"  🤖 回复: {result}")
            await asyncio.sleep(0.5)
        
        # 3. 高级优先级队列演示
        await demonstrate_advanced_priority_queue()
        
        # 4. 事件系统演示
        print("\n=== 事件系统演示 ===")
        dispatcher = EventDispatcher()
        
        events = [
            ("user_login", 1, "张三", "192.168.1.100"),
            ("user_logout", 2, "李四", 30),
            ("system_alert", 3, "warning", "磁盘空间不足", "storage"),
            ("system_alert", 4, "error", "数据库连接超时", "database")
        ]
        
        for event_name, priority, *args in events:
            result = await dispatcher.trigger_event(event_name, priority, *args)
            print(f"📡 事件 '{event_name}' 结果: {result}")
        
        # 5. 等待定时任务执行
        print(f"\n⏰ 等待定时任务执行...")
        await asyncio.sleep(5)
        
    finally:
        # 停止后台任务
        await assistant.stop_background_tasks()

# ==========================================
# 8. 实用工具函数
# ==========================================

def show_system_statistics():
    """显示系统统计信息"""
    print("\n=== 系统统计信息 ===")
    
    registry = ClassNucleus.get_registry()
    
    stats = {
        "事件处理器": len(registry.get('on', {})),
        "命令处理器": len(registry.get('command_on', {})),
        "定时任务": len(registry.get('time_on', {})),
        "正则处理器": len(registry.get('re_on', {}))
    }
    
    for component, count in stats.items():
        print(f"  📊 {component}: {count} 个")
    
    return stats

def export_registered_handlers() -> Dict[str, List[Dict[str, Any]]]:
    """导出所有注册的处理函数信息"""
    registry = ClassNucleus.get_registry()
    
    export_data = {}
    
    # registry 是一个字典，键是 fun_name，值是类对象
    for fun_name, handler_class in registry.items():
        # 根据类的属性确定处理器类型
        if hasattr(handler_class, 'command'):
            handler_type = 'command_on'
        elif hasattr(handler_class, 'interval'):
            handler_type = 'time_on'
        elif hasattr(handler_class, 'rule'):
            handler_type = 're_on'
        else:
            handler_type = 'on'
        
        if handler_type not in export_data:
            export_data[handler_type] = []
        
        handler_info = {
            "name": fun_name,
            "fun_name": getattr(handler_class, 'fun_name', 'unknown'),
            "priority": getattr(handler_class, 'priority', 1),
            "interval": getattr(handler_class, 'interval', None),
            "command": getattr(handler_class, 'command', None),
            "aliases": getattr(handler_class, 'aliases', []),
            "pattern": getattr(handler_class, 'rule', None)
        }
        export_data[handler_type].append(handler_info)
    
    return export_data

# ==========================================
# 9. 主函数
# ==========================================

async def main():
    """主函数：运行完整演示"""
    print("🎯 装饰器框架完整使用案例")
    print("=" * 60)
    print("📋 本演示将展示框架的所有核心功能：")
    print("  • 事件处理系统 (@on)")
    print("  • 命令处理系统 (@command_on)")
    print("  • 定时任务系统 (@time_on)")
    print("  • 正则匹配系统 (@re_on)")
    print("  • 优先级队列管理")
    print("  • 智能消息处理")
    print("=" * 60)
    
    try:
        # 显示系统统计
        show_system_statistics()
        
        # 运行完整演示
        await demonstrate_all_features()
        
        # 导出注册信息
        print("\n=== 注册处理器详情 ===")
        handlers_info = export_registered_handlers()
        
        for handler_type, handlers in handlers_info.items():
            if handlers:
                print(f"\n🔧 {handler_type.upper()} 处理器:")
                for handler in handlers:
                    print(f"  • {handler['fun_name']}")
                    if handler['priority'] != 1:
                        print(f"    优先级: {handler['priority']}")
                    if handler['interval']:
                        print(f"    间隔: {handler['interval']}秒")
                    if handler['command']:
                        print(f"    命令: {handler['command']}")
                    if handler['aliases']:
                        print(f"    别名: {handler['aliases']}")
        
        print("\n" + "=" * 60)
        print("✅ 装饰器框架完整演示完成！")
        print("🎉 所有功能正常运行，框架稳定可靠！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())