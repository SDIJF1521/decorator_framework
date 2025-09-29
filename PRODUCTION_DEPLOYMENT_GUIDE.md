# 装饰器框架生产环境部署指南

## 文档语言
- [English Version](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) - 英文生产部署指南
- [中文版本](PRODUCTION_DEPLOYMENT_GUIDE.md) - 当前文档（中文生产部署）

## 框架概述

这是一个基于装饰器的轻量级异步事件驱动框架，提供事件处理、定时任务、命令处理和正则表达式匹配四大核心功能。框架完全基于实际的 `decorators/on.py` 和 `nucleus/dispatcher.py` 实现。

## 核心功能

### 1. 事件系统 (@on)
```python
from decorators.on import on

@on("user_registration").execute()
async def handle_user_registration(user_data):
    """处理用户注册事件"""
    return f"用户注册成功: {user_data['email']}"
```

### 2. 定时任务 (@time_on)
```python
from decorators.on import time_on

@time_on("system_monitor", priority=1, interval=3).execute()
async def monitor_system():
    """每3秒执行的系统监控"""
    return f"系统监控: 正常运行"
```

### 3. 命令处理 (@command_on)
```python
from decorators.on import command_on

@command_on("health_check", "/health").execute()
async def health_check(args=None):
    """健康检查命令"""
    return "健康检查: 状态正常"
```

### 4. 正则表达式 (@re_on)
```python
from decorators.on import re_on
import re

@re_on("error_detector", "content", re.compile(r"ERROR.*")).execute()
async def detect_errors(error_message):
    """错误检测"""
    return f"检测到错误: {error_message}"
```

## 快速开始

### 1. 项目结构
```
decorator_framework/
├── decorators/
│   ├── on.py          # 核心装饰器实现
├── nucleus/
│   ├── dispatcher.py    # 调度器实现
│   ├── Myclass.py     # 类注册系统
├── production_final.py  # 生产级示例
├── QUICK_START_CORRECT.py # 快速入门示例
```

### 2. 基础使用示例

#### 创建事件处理器
```python
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decorators.on import on
from nucleus.dispatcher import EventDispatcher

@on("user_login").execute()
async def handle_login(user_data):
    """处理用户登录"""
    print(f"用户 {user_data['username']} 登录成功")
    return f"欢迎 {user_data['username']}"

async def demo():
    dispatcher = EventDispatcher()
    result = await dispatcher.trigger_event("user_login", {
        "username": "alice",
        "user_id": "U123"
    })
    print(result)

if __name__ == "__main__":
    asyncio.run(demo())
```

#### 创建定时任务
```python
from decorators.on import time_on
from nucleus.dispatcher import TimeTaskScheduler

@time_on("backup_task", priority=1, interval=3600).execute()
async def backup_database():
    """每小时备份数据库"""
    return "数据库备份完成"

# 启动定时任务
scheduler = TimeTaskScheduler()
await scheduler.start()
```

#### 创建命令处理器
```python
from decorators.on import command_on
from nucleus.dispatcher import DecisionCommandDispatcher

@command_on("backup", "/backup").execute()
async def backup_command(args=None):
    """手动备份命令"""
    if args and args[0] == "full":
        return "执行全量备份"
    return "执行增量备份"

# 使用命令
dispatcher = DecisionCommandDispatcher()
result = await dispatcher.handle("/backup full")
```

## 生产环境部署

### 优先级队列配置

#### 1. 资源控制配置
```python
from nucleus.data.priority_queue import ResourceController

# 生产环境资源控制
RESOURCE_CONTROLLER = ResourceController(
    max_concurrent=int(os.getenv("MAX_CONCURRENT_TASKS", "100")),
    timeout=int(os.getenv("RESOURCE_TIMEOUT", "30"))
)

# 事件调度器配置（带优先级队列）
EVENT_DISPATCHER = EventDispatcher(
    max_queue_size=int(os.getenv("MAX_EVENT_QUEUE_SIZE", "1000")),
    priority_levels=int(os.getenv("PRIORITY_LEVELS", "10"))
)
```

#### 2. 队列监控和告警
```python
# 队列监控配置
QUEUE_MONITORING = {
    'enabled': os.getenv("QUEUE_MONITORING_ENABLED", "true").lower() == "true",
    'alert_threshold': int(os.getenv("QUEUE_ALERT_THRESHOLD", "800")),
    'stats_interval': int(os.getenv("QUEUE_STATS_INTERVAL", "60"))
}

# 队列统计函数
async def monitor_queue_health():
    """监控队列健康状况"""
    stats = EVENT_DISPATCHER.get_event_queue_stats()
    if stats['queue_size'] > QUEUE_MONITORING['alert_threshold']:
        logging.warning(f"事件队列积压: {stats['queue_size']} 任务")
        # 发送告警通知
        await send_alert(f"队列积压告警: {stats['queue_size']} 任务等待处理")
```

### 1. 配置文件 (config.py)
```python
import os
import logging

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 框架配置
FRAMEWORK_CONFIG = {
    'scheduler_enabled': os.getenv("SCHEDULER_ENABLED", "true").lower() == "true",
    'heartbeat_interval': int(os.getenv("HEARTBEAT_INTERVAL", "30")),
    'log_level': os.getenv("LOG_LEVEL", "INFO"),
    'max_concurrent_tasks': int(os.getenv("MAX_CONCURRENT_TASKS", "100")),
    'max_event_queue_size': int(os.getenv("MAX_EVENT_QUEUE_SIZE", "1000")),
    'queue_monitoring_enabled': os.getenv("QUEUE_MONITORING_ENABLED", "true").lower() == "true",
}

# 实际使用的模块
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler
from nucleus.data.priority_queue import ResourceController
from decorators.on import on, time_on, command_on, re_on

# 初始化事件调度器（内部已包含资源控制器）
event_dispatcher = EventDispatcher()
```

### 2. 生产级日志配置
```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 3. Docker 部署

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "production_final.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  decorator-app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - LOG_LEVEL=INFO
      - SCHEDULER_ENABLED=true
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### 4. Kubernetes 部署

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: decorator-framework
spec:
  replicas: 3
  selector:
    matchLabels:
      app: decorator-framework
  template:
    metadata:
      labels:
        app: decorator-framework
    spec:
      containers:
      - name: app
        image: your-registry/decorator-framework:latest
        ports:
        - containerPort: 8080
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: SCHEDULER_ENABLED
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 📊 监控与告警

### 1. 健康检查端点
```python
from decorators.on import command_on
from datetime import datetime

@command_on("health_check", "/health").execute()
async def health_check(args=None):
    """健康检查端点"""
    return "健康检查: 状态正常 - 框架运行中"
```

### 2. 日志监控
```python
import logging
from decorators.on import on

logger = logging.getLogger(__name__)

@on("user_action").execute()
async def track_user_action(action_data):
    """跟踪用户行为"""
    logger.info(f"用户行为: {action_data}")
    return "行为已记录"
```

### 3. 告警规则
```yaml
# alerts.yaml
groups:
- name: decorator-framework
  rules:
  - alert: HighErrorRate
    expr: rate(framework_events_total{status="error"}[5m]) > 0.1
    for: 5m
    annotations:
      summary: "高错误率告警"
      
  - alert: ServiceDown
    expr: up{job="decorator-framework"} == 0
    for: 1m
    annotations:
      summary: "服务不可用"
```

## 🔒 安全最佳实践

### 1. 输入验证
```python
import re
from decorators.on import command_on

@command_on("user_command", "/user").execute()
async def handle_user_command(args=None):
    """安全的用户命令处理"""
    if not args or len(args) < 2:
        return "错误: 参数不足"
    
    user_id = re.sub(r'[^a-zA-Z0-9_-]', '', args[0])
    action = args[1]
    
    # 简单验证
    if len(user_id) < 3:
        return "错误: 用户ID太短"
    
    return f"执行 {action} 成功"
```

### 2. 内置速率限制
框架的 `@command_on` 装饰器内置了冷却功能：
```python
from decorators.on import command_on

@command_on("api_call", "/api", cooldown=60).execute()
async def rate_limited_api(args=None):
    """带60秒冷却的命令"""
    return "API调用成功"
```

## 🔄 错误处理与重试

### 1. 异常处理
```python
import asyncio
from functools import wraps

def retry_on_exception(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

@time_on("critical_task", priority=1, interval=60).execute()
@retry_on_exception(max_retries=3, delay=2)
async def critical_database_operation():
    """带重试的关键数据库操作"""
    # 数据库操作
    return "操作成功"
```

### 2. 死信队列
```python
@on("failed_task").execute()
async def handle_failed_task(task_data):
    """处理失败的任务"""
    logger.error(f"任务失败: {task_data}")
    # 发送到死信队列
    await send_to_dlq(task_data)
    return "已记录到失败队列"
```

## 📈 性能优化

### 1. 连接池管理
```python
import asyncio
from aiohttp import ClientSession

class ConnectionPool:
    def __init__(self, max_connections=100):
        self.connector = None
        self.session = None
    
    async def get_session(self):
        if not self.session:
            self.session = ClientSession(
                connector=aiohttp.TCPConnector(limit=100)
            )
        return self.session

pool = ConnectionPool()

@on("http_request").execute()
async def make_http_request(request_data):
    """使用连接池的HTTP请求"""
    session = await pool.get_session()
    async with session.get(request_data['url']) as response:
        return await response.text()
```

### 2. 缓存策略
```python
from functools import lru_cache
import asyncio

@lru_cache(maxsize=128)
def cached_calculation(key):
    return expensive_operation(key)

@command_on("cache", "/cache").execute()
async def cache_command(args=None):
    """缓存命令"""
    if not args:
        return "请提供缓存键"
    
    key = args[0]
    result = cached_calculation(key)
    return f"缓存结果: {result}"
```

## 🧪 测试策略

### 1. 单元测试
```python
import pytest
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decorators.on import on
from nucleus.dispatcher import EventDispatcher

@pytest.mark.asyncio
async def test_user_registration():
    @on("test_registration").execute()
    async def mock_registration(data):
        return f"注册成功: {data['email']}"
    
    dispatcher = EventDispatcher()
    result = await dispatcher.trigger_event("test_registration", {
        "email": "test@example.com"
    })
    assert "注册成功" in result

@pytest.mark.asyncio
async def test_command_handler():
    from decorators.on import command_on
    from nucleus.dispatcher import DecisionCommandDispatcher
    
    @command_on("test_cmd", "/test").execute()
    async def test_command(args=None):
        return f"测试命令: {args}"
    
    dispatcher = DecisionCommandDispatcher()
    result = await dispatcher.handle("/test hello")
    assert "测试命令" in str(result)
```

### 2. 集成测试
```python
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_full_workflow():
    """测试完整工作流"""
    from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler
    
    # 测试事件系统
    event_dispatcher = EventDispatcher()
    
    # 测试命令系统
    command_dispatcher = DecisionCommandDispatcher()
    
    # 测试定时任务
    time_scheduler = TimeTaskScheduler()
    
    # 验证各组件初始化
    assert event_dispatcher is not None
    assert command_dispatcher is not None
    assert time_scheduler is not None
    
    print("✅ 所有组件测试通过")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())
```

## 📋 部署检查清单

### 预部署检查
- [ ] 代码审查完成
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试完成
- [ ] 安全扫描通过
- [ ] 配置验证完成

### 部署步骤
1. **环境准备**
   ```bash
   # 创建命名空间
   kubectl create namespace decorator-prod
   
   # 创建配置映射
   kubectl create configmap decorator-config --from-file=config.py
   ```

2. **部署应用**
   ```bash
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   kubectl apply -f ingress.yaml
   ```

3. **验证部署**
   ```bash
   kubectl get pods -n decorator-prod
   kubectl logs -f deployment/decorator-framework -n decorator-prod
   ```

4. **健康检查**
   ```bash
   curl http://your-domain/health
   ```

## 🔧 故障排除

### 常见问题

#### 1. 类型错误: Expected str got dict
**原因**: 函数返回字典而框架期望字符串
**解决**: 确保所有装饰器函数返回字符串类型

#### 2. 异步警告
**原因**: 未正确使用 await
**解决**: 所有异步方法调用都使用 await

#### 3. 任务不执行
**原因**: 定时任务未正确注册
**解决**: 检查装饰器语法和间隔设置

### 调试命令
```bash
# 查看注册的任务
python -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
from nucleus.Myclass import ClassNucleus
print('已注册的任务:', list(ClassNucleus.get_registry().keys()))
"

# 测试单个命令
python -c "
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
from nucleus.dispatcher import DecisionCommandDispatcher

async def test():
    d = DecisionCommandDispatcher()
    result = await d.handle('/health')
    print('命令结果:', result)

asyncio.run(test())
"

# 测试事件
python -c "
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
from nucleus.dispatcher import EventDispatcher

async def test():
    e = EventDispatcher()
    result = await e.trigger_event('user_login', {'username': 'test'})
    print('事件结果:', result)

asyncio.run(test())
"
```

## 📞 支持与维护

### 监控指标
- 事件处理延迟
- 命令响应时间
- 定时任务成功率
- 系统资源使用率

### 升级策略
1. 蓝绿部署
2. 滚动更新
3. 金丝雀发布

### 备份策略
- 配置备份
- 任务状态备份
- 日志归档

---
**版本**: 2.1.0  
**最后更新**: 2025-01-15  
**文档状态**: ✅ 生产就绪 - 基于实际代码框架修正