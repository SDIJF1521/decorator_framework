"""
调度器集成演示 - 事件调度 + 命令调度 + 定时任务 + 正则任务
展示如何与依赖注入、调用链和任务管理集成使用
"""
import asyncio
import time
import re
import sys
from typing import Optional,Any
from datetime import datetime

# 添加当前目录到Python路径，确保导入本地模块
sys.path.insert(0, '.')

# 导入核心功能
from nucleus import (
    enable_framework_integration,
    service,
    inject,
    task_with_chain,
    get_task_manager,
    get_dependency_container,
    get_call_chain,
    get_framework_integration
)

# 从核心模块导入额外的类
from nucleus.core.chain import ChainInterceptor, ChainContext

# 导入调度器功能
from nucleus.dispatcher import (
    EventDispatcher,
    DecisionCommandDispatcher,
    TimeTaskScheduler,
    ReTaskScheduler
)

# 1. 定义服务接口和实现
class INotificationService:
    """通知服务接口"""
    
    async def send_notification(self, message: str, priority: int = 5) -> str:
        """发送通知"""
        raise NotImplementedError


@service('singleton')
class EmailNotificationService(INotificationService):
    """邮件通知服务实现"""
    
    def __init__(self):
        self.sent_count = 0
    
    async def send_notification(self, message: str, priority: int = 5) -> str:
        """发送邮件通知"""
        self.sent_count += 1
        await asyncio.sleep(0.1)  # 模拟发送延迟
        
        result = f"📧 邮件通知已发送: {message} (优先级: {priority}, 总计: {self.sent_count})"
        print(result)
        return result


class ILogService:
    """日志服务接口"""
    
    async def log_event(self, event_type: str, message: str) -> None:
        """记录事件日志"""
        raise NotImplementedError


@service('singleton')
class FileLogService(ILogService):
    """文件日志服务实现"""
    
    def __init__(self):
        self.log_entries = []
    
    async def log_event(self, event_type: str, message: str) -> None:
        """记录事件到文件日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {event_type}: {message}"
        self.log_entries.append(log_entry)
        print(f"📝 日志记录: {log_entry}")


# 2. 定义事件处理器类（用于事件调度器）
class UserRegistrationHandler:
    """用户注册事件处理器"""
    fun_name = "user_registered"
    
    def __init__(self):
        self.notification_service = None
        self.log_service = None
    
    async def execute(self, username: str, email: str) -> str:
        """处理用户注册事件"""
        # 延迟初始化服务（解决循环依赖）
        if not self.notification_service:
            container = get_dependency_container()
            self.notification_service = container.resolve(INotificationService)
            self.log_service = container.resolve(ILogService)
        
        # 发送欢迎通知
        message = f"欢迎 {username} 注册成功！邮箱: {email}"
        await self.notification_service.send_notification(message, priority=3)
        
        # 记录日志
        await self.log_service.log_event("USER_REGISTRATION", f"用户 {username} 注册成功")
        
        return f"用户注册事件处理完成: {username}"


class OrderCreatedHandler:
    """订单创建事件处理器"""
    fun_name = "order_created"
    
    def __init__(self):
        self.notification_service = None
        self.log_service = None
    
    async def execute(self, order_id: str, amount: float) -> str:
        """处理订单创建事件"""
        if not self.notification_service:
            container = get_dependency_container()
            self.notification_service = container.resolve(INotificationService)
            self.log_service = container.resolve(ILogService)
        
        # 发送订单确认通知
        message = f"订单 {order_id} 创建成功，金额: ¥{amount:.2f}"
        await self.notification_service.send_notification(message, priority=2)
        
        # 记录日志
        await self.log_service.log_event("ORDER_CREATED", f"订单 {order_id} 创建，金额: {amount}")
        
        return f"订单创建事件处理完成: {order_id}"


# 3. 定义命令处理器类（用于命令调度器）
class HelpCommand:
    """帮助命令处理器"""
    fun_name = "help_command"
    command = "/help"
    aliases = ["/h", "/?"]
    cooldown = 2  # 2秒冷却时间
    
    def __init__(self):
        self.last_executed = 0
        self.cooldown_lock = asyncio.Lock()
    
    async def execute(self) -> str:
        """执行帮助命令"""
        help_text = """
🤖 可用命令列表:
• /help, /h, /? - 显示此帮助信息
• /status - 显示系统状态
• /notify <消息> - 发送测试通知
• /stats - 显示统计信息
        """.strip()
        return help_text


class StatusCommand:
    """状态命令处理器"""
    fun_name = "status_command"
    command = "/status"
    cooldown = 1
    
    def __init__(self):
        self.last_executed = 0
        self.cooldown_lock = asyncio.Lock()
    
    async def execute(self) -> str:
        """执行状态命令"""
        # 获取各种统计信息
        task_manager = get_task_manager()
        task_stats = task_manager.get_statistics()
        
        status_text = f"""
📊 系统状态:
• 任务总数: {task_stats['total_tasks']}
• 活跃任务: {task_stats['active_tasks']}
• 已完成任务: {task_stats['completed_tasks']}
• 失败任务: {task_stats['failed_tasks']}
        """.strip()
        return status_text


class NotifyCommand:
    """通知命令处理器"""
    fun_name = "notify_command"
    command = "/notify"
    cooldown = 3
    
    def __init__(self):
        self.last_executed = 0
        self.cooldown_lock = asyncio.Lock()
        self.notification_service = None
    
    def arg_parser(self, args: str) -> dict:
        """解析命令参数"""
        return {"message": args.strip()}
    
    async def execute(self, message: str = "") -> str:
        """执行通知命令"""
        if not message:
            return "❌ 请提供通知消息，例如: /notify 测试消息"
        
        if not self.notification_service:
            container = get_dependency_container()
            self.notification_service = container.resolve(INotificationService)
        
        result = await self.notification_service.send_notification(message, priority=4)
        return f"✅ 通知已发送: {message}"


# 4. 定义定时任务类（用于定时任务调度器）
class DataCleanupTask:
    """数据清理定时任务"""
    fun_name = "data_cleanup_task"
    interval = 10  # 每10秒执行一次
    priority = 1   # 高优先级
    
    def __init__(self):
        self.log_service = None
        self.execution_count = 0
    
    async def execute(self) -> None:
        """执行数据清理任务"""
        if not self.log_service:
            container = get_dependency_container()
            self.log_service = container.resolve(ILogService)
        
        self.execution_count += 1
        
        # 模拟数据清理
        cleanup_time = time.strftime("%H:%M:%S")
        print(f"🧹 执行数据清理任务 #{self.execution_count} - {cleanup_time}")
        
        await self.log_service.log_event("DATA_CLEANUP", f"数据清理任务 #{self.execution_count} 执行完成")


class HealthCheckTask:
    """健康检查定时任务"""
    fun_name = "health_check_task"
    interval = 5   # 每5秒执行一次
    priority = 2   # 中等优先级
    
    def __init__(self):
        self.log_service = None
        self.check_count = 0
    
    async def execute(self) -> None:
        """执行健康检查任务"""
        if not self.log_service:
            container = get_dependency_container()
            self.log_service = container.resolve(ILogService)
        
        self.check_count += 1
        
        # 模拟健康检查
        check_time = time.strftime("%H:%M:%S")
        status = "正常" if self.check_count % 3 != 0 else "警告"
        
        print(f"🏥 执行健康检查 #{self.check_count} - {check_time} - 状态: {status}")
        
        await self.log_service.log_event("HEALTH_CHECK", f"健康检查 #{self.check_count} - 状态: {status}")


# 5. 定义正则任务类（用于正则任务调度器）
class LogAnalyzerTask:
    """日志分析正则任务"""
    fun_name = "log_analyzer_task"
    rule = r"ERROR|WARN|异常|失败"  # 匹配错误关键词
    priority = 1  # 高优先级
    
    def __init__(self):
        self.log_service = None
        self.error_count = 0
    
    async def execute(self, content: str, match_obj: Optional[re.Match]) -> str:
        """分析日志内容"""
        if not self.log_service:
            container = get_dependency_container()
            self.log_service = container.resolve(ILogService)
        
        self.error_count += 1
        
        # 分析匹配到的错误
        error_type = match_obj.group() if match_obj else "未知错误"
        
        alert_message = f"🚨 发现 {error_type} 类型错误 (总计: {self.error_count})"
        print(alert_message)
        
        await self.log_service.log_event("ERROR_DETECTED", f"检测到错误: {error_type} 在内容: {content[:50]}...")
        
        return alert_message


class KeywordMonitorTask:
    """关键词监控正则任务"""
    fun_name = "keyword_monitor_task"
    rule = r"重要|紧急|立刻|马上"  # 匹配重要关键词
    priority = 2  # 中等优先级
    
    def __init__(self):
        self.log_service = None
        self.keyword_count = 0
    
    async def execute(self, content: str, match_obj: Optional[re.Match]) -> str:
        """监控关键词"""
        if not self.log_service:
            container = get_dependency_container()
            self.log_service = container.resolve(ILogService)
        
        self.keyword_count += 1
        
        # 分析匹配到的关键词
        keyword = match_obj.group() if match_obj else "未知关键词"
        
        alert_message = f"🔍 发现重要关键词 '{keyword}' (总计: {self.keyword_count})"
        print(alert_message)
        
        await self.log_service.log_event("KEYWORD_DETECTED", f"检测到关键词: {keyword} 在内容: {content[:50]}...")
        
        return alert_message


# 6. 创建自定义调用链拦截器
class SchedulerInterceptor(ChainInterceptor):
    """调度器调用链拦截器"""
    
    def __init__(self):
        self.call_count = 0
    
    async def before_execute(self, context: ChainContext) -> None:
        self.call_count += 1
        context_name = getattr(context, 'function_name', 'unknown')
        print(f"🔗 [调度器链] 开始执行: {context_name} (#{self.call_count})")
        context.metadata['start_time'] = time.time()
    
    async def after_execute(self, context: ChainContext) -> None:
        duration = time.time() - context.metadata.get('start_time', 0)
        context_name = getattr(context, 'function_name', 'unknown')
        print(f"✅ [调度器链] 执行完成: {context_name} (耗时: {duration:.3f}s)")
    
    async def on_error(self, context: ChainContext, error: Exception) -> None:
        duration = time.time() - context.metadata.get('start_time', 0)
        context_name = getattr(context, 'function_name', 'unknown')
        print(f"❌ [调度器链] 执行失败: {context_name} (耗时: {duration:.3f}s, 错误: {error})")


# 7. 主演示函数
async def demo_event_dispatcher():
    """演示事件调度器"""
    print("\n🎯 演示事件调度器")
    print("=" * 50)
    
    event_dispatcher = EventDispatcher()
    
    # 注册事件处理器
    event_dispatcher.register_event("user_registered", UserRegistrationHandler)
    event_dispatcher.register_event("order_created", OrderCreatedHandler)
    
    # 触发事件
    print("🚀 触发用户注册事件:")
    result1 = await event_dispatcher.trigger_event("user_registered", priority=3, username="张三", email="zhang@example.com")
    print(f"结果: {result1}")
    
    print("\n🚀 触发订单创建事件:")
    result2 = await event_dispatcher.trigger_event("order_created", priority=2, order_id="ORD001", amount=299.99)
    print(f"结果: {result2}")
    
    # 等待事件处理完成
    await asyncio.sleep(2)
    
    # 查看事件队列统计
    stats = event_dispatcher.get_event_queue_stats()
    print(f"\n📊 事件队列统计: {stats}")
    
    # 停止事件处理
    event_dispatcher.stop_event_processing()


async def demo_command_dispatcher():
    """演示命令调度器"""
    print("\n🎯 演示命令调度器")
    print("=" * 50)
    
    command_dispatcher = DecisionCommandDispatcher()
    
    # 注册命令处理器
    command_dispatcher.register_command("help_command", HelpCommand)
    command_dispatcher.register_command("status_command", StatusCommand)
    command_dispatcher.register_command("notify_command", NotifyCommand)
    
    # 测试各种命令
    commands_to_test = [
        "/help",
        "/h",
        "/status",
        "/notify 测试通知消息",
        "/invalid_command",  # 无效命令
        "不是命令",          # 非命令消息
    ]
    
    for cmd in commands_to_test:
        print(f"\n🚀 测试命令: {cmd}")
        result = await command_dispatcher.handle(cmd, priority=3)
        print(f"结果: {result}")
        await asyncio.sleep(0.5)  # 稍微等待以避免过快
    
    # 查看命令队列统计
    stats = command_dispatcher.get_command_queue_stats()
    print(f"\n📊 命令队列统计: {stats}")
    
    # 停止命令处理
    command_dispatcher.stop_command_processing()


async def demo_time_task_scheduler():
    """演示定时任务调度器"""
    print("\n🎯 演示定时任务调度器")
    print("=" * 50)
    
    time_scheduler = TimeTaskScheduler()
    
    # 注册定时任务
    # 注意：这里我们手动添加任务，实际使用时会从注册器自动加载
    time_scheduler.time_tasks = [
        {
            'priority': 1,
            'interval': 5,  # 每5秒
            'handler': DataCleanupTask().execute,
            'last_executed': 0
        },
        {
            'priority': 2,
            'interval': 3,  # 每3秒
            'handler': HealthCheckTask().execute,
            'last_executed': 0
        }
    ]
    
    # 启动定时任务调度器
    await time_scheduler.start()
    
    # 运行一段时间
    print("⏰ 定时任务调度器运行中...")
    await asyncio.sleep(12)  # 运行12秒，观察多个周期的任务执行
    
    # 查看队列统计
    stats = time_scheduler.get_queue_stats()
    print(f"\n📊 定时任务统计: {stats}")
    
    # 停止调度器
    await time_scheduler.stop()


async def demo_regex_task_scheduler():
    """演示正则任务调度器"""
    print("\n🎯 演示正则任务调度器")
    print("=" * 50)
    
    regex_scheduler = ReTaskScheduler()
    
    # 模拟日志内容分析
    log_contents = [
        "用户登录成功，一切正常",
        "ERROR: 数据库连接失败，需要立刻处理",
        "系统运行稳定，无异常",
        "WARN: 内存使用率过高，建议检查",
        "这是一个重要的系统更新通知",
        "普通的消息内容",
        "异常：网络连接超时，请马上联系技术支持",
    ]
    
    for content in log_contents:
        print(f"\n🔍 分析日志内容: {content}")
        results = await regex_scheduler.match_content(content)
        
        if results:
            print("匹配结果:")
            for result in results:
                print(f"  • {result}")
        else:
            print("未匹配到任何模式")
        
        await asyncio.sleep(0.5)
    
    # 测试特定任务触发
    print(f"\n🚀 触发特定日志分析任务:")
    specific_results = await regex_scheduler.trigger("log_analyzer_task", "ERROR: 严重的系统错误")
    for result in specific_results:
        print(f"结果: {result}")


async def demo_integrated_scheduler_workflow():
    """演示集成调度器工作流"""
    print("\n🎯 演示集成调度器工作流")
    print("=" * 60)
    
    # 获取调用链并添加拦截器
    call_chain = get_call_chain()
    scheduler_interceptor = SchedulerInterceptor()
    call_chain.add_interceptor(scheduler_interceptor)
    
    # 定义集成工作流函数
    @task_with_chain(name="集成调度器工作流", metadata={"type": "integrated_workflow"})
    async def integrated_workflow(user_action: str) -> str:
        """集成调度器工作流"""
        print(f"🔄 开始集成工作流，用户动作: {user_action}")
        
        # 创建调度器实例
        event_dispatcher = EventDispatcher()
        command_dispatcher = DecisionCommandDispatcher()
        
        # 注册处理器
        event_dispatcher.register_event("user_registered", UserRegistrationHandler)
        command_dispatcher.register_command("help_command", HelpCommand)
        
        # 步骤1: 处理用户命令
        if user_action.startswith("/"):
            command_result = await command_dispatcher.handle(user_action, priority=2)
            print(f"命令处理结果: {command_result}")
        
        # 步骤2: 触发相关事件
        if "注册" in user_action:
            event_result = await event_dispatcher.trigger_event("user_registered", priority=1, username="新用户", email="new@example.com")
            print(f"事件处理结果: {event_result}")
        
        # 步骤3: 创建后台任务
        task_manager = get_task_manager()
        
        async def background_task(task_name: str) -> str:
            await asyncio.sleep(1)
            return f"后台任务完成: {task_name}"
        
        task_id = task_manager.create_task(
            background_task("集成工作流后台任务"),
            name="集成工作流任务",
            metadata={"workflow": "integrated"}
        )
        
        # 等待后台任务完成
        task_result = await task_manager.wait_for_task_async(task_id, timeout=2)
        print(f"后台任务结果: {task_result}")
        
        # 清理调度器
        event_dispatcher.stop_event_processing()
        command_dispatcher.stop_command_processing()
        
        return f"集成工作流完成: {user_action}"
    
    # 执行集成工作流
    workflow_actions = [
        "/help",
        "用户注册流程",
        "/status",
        "普通用户操作"
    ]
    
    for action in workflow_actions:
        print(f"\n🚀 执行工作流: {action}")
        result = await integrated_workflow(action)
        print(f"工作流结果: {result}")
        await asyncio.sleep(1)


async def main():
    """主演示函数"""
    print("🚀 调度器集成演示")
    print("=" * 60)
    
    # 启用框架集成
    integration = enable_framework_integration()
    print("✅ 框架集成已启用")
    
    try:
        # 演示1: 事件调度器
        await demo_event_dispatcher()
        
        # 演示2: 命令调度器
        await demo_command_dispatcher()
        
        # 演示3: 定时任务调度器（运行较短时间用于演示）
        await demo_time_task_scheduler()
        
        # 演示4: 正则任务调度器
        await demo_regex_task_scheduler()
        
        # 演示5: 集成工作流
        await demo_integrated_scheduler_workflow()
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        task_manager = get_task_manager()
        cancelled = task_manager.cancel_all_tasks()
        print(f"✅ 已取消 {cancelled} 个活跃任务")
        
        stats = task_manager.get_statistics()
        print(f"📊 最终任务统计: {stats}")
        
        print("\n🎉 调度器集成演示完成！")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())