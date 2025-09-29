---
**Version**: 2.2.0  
**Last Updated**: 2025-01-16  
**Document Status**: ✅ API Documentation Updated - Includes Priority Queue and Integration Examples
---

**Important**: All decorators must use the `.execute()` method!

# Decorator Framework API Reference

## Decorator API

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

Manages event registration and triggering, supports priority queue.

```python
from nucleus.dispatcher import EventDispatcher

dispatcher = EventDispatcher()

# Trigger event (supports priority)
await dispatcher.trigger_event(event_name: str, priority: int = 5, data: dict = None) -> Any

# Register event handler
dispatcher.register_event(event_name: str, handler_class)

# Get event queue statistics
stats = dispatcher.get_event_queue_stats()

# Get registered events
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

**Methods:**
- `trigger_event()`: Triggers event and executes registered handlers
- `register_event()`: Register event handler
- `get_event_queue_stats()`: Get event queue statistics
- `ClassNucleus.get_registry()`: Returns all registered classes

### DecisionCommandDispatcher Command Scheduler

Handles command parsing and execution, supports priority queue and decision tree.

```python
from nucleus.dispatcher import DecisionCommandDispatcher
from nucleus.data.tree import Tree

dispatcher = DecisionCommandDispatcher()

# Set decision tree
dispatcher.tree = Tree()

# Register command handler
dispatcher.register_command(command_name: str, handler_class)

# Process command (supports priority)
await dispatcher.handle(message: str, priority: int = 5) -> str

# Get command queue statistics
stats = dispatcher.get_command_queue_stats()

# Get registered commands
from nucleus.Myclass import ClassNucleus
ClassNucleus.get_registry() -> dict
```

### TimeTaskScheduler Scheduled Task Scheduler

Manages scheduled task execution, supports priority queue and resource control.

```python
from nucleus.dispatcher import TimeTaskScheduler

scheduler = TimeTaskScheduler()

# Start scheduler
await scheduler.start()

# Stop scheduler
await scheduler.stop()

# Get task queue statistics
stats = scheduler.get_queue_stats()

# Get task list
scheduler.time_tasks -> list

# Access internal priority queue
scheduler.task_queue -> PriorityQueue
```

## 📊 Priority Queue API

### PriorityQueue Priority Queue

Thread-safe priority queue implementation supporting task priority management and resource limits.

```python
from nucleus.data.priority_queue import PriorityQueue, ResourceController

# Create priority queue
queue = PriorityQueue(maxsize=100, resource_limit=50)

# Add task (priority: 1 highest, 10 lowest)
success = queue.put(item, priority=5)

# Get task
item = queue.get()

# Get queue statistics
stats = queue.get_stats()
```

**Parameters:**
- `maxsize`: Queue maximum capacity (optional)
- `resource_limit`: Resource limit quantity (optional)

**Methods:**
- `put(item, priority=5)`: Add task to queue
- `get()`: Get highest priority task
- `get_stats()`: Return queue statistics
- `qsize()`: Return queue size

### ResourceController Resource Controller

Manages queue resource usage to prevent resource exhaustion.

```python
from nucleus.data.priority_queue import ResourceController

# Create resource controller
controller = ResourceController(limit=100)

# Request resource
if controller.acquire_resource():
    try:
        # Execute task
        pass
    finally:
        # Release resource
        controller.release_resource()
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