---
**Version**: 2.1.0  
**Last Updated**: 2025-01-15  
**Document Status**: ✅ API Documentation Fixed - Based on Actual Code Framework
---

**⚠️ Important**: All decorators must use the `.execute()` method!

# Decorator Framework API Reference

## 📋 Decorator API

### @on Event Decorator

Handles event-driven asynchronous tasks.

```python
from decorators.on import on

@on(name: str).execute()
async def handler_function(*args, **kwargs) -> str:
    """Event handler"""
    return "Processing result"
```

**Parameters:**
- `name`: Event name for triggering and listening

**Example:**
```python
@on("user_login").execute()  # Note: Must call .execute()
async def handle_login(username):
    return f"Welcome {username}"

# Trigger event
await dispatcher.trigger_event("user_login", "alice")
```

### @time_on Scheduled Task Decorator

Creates periodically executed scheduled tasks.

```python
from decorators.on import time_on

@time_on(name: str, priority: int = 1, interval: int = 0).execute()
async def scheduled_task() -> str:
    """Scheduled task"""
    return "Task execution result"
```

**Parameters:**
- `name`: Task unique identifier
- `priority`: Task priority (1-10, smaller numbers have higher priority)
- `interval`: Execution interval time (seconds)

**Example:**
```python
@time_on("backup_task", priority=1, interval=3600).execute()  # Note: Must call .execute()
async def hourly_backup():
    return "Database backup completed"
```

### @command_on Command Decorator

Handles command line or API calls.

```python
from decorators.on import command_on

@command_on(name: str, command: str, aliases: list = None, cooldown: int = 0).execute()
async def command_handler(args: str = "") -> str:
    """Command handler"""
    return "Command execution result"
```

**Parameters:**
- `name`: Command handler name
- `command`: Command match pattern (must start with "/", e.g., "/start")
- `aliases`: Command alias list (optional)
- `cooldown`: Cooldown time (seconds, optional)

**Example:**
```python
@command_on("greet", "/hello").execute()  # Note: Must call .execute()
async def greet_command(args=""):
    name = args.strip() if args.strip() else "World"
    return f"Hello, {name}!"

# Execute command
result = await dispatcher.handle("/hello Alice")
```

### @re_on Regular Expression Decorator

Processes text content based on regular expression matching.

```python
import re
from decorators.on import re_on

@re_on(name: str, content: str, pattern: re.Pattern, priority: int = 1).execute()
async def regex_handler(content: str, match: re.Match) -> str:
    """Regular expression handler"""
    return f"Match result: {match.group(1)}"
```

**Parameters:**
- `name`: Pattern name
- `content`: Text content parameter name to match
- `pattern`: Regular expression pattern object (created using `re.compile()`)
- `priority`: Priority (optional, defaults to 1)

**Example:**
```python
import re
from decorators.on import re_on

@re_on("error_pattern", "content", re.compile(r"ERROR:(\w+)")).execute()  # Note: Must call .execute()
async def handle_error(content, match):
    error_type = match.group(1)
    return f"Error detected: {error_type}"

# Trigger match
await dispatcher.trigger_event("error_detector", "ERROR:database_timeout")
```

## 🔧 Scheduler API

### EventDispatcher Event Scheduler

Manages event registration and triggering.

```python
from nucleus.dispatcher import EventDispatcher

dispatcher = EventDispatcher()

# Trigger event
await dispatcher.trigger_event(event_name: str, *args, **kwargs) -> Any

# Get registered events
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

**Methods:**
- `trigger_event()`: Triggers event and executes registered handlers
- `ClassNucleus.get_registry()`: Returns all registered classes

### DecisionCommandDispatcher Command Scheduler

Handles command parsing and execution.

```python
from nucleus.dispatcher import DecisionCommandDispatcher

dispatcher = DecisionCommandDispatcher()

# Process command
await dispatcher.handle(message: str) -> str

# Get registered commands
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

### TimeTaskScheduler Scheduled Task Scheduler

Manages scheduled task execution.

```python
from nucleus.dispatcher import TimeTaskScheduler

scheduler = TimeTaskScheduler()

# Start scheduler
await scheduler.start()

# Stop scheduler
await scheduler.stop()

# Get task list
scheduler.time_tasks -> list
```

## 📊 Logging Configuration

### Basic Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get module logger
logger = logging.getLogger(__name__)
```