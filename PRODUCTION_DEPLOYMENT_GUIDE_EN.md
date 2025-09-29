# Decorator Framework Production Deployment Guide

## Framework Overview

This is a production-grade asynchronous event-driven framework based on decorators, providing four core functions: event handling, scheduled tasks, command processing, and regular expression matching. The framework is completely based on the actual implementation of `decorators/on.py` and `nucleus/dispatcher.py`.

## Core Features

### 1. Event System (@on)
```python
from decorators.on import on

@on("user_registration").execute()
async def handle_user_registration(user_data):
    """Handle user registration event"""
    return f"User registration successful: {user_data['email']}"
```

### 2. Scheduled Tasks (@time_on)
```python
from decorators.on import time_on

@time_on("system_monitor", priority=1, interval=3).execute()
async def monitor_system():
    """System monitoring every 3 seconds"""
    return f"System monitoring: Running normally"
```

### 3. Command Processing (@command_on)
```python
from decorators.on import command_on

@command_on("health_check", "/health").execute()
async def health_check(args=None):
    """Health check command"""
    return "Health check: Status normal"
```

### 4. Regular Expression (@re_on)
```python
from decorators.on import re_on
import re

@re_on("error_detector", "content", re.compile(r"ERROR.*")).execute()
async def detect_errors(error_message):
    """Error detection"""
    return f"Error detected: {error_message}"
```

## Quick Start

### 1. Project Structure
```
decorator_framework/
├── decorators/
│   ├── on.py          # Core decorator implementation
├── nucleus/
│   ├── dispatcher.py    # Scheduler implementation
│   ├── Myclass.py     # Class registration system
├── production_final.py  # Production-grade example
├── QUICK_START_CORRECT.py # Quick start example
```

### 2. Basic Usage Examples

#### Create Event Handler
```python
import asyncio
import sys
import os

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decorators.on import on
from nucleus.dispatcher import EventDispatcher

@on("user_login").execute()
async def handle_login(user_data):
    """Handle user login"""
    print(f"User {user_data['username']} logged in successfully")
    return f"Welcome {user_data['username']}"

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

#### Create Scheduled Tasks
```python
from decorators.on import time_on
from nucleus.dispatcher import TimeTaskScheduler

@time_on("backup_task", priority=1, interval=3600).execute()
async def backup_database():
    """Backup database every hour"""
    return "Database backup completed"

# Start scheduled tasks
scheduler = TimeTaskScheduler()
await scheduler.start()
```

#### Create Command Processor
```python
from decorators.on import command_on
from nucleus.dispatcher import DecisionCommandDispatcher

@command_on("backup", "/backup").execute()
async def backup_command(args=None):
    """Manual backup command"""
    if args and args[0] == "full":
        return "Performing full backup"
    return "Performing incremental backup"

# Use command
dispatcher = DecisionCommandDispatcher()
result = await dispatcher.handle("/backup full")
```

## Production Environment Deployment

### Priority Queue Configuration

#### 1. Resource Control Configuration
```python
from nucleus.data.priority_queue import ResourceController

# Production environment resource control
RESOURCE_CONTROLLER = ResourceController(
    max_concurrent=int(os.getenv("MAX_CONCURRENT_TASKS", "100")),
    timeout=int(os.getenv("RESOURCE_TIMEOUT", "30"))
)

# Event dispatcher configuration (with priority queue)
EVENT_DISPATCHER = EventDispatcher(
    max_queue_size=int(os.getenv("MAX_EVENT_QUEUE_SIZE", "1000")),
    priority_levels=int(os.getenv("PRIORITY_LEVELS", "10"))
)
```

#### 2. Queue Monitoring and Alerting
```python
# Queue monitoring configuration
QUEUE_MONITORING = {
    'enabled': os.getenv("QUEUE_MONITORING_ENABLED", "true").lower() == "true",
    'alert_threshold': int(os.getenv("QUEUE_ALERT_THRESHOLD", "800")),
    'stats_interval': int(os.getenv("QUEUE_STATS_INTERVAL", "60"))
}

# Queue health monitoring function
async def monitor_queue_health():
    """Monitor queue health status"""
    stats = EVENT_DISPATCHER.get_event_queue_stats()
    if stats['queue_size'] > QUEUE_MONITORING['alert_threshold']:
        logging.warning(f"Event queue backlog: {stats['queue_size']} tasks")
        # Send alert notification
        await send_alert(f"Queue backlog alert: {stats['queue_size']} tasks waiting for processing")
```

### 1. Configuration File (config.py)
```python
import os
import logging

# Log configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Framework configuration
FRAMEWORK_CONFIG = {
    'scheduler_enabled': os.getenv("SCHEDULER_ENABLED", "true").lower() == "true",
    'heartbeat_interval': int(os.getenv("HEARTBEAT_INTERVAL", "30")),
    'log_level': os.getenv("LOG_LEVEL", "INFO"),
    'max_concurrent_tasks': int(os.getenv("MAX_CONCURRENT_TASKS", "100")),
    'max_event_queue_size': int(os.getenv("MAX_EVENT_QUEUE_SIZE", "1000")),
    'queue_monitoring_enabled': os.getenv("QUEUE_MONITORING_ENABLED", "true").lower() == "true",
}

# Actual modules used
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler
from nucleus.data.priority_queue import ResourceController
from decorators.on import on, time_on, command_on, re_on

# Initialize event dispatcher (includes internal resource controller)
event_dispatcher = EventDispatcher()
```

### 2. Production-grade Log Configuration
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

###### 3. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

```

## 🔗 Document Navigation

- [中文生产部署指南](PRODUCTION_DEPLOYMENT_GUIDE.md) - Chinese Production Deployment Guide
- [English README](EN_README.md) - English Documentation
- [中文README](README.md) - Chinese Documentation
- [API Reference](API_REFERENCE_EN.md) - API Documentation
- [Best Practices](BEST_PRACTICES_EN.md) - Best Practices Guide
- [Test Guide](RUN_TESTS_EN.md) - Testing Documentation

### Framework Documentation
- **Main Documentation**: [EN_README.md](EN_README.md) | [README.md](README.md)
- **API Reference**: [API_REFERENCE_EN.md](API_REFERENCE_EN.md) | [API_REFERENCE.md](API_REFERENCE.md)
- **Best Practices**: [BEST_PRACTICES_EN.md](BEST_PRACTICES_EN.md) | [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Production Guide**: [PRODUCTION_DEPLOYMENT_GUIDE_EN.md](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) | [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
- **Test Guide**: [RUN_TESTS_EN.md](RUN_TESTS_EN.md) | [RUN_TESTS.md](RUN_TESTS.md)