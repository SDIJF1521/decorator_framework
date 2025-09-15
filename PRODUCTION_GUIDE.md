# 🏭 装饰器框架 - 生产环境部署指南

## 📋 目录

1. [架构概览](#架构概览)
2. [生产环境配置](#生产环境配置)
3. [性能优化](#性能优化)
4. [监控与告警](#监控与告警)
5. [部署方案](#部署方案)
6. [扩展开发](#扩展开发)
7. [故障处理](#故障处理)
8. [最佳实践](#最佳实践)

## 🏗️ 架构概览

### 核心组件

```
┌─────────────────────────────────────────┐
│              生产架构图                  │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    │
│  │   API网关    │    │   负载均衡   │    │
│  └──────┬──────┘    └──────┬──────┘    │
│         │                  │            │
│  ┌──────┴──────┐    ┌──────┴──────┐    │
│  │  应用实例1   │    │  应用实例2   │    │
│  │ ┌─────────┐ │    │ ┌─────────┐ │    │
│  │ │事件调度器 │ │    │ │事件调度器 │ │    │
│  │ ├─────────┤ │    │ ├─────────┤ │    │
│  │ │命令调度器 │ │    │ │命令调度器 │ │    │
│  │ ├─────────┤ │    │ ├─────────┤ │    │
│  │ │定时调度器 │ │    │ │定时调度器 │ │    │
│  │ └─────────┘ │    │ └─────────┘ │    │
│  └─────────────┘    └─────────────┘    │
│         │                  │            │
│  ┌──────┴──────┐    ┌──────┴──────┐    │
│  │   Redis     │    │ PostgreSQL  │    │
│  │  (缓存/锁)   │    │  (持久化)    │    │
│  └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────┘
```

### 组件职责

| 组件 | 职责 | 高可用方案 |
|---|---|---|
| EventDispatcher | 事件触发与处理 | 多实例 + 消息队列 |
| DecisionCommandDispatcher | 命令解析与路由 | 无状态服务 |
| TimeTaskScheduler | 定时任务调度 | 分布式锁 |
| ReTaskScheduler | 正则表达式匹配 | 无状态服务 |

## ⚙️ 生产环境配置

### 1. 环境变量配置

创建 `config/production.py`：

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductionConfig:
    # 数据库配置
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/db')
    
    # Redis配置
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 日志配置
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', '/var/log/decorator_framework/app.log')
    
    # 性能配置
    MAX_WORKERS: int = int(os.getenv('MAX_WORKERS', '4'))
    QUEUE_SIZE: int = int(os.getenv('QUEUE_SIZE', '1000'))
    
    # 监控配置
    METRICS_PORT: int = int(os.getenv('METRICS_PORT', '9090'))
    HEALTH_CHECK_PORT: int = int(os.getenv('HEALTH_CHECK_PORT', '8080'))
    
    # 安全配置
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key')
    ALLOWED_HOSTS: list = os.getenv('ALLOWED_HOSTS', '*').split(',')

config = ProductionConfig()
```

### 2. 日志配置

创建 `config/logging.py`：

```python
import logging
import logging.handlers
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'task_name': getattr(record, 'task_name', None),
            'execution_time': getattr(record, 'execution_time', None)
        }
        return json.dumps(log_entry)

def setup_logging(log_level='INFO', log_file='/var/log/decorator_framework/app.log'):
    # 创建日志目录
    import os
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # JSON格式处理器
    json_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=50*1024*1024, backupCount=5
    )
    json_handler.setFormatter(JSONFormatter())
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    root_logger.addHandler(json_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
```

### 3. 数据库模型

创建 `models/task_storage.py`：

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class TaskExecutionLog(Base):
    __tablename__ = 'task_execution_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(255), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)  # on, command, time, re
    status = Column(String(20), nullable=False)  # success, failed, timeout
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    duration_ms = Column(Float)
    result = Column(Text)
    error_message = Column(Text)
    hostname = Column(String(255))
    pid = Column(Integer)
    memory_usage_mb = Column(Float)
    
class ScheduledTask(Base):
    __tablename__ = 'scheduled_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(255), unique=True, nullable=False)
    task_type = Column(String(50), nullable=False)
    interval_seconds = Column(Integer)
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    config = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

## 🚀 性能优化

### 1. 连接池配置

创建 `utils/connection_pool.py`：

```python
import redis
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

class ConnectionPool:
    def __init__(self, config):
        self.config = config
        self._redis_pool = None
        self._db_engine = None
        self._async_session = None
    
    @property
    def redis_pool(self):
        if not self._redis_pool:
            self._redis_pool = redis.ConnectionPool(
                host='localhost',
                port=6379,
                db=0,
                max_connections=50,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
        return redis.Redis(connection_pool=self._redis_pool)
    
    @property
    def db_engine(self):
        if not self._db_engine:
            self._db_engine = create_engine(
                self.config.DATABASE_URL,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600
            )
        return self._db_engine
    
    @property
    def async_session(self):
        if not self._async_session:
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            async_engine = create_async_engine(
                self.config.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True
            )
            self._async_session = sessionmaker(
                async_engine, class_=AsyncSession
            )
        return self._async_session

# 全局连接池实例
connection_pool = None

def init_connection_pool(config):
    global connection_pool
    connection_pool = ConnectionPool(config)
    logger.info("Connection pools initialized")
```

### 2. 异步优化

创建 `utils/async_worker.py`：

```python
import asyncio
import concurrent.futures
import logging
from typing import Callable, Any
import psutil
import os

logger = logging.getLogger(__name__)

class AsyncWorkerPool:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix='decorator_worker'
        )
        self.semaphore = asyncio.Semaphore(max_workers * 2)
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor, 
                lambda: func(*args, **kwargs)
            )
    
    def get_system_metrics(self):
        process = psutil.Process(os.getpid())
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'num_threads': process.num_threads()
        }
    
    def shutdown(self):
        self.executor.shutdown(wait=True)

# 全局工作池
worker_pool = AsyncWorkerPool()
```

## 📊 监控与告警

### 1. 指标收集

创建 `monitoring/metrics.py`：

```python
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import logging

logger = logging.getLogger(__name__)

# Prometheus指标
TASK_EXECUTION_COUNT = Counter('decorator_task_executions_total', 'Total task executions', ['task_type', 'status'])
TASK_EXECUTION_DURATION = Histogram('decorator_task_duration_seconds', 'Task execution duration', ['task_type'])
ACTIVE_TASKS = Gauge('decorator_active_tasks', 'Number of active tasks')
SYSTEM_MEMORY = Gauge('decorator_system_memory_mb', 'System memory usage in MB')
SYSTEM_CPU = Gauge('decorator_system_cpu_percent', 'System CPU usage percent')

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    def record_task_execution(self, task_type: str, duration: float, status: str):
        TASK_EXECUTION_COUNT.labels(task_type=task_type, status=status).inc()
        TASK_EXECUTION_DURATION.labels(task_type=task_type).observe(duration)
    
    def update_system_metrics(self):
        process = psutil.Process()
        SYSTEM_MEMORY.set(process.memory_info().rss / 1024 / 1024)
        SYSTEM_CPU.set(psutil.cpu_percent())
    
    def start_metrics_server(self, port: int = 9090):
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")

metrics = MetricsCollector()
```

### 2. 健康检查

创建 `monitoring/health.py`：

```python
import asyncio
import psutil
import json
from datetime import datetime
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self, config):
        self.config = config
        self.start_time = datetime.now()
        self.checks = {}
    
    def register_check(self, name: str, check_func):
        self.checks[name] = check_func
    
    async def health_check(self, request):
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'version': '1.0.0',
            'checks': {}
        }
        
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                health_status['checks'][check_name] = result
                if not result.get('healthy', True):
                    health_status['status'] = 'unhealthy'
            except Exception as e:
                health_status['checks'][check_name] = {
                    'healthy': False,
                    'error': str(e)
                }
                health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return web.json_response(health_status, status=status_code)
    
    async def readiness_check(self, request):
        return web.json_response({'ready': True})
    
    async def liveness_check(self, request):
        return web.json_response({'alive': True})
    
    def start_health_server(self, port: int = 8080):
        app = web.Application()
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/ready', self.readiness_check)
        app.router.add_get('/live', self.liveness_check)
        
        web.run_app(app, port=port)

# 健康检查函数示例
async def check_database_connection():
    # 实现数据库连接检查
    return {'healthy': True, 'latency_ms': 5}

async def check_redis_connection():
    # 实现Redis连接检查
    return {'healthy': True, 'connected_clients': 10}
```

## 🚀 部署方案

### 1. Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8080 9090

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令
CMD ["python", "main.py"]
```

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
      - "9090:9090"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/decorator_db
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    volumes:
      - ./logs:/var/log/decorator_framework

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: decorator_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  postgres_data:
  redis_data:
```

### 2. Kubernetes部署

创建 `k8s/namespace.yaml`：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: decorator-framework
  labels:
    name: decorator-framework
```

创建 `k8s/configmap.yaml`：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: decorator-config
  namespace: decorator-framework
data:
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "4"
  QUEUE_SIZE: "1000"
  METRICS_PORT: "9090"
  HEALTH_CHECK_PORT: "8080"
```

创建 `k8s/deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: decorator-app
  namespace: decorator-framework
  labels:
    app: decorator-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: decorator-app
  template:
    metadata:
      labels:
        app: decorator-app
    spec:
      containers:
      - name: decorator-app
        image: decorator-framework:latest
        ports:
        - containerPort: 8080
        - containerPort: 9090
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: decorator-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: decorator-secrets
              key: redis-url
        envFrom:
        - configMapRef:
            name: decorator-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

创建 `k8s/service.yaml`：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: decorator-service
  namespace: decorator-framework
spec:
  selector:
    app: decorator-app
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
```

## 🔧 扩展开发

### 1. 自定义调度器

创建 `extensions/custom_dispatcher.py`：

```python
from nucleus.dispatcher import BaseDispatcher
import asyncio
from typing import Any, Dict

class CustomEventDispatcher(BaseDispatcher):
    """自定义事件调度器示例"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.retry_policy = {
            'max_retries': 3,
            'backoff_factor': 2,
            'max_backoff': 60
        }
    
    async def dispatch_with_retry(self, event_name: str, *args, **kwargs) -> Any:
        """带重试的事件分发"""
        last_exception = None
        
        for attempt in range(self.retry_policy['max_retries']):
            try:
                return await self.dispatch(event_name, *args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.retry_policy['max_retries'] - 1:
                    backoff = min(
                        self.retry_policy['backoff_factor'] ** attempt,
                        self.retry_policy['max_backoff']
                    )
                    await asyncio.sleep(backoff)
        
        raise last_exception
    
    async def batch_dispatch(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """批量事件分发"""
        tasks = []
        for event_name, data in events.items():
            task = asyncio.create_task(
                self.dispatch(event_name, **data)
            )
            tasks.append((event_name, task))
        
        results = {}
        for event_name, task in tasks:
            try:
                results[event_name] = await task
            except Exception as e:
                results[event_name] = {'error': str(e)}
        
        return results
```

### 2. 插件系统

创建 `extensions/plugin_system.py`：

```python
import importlib
import inspect
from typing import Dict, List, Type

class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def load_plugin(self, plugin_path: str):
        """动态加载插件"""
        try:
            module = importlib.import_module(plugin_path)
            
            # 查找调度器类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith('Dispatcher') and hasattr(obj, 'dispatch'):
                    self.plugins[name] = obj
                    print(f"Loaded plugin: {name}")
        except Exception as e:
            print(f"Failed to load plugin {plugin_path}: {e}")
    
    def get_plugin(self, name: str):
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())

plugin_manager = PluginManager()
```

## 🚨 故障处理

### 1. 常见故障及解决方案

| 故障类型 | 症状 | 解决方案 |
|---|---|---|
| 内存泄漏 | 内存持续增长 | 重启服务，检查循环引用 |
| 连接超时 | 数据库/Redis连接失败 | 检查网络，增加超时时间 |
| 任务堆积 | 队列长度持续增长 | 增加worker数量，优化任务 |
| 死锁 | 任务无法执行 | 检查分布式锁配置 |

### 2. 故障恢复脚本

创建 `scripts/recovery.py`：

```python
#!/usr/bin/env python3
import asyncio
import redis
import psycopg2
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecoveryManager:
    def __init__(self, redis_url, db_url):
        self.redis_client = redis.from_url(redis_url)
        self.db_url = db_url
    
    async def cleanup_stuck_tasks(self):
        """清理卡住的任务"""
        stuck_keys = self.redis_client.keys("task:lock:*")
        for key in stuck_keys:
            ttl = self.redis_client.ttl(key)
            if ttl == -1:  # 永不过期的锁
                self.redis_client.delete(key)
                logger.info(f"Removed stuck lock: {key}")
    
    async def retry_failed_tasks(self, hours=24):
        """重试失败的任务"""
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_name, config FROM task_execution_logs 
            WHERE status = 'failed' 
            AND start_time > NOW() - INTERVAL '%s hours'
        """, (hours,))
        
        failed_tasks = cursor.fetchall()
        for task_name, config in failed_tasks:
            logger.info(f"Retrying failed task: {task_name}")
            # 实现重试逻辑
        
        cursor.close()
        conn.close()

if __name__ == "__main__":
    recovery = RecoveryManager('redis://localhost:6379', 'postgresql://localhost/db')
    asyncio.run(recovery.cleanup_stuck_tasks())
```

## 📈 最佳实践

### 1. 任务设计原则

```python
# ✅ 推荐做法
@time_on("data_sync", priority=1, interval=300).execute()
async def sync_user_data():
    """批量同步用户数据"""
    try:
        # 使用分页避免内存溢出
        async for batch in fetch_user_batches(size=1000):
            await process_batch(batch)
            await asyncio.sleep(0.1)  # 防止CPU过载
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        raise

# ❌ 不推荐做法
@time_on("data_sync", priority=1, interval=60).execute()
def sync_all_users():
    users = fetch_all_users()  # 可能内存溢出
    for user in users:
        process_user(user)  # 阻塞操作
```

### 2. 配置管理

创建 `config/config_loader.py`：

```python
import yaml
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_dir='config'):
        self.config_dir = config_dir
    
    def load_config(self, environment: str) -> Dict[str, Any]:
        """加载环境配置"""
        base_config = self._load_yaml('base.yaml')
        env_config = self._load_yaml(f'{environment}.yaml')
        
        # 环境变量覆盖
        for key, value in os.environ.items():
            if key.startswith('DECORATOR_'):
                config_key = key[10:].lower()
                self._set_nested_value(base_config, config_key, value)
        
        return {**base_config, **env_config}
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        try:
            with open(f'{self.config_dir}/{filename}') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
    
    def _set_nested_value(self, config: Dict, key: str, value: str):
        keys = key.split('__')
        current = config
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value

config_loader = ConfigLoader()
```

### 3. 部署检查清单

创建 `scripts/deploy_checklist.py`：

```python
import subprocess
import sys
import os

def check_deployment():
    checks = [
        ("Python版本", "python --version"),
        ("依赖安装", "pip list | grep -E 'sqlalchemy|redis|psycopg2'"),
        ("环境变量", "env | grep -E 'DATABASE_URL|REDIS_URL'"),
        ("端口监听", "netstat -tlnp | grep -E '8080|9090'"),
        ("日志目录", "ls -la /var/log/decorator_framework/"),
        ("数据库连接", "python -c 'import psycopg2; psycopg2.connect()'"),
        ("Redis连接", "python -c 'import redis; redis.Redis().ping()'"),
    ]
    
    all_passed = True
    for name, command in checks:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: FAILED")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    if check_deployment():
        print("\n🎉 所有检查通过，可以开始部署")
    else:
        print("\n⚠️  有检查项未通过，请修复后再部署")
        sys.exit(1)
```

## 📊 性能基准测试

创建 `benchmarks/performance_test.py`：

```python
import asyncio
import time
import statistics
from decorators.on import on, time_on, command_on
from nucleus.dispatcher import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    def __init__(self):
        self.results = {}
    
    async def benchmark_event_dispatch(self, num_events=10000):
        """事件分发性能测试"""
        
        @on("benchmark_event").execute()
        async def fast_task(data):
            return f"processed {data}"
        
        dispatcher = EventDispatcher()
        
        start_time = time.time()
        tasks = []
        for i in range(num_events):
            task = dispatcher.trigger_event("benchmark_event", f"data_{i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        self.results['event_dispatch'] = {
            'events_per_second': num_events / duration,
            'total_events': num_events,
            'duration': duration
        }
    
    async def benchmark_command_processing(self, num_commands=1000):
        """命令处理性能测试"""
        
        @command_on("benchmark_cmd", "/benchmark").execute()
        async def benchmark_command(args=None):
            return f"processed {len(args or [])} args"
        
        dispatcher = DecisionCommandDispatcher()
        
        start_time = time.time()
        tasks = []
        for i in range(num_commands):
            task = dispatcher.handle(f"/benchmark arg1 arg2 arg3")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        self.results['command_processing'] = {
            'commands_per_second': num_commands / duration,
            'total_commands': num_commands,
            'duration': duration
        }
    
    def print_results(self):
        print("=" * 50)
        print("性能测试结果")
        print("=" * 50)
        for test_name, metrics in self.results.items():
            print(f"{test_name}:")
            for key, value in metrics.items():
                print(f"  {key}: {value}")
            print()

async def main():
    benchmark = PerformanceBenchmark()
    await benchmark.benchmark_event_dispatch()
    await benchmark.benchmark_command_processing()
    benchmark.print_results()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📞 支持与联系

- **文档**: [完整文档]([https://github.com/your-org/decorator-framework](https://github.com/SDIJF1521/decorator_framework/blob/master/README.md))
- **问题反馈**: [GitHub Issues](https://github.com/your-org/decorator-framework/issues)
- **邮件**: 839682307@qq.com
- **Slack**: #decorator-framework on your-org.slack.com

---

*这份文档将持续更新，欢迎贡献您的生产经验！*
