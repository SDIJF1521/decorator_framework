# 生产级装饰器框架部署指南

## 概述

本指南提供从开发到生产的完整部署流程，涵盖架构设计、环境配置、监控告警、扩展性考虑等生产级要素。

## 1. 架构设计

### 1.1 核心架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Event System  │    │ Command System  │    │ Schedule System │
│      (@on)      │    │  (@command_on)   │    │   (@time_on)    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│  EventDispatcher │    │ CommandHandler  │    │ TaskScheduler   │
│  Async Processing │    │  Pattern Match  │    │  Cron-like      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Core Engine   │
                    │   Dispatcher    │
                    └─────────────────┘
```

### 1.2 部署架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Application   │    │   Database      │
│     (Nginx)    │────│    Instances    │────│   (PostgreSQL)  │
│   SSL/TLS       │    │   (Docker)      │    │   Redis Cache   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Monitoring    │
                    │   Prometheus    │
                    │   Grafana       │
                    └─────────────────┘
```

## 2. 环境配置

### 2.1 开发环境

```bash
# 安装依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 启动开发服务器
python production_ready.py
```

### 2.2 生产环境配置

#### 环境变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/prod_db
REDIS_URL=redis://localhost:6379/0

# 应用配置
LOG_LEVEL=INFO
WORKERS=4
PORT=8000
HOST=0.0.0.0

# 安全配置
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### 配置文件

```python
# config/production.py
import os
from dataclasses import dataclass

@dataclass
class ProductionConfig:
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    WORKERS: int = int(os.getenv("WORKERS", 4))
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALLOWED_HOSTS: list = None
    
    def __post_init__(self):
        if self.ALLOWED_HOSTS is None:
            self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
```

## 3. Docker 部署

### 3.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

CMD ["python", "production_ready.py"]
```

### 3.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/prod_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=prod_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

## 4. Kubernetes 部署

### 4.1 Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: decorator-framework
  labels:
    app: decorator-framework
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
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 4.2 Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: decorator-framework-service
spec:
  selector:
    app: decorator-framework
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## 5. 监控与告警

### 5.1 指标收集

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
EVENT_COUNTER = Counter('framework_events_total', 'Total events processed')
COMMAND_COUNTER = Counter('framework_commands_total', 'Total commands processed')
TASK_DURATION = Histogram('framework_task_duration_seconds', 'Task execution time')
ACTIVE_TASKS = Gauge('framework_active_tasks', 'Number of active tasks')

class MetricsMiddleware:
    def __init__(self):
        self.start_time = time.time()
    
    def record_event(self, event_name):
        EVENT_COUNTER.inc()
        logger.info(f"Event recorded: {event_name}")
    
    def record_command(self, command_name):
        COMMAND_COUNTER.inc()
        logger.info(f"Command recorded: {command_name}")
```

### 5.2 告警规则

```yaml
# monitoring/alerts.yml
groups:
  - name: framework
    rules:
      - alert: HighErrorRate
        expr: rate(framework_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
      
      - alert: TaskQueueBacklog
        expr: framework_active_tasks > 100
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Task queue backlog detected"
```

## 6. 性能优化

### 6.1 连接池配置

```python
# database/pool.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600
)
```

### 6.2 缓存策略

```python
# cache/redis.py
import redis
import json
from functools import wraps

redis_client = redis.from_url(REDIS_URL)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 7. 扩展开发

### 7.1 自定义调度器

```python
# extensions/custom_scheduler.py
from nucleus.dispatcher import BaseScheduler
import asyncio

class CustomScheduler(BaseScheduler):
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    async def schedule_task(self, task, interval):
        while True:
            try:
                await task()
            except Exception as e:
                logger.error(f"Task failed: {e}")
            await asyncio.sleep(interval)
```

### 7.2 插件系统

```python
# extensions/plugin_system.py
class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin):
        self.plugins.append(plugin)
    
    async def initialize_plugins(self):
        for plugin in self.plugins:
            await plugin.initialize()
    
    async def cleanup_plugins(self):
        for plugin in self.plugins:
            await plugin.cleanup()
```

## 8. 安全考虑

### 8.1 输入验证

```python
# security/validation.py
import re
from typing import Any, Dict

class InputValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        return sanitized
```

### 8.2 访问控制

```python
# security/auth.py
from functools import wraps

def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 验证逻辑
        if not validate_token(kwargs.get('token')):
            raise PermissionError("Invalid token")
        return await func(*args, **kwargs)
    return wrapper
```

## 9. 部署脚本

### 9.1 自动化部署

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting deployment..."

# 构建镜像
docker build -t decorator-framework:latest .

# 推送到仓库
docker push your-registry/decorator-framework:latest

# 部署到Kubernetes
kubectl apply -f k8s/

# 等待部署完成
kubectl rollout status deployment/decorator-framework

echo "Deployment completed!"
```

### 9.2 回滚脚本

```bash
#!/bin/bash
# rollback.sh

set -e

if [ -z "$1" ]; then
    echo "Usage: ./rollback.sh <previous-version>"
    exit 1
fi

kubectl set image deployment/decorator-framework \
    app=your-registry/decorator-framework:$1

kubectl rollout status deployment/decorator-framework

echo "Rollback to $1 completed!"
```

## 10. 监控仪表板

### 10.1 Grafana 配置

```json
{
  "dashboard": {
    "title": "Decorator Framework Dashboard",
    "panels": [
      {
        "title": "Event Rate",
        "targets": [
          {
            "expr": "rate(framework_events_total[5m])",
            "legendFormat": "Events/sec"
          }
        ]
      },
      {
        "title": "Command Rate",
        "targets": [
          {
            "expr": "rate(framework_commands_total[5m])",
            "legendFormat": "Commands/sec"
          }
        ]
      }
    ]
  }
}
```

## 11. 故障处理

### 11.1 日志分析

```bash
# 查看实时日志
kubectl logs -f deployment/decorator-framework

# 搜索错误
kubectl logs deployment/decorator-framework | grep ERROR

# 查看特定时间段的日志
kubectl logs deployment/decorator-framework --since=1h
```

### 11.2 性能诊断

```bash
# CPU使用率
kubectl top pods

# 内存使用率
kubectl top nodes

# 网络延迟
kubectl exec -it pod-name -- ping database-host
```

## 12. 扩展性考虑

### 12.1 水平扩展

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: decorator-framework-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: decorator-framework
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 12.2 数据库分片

```python
# database/sharding.py
class ShardingManager:
    def __init__(self, shards):
        self.shards = shards
    
    def get_shard(self, key):
        return self.shards[hash(key) % len(self.shards)]
```

## 总结

本生产部署指南提供了从开发到生产的完整路径，包括：

- ✅ 完整的架构设计
- ✅ Docker和Kubernetes部署
- ✅ 监控和告警系统
- ✅ 性能优化策略
- ✅ 安全最佳实践
- ✅ 扩展性考虑
- ✅ 故障处理流程

通过遵循本指南，您可以将装饰器框架成功部署到生产环境，并确保其稳定运行。