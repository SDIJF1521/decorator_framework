# 🎭 Decorator Framework

A powerful Python decorator framework providing **dependency injection**, **call chain interception**, **task management**, and **priority queue** advanced features. Supports event triggering, command processing, scheduled tasks, and regular expression matching.

## 1. Framework Core Features

### Dependency Injection System
- **Automatic Service Registration**: Register services automatically using `@service()` decorator
- **Interface Mapping**: Support interface to implementation class mapping
- **Lifecycle Management**: Support singleton and transient lifecycles
- **Constructor Injection**: Automatic dependency resolution and injection

### Call Chain System
- **Interceptor Pattern**: Support before, after, and exception interception
- **Context Passing**: Pass context information in the call chain
- **Performance Monitoring**: Built-in logging and metrics interceptors
- **Async Support**: Full support for async function call chains

### Task Management System
- **Task Scheduling**: Support timed and delayed task execution
- **Task Cancellation**: Provide graceful task cancellation mechanism
- **Concurrency Control**: Support maximum concurrency limits
- **Task Statistics**: Real-time monitoring of task execution status

### Priority Queue System
- **Intelligent Scheduling**: Task scheduling based on priority
- **Resource Control**: Memory and concurrency limits
- **Dynamic Adjustment**: Adjust queue parameters at runtime
- **Statistical Monitoring**: Detailed queue status statistics

## Documentation Languages
- [English Version](EN_README.md) - Current Document (English)
- [中文版本](README.md) - Chinese Documentation

## Quick Start

### Important: Decorator Usage
**All decorators must use the `.execute()` method!**

✅ **Correct usage:**
```python
@on("event_name").execute()  # ✅ Correct - must call .execute()
def handler_function(data):
    return f"Processing result: {data}"
```

❌ **Incorrect usage:**
```python
@on("event_name")  # ❌ Error - missing .execute()
def handler_function(data):
    return f"Processing result: {data}"
```

### 1. Install Framework
```bash
# Install from PyPI (recommended)
pip install decorator-framework

# Or install from source
pip install -r requirements.txt
```

### Important: Decorator Usage
**All decorators must use the `.execute()` method!**

✅ **Correct usage:**
```python
@on("event_name").execute()
def handler_function(data):
    return f"Processing result: {data}"
```

❌ **Incorrect usage:**
```python
@on("event_name")  # Missing .execute()
def handler_function(data):
    return f"Processing result: {data}"
```

### 2. Framework Core Features Demo

#### Dependency Injection System
```python
from nucleus import service, inject, get_dependency_container
from typing import Protocol

# Define interface
class IDataService(Protocol):
    async def get_data(self) -> str:
        ...

# Register service (singleton mode)
@service('singleton')
class DataService(IDataService):
    async def get_data(self) -> str:
        return "Hello from DataService!"

# Use dependency injection
@inject
async def process_data(data_service: IDataService) -> str:
    return await data_service.get_data()

# Usage example
async def test_di():
    result = await process_data()  # Auto inject dependency
    print(result)  # Output: Hello from DataService!
```

#### Call Chain System
```python
from nucleus import get_call_chain, ChainInterceptor, ChainContext

class LoggingInterceptor(ChainInterceptor):
    async def before_execute(self, context: ChainContext) -> None:
        print(f"Starting execution: {context.function_name}")
    
    async def after_execute(self, context: ChainContext) -> None:
        print(f"Execution completed: {context.function_name}")

# Use call chain
chain = get_call_chain()
chain.add_interceptor(LoggingInterceptor())

@chain.decorate
def my_function():
    return "processing result"
```

#### Task Management System
```python
from nucleus import get_task_manager, TaskCancellationToken

async def long_running_task(token: TaskCancellationToken) -> str:
    for i in range(10):
        token.throw_if_cancelled()  # Check cancellation signal
        await asyncio.sleep(0.1)
    return "Task completed"

# Use task manager
task_manager = get_task_manager()
task = await task_manager.create_task(long_running_task())
result = await task.wait_for_completion()
```

### 3. Decorator Usage
The framework provides four core decorators, all decorators must use `.execute()` method:
- `@on().execute()` - Regular event registration
- `@command_on().execute()` - Command registration (supports decision tree)
- `@time_on().execute()` - Scheduled tasks
- `@re_on().execute()` - Regular expression tasks

### 4. Project Structure
```
decorator_framework/
├── decorators/          # Core decorator modules
│   ├── __init__.py     # Package initialization
│   └── on.py           # Four decorator implementations
├── nucleus/            # Core framework modules
│   ├── __init__.py     # Package initialization, exports core classes
│   ├── dispatcher.py   # Four dispatcher implementations
│   ├── Myclass.py      # Core classes
│   ├── core/           # Core functionality submodules
│   │   ├── __init__.py
│   │   ├── chain.py    # Call chain system
│   │   ├── di.py       # Dependency injection system
│   │   ├── integration.py # Framework integration
│   │   └── task_manager.py # Task management
│   └── data/           # Data structure submodules
│       ├── __init__.py
│       ├── data_structure.py # Basic data structures
│       ├── priority_queue.py # Priority queue and resource control
│       └── tree.py      # Decision tree implementation
├── examples/           # Usage examples
│   ├── command_on_di_example.py    # Command + dependency injection example
│   ├── core_integration_demo.py    # Core integration demonstration
│   ├── on_di_example.py           # Decorator + dependency injection example
│   ├── priority_queue_example.py  # Priority queue example
│   ├── quick_start_example.py     # Quick start example
│   └── scheduler_integration_demo.py # Scheduler integration demonstration
├── tests/              # Test modules
│   ├── __init__.py    # Test package initialization
│   ├── test_basic.py  # Basic functionality tests
│   ├── test_core_integration.py # Core integration tests
│   ├── test_integration.py      # Integration tests
│   └── test_priority_queue.py   # Priority queue tests
├── complete_demo.py   # Complete functionality demonstration
├── setup.py           # Installation configuration
├── requirements.txt   # Dependency list
├── requirements-dev.txt # Development dependencies
├── MANIFEST.in        # Package manifest configuration
├── .gitignore         # Git ignore configuration
├── LICENSE            # MIT license
└── Documentation (EN/CN) # Complete bilingual documentation system
```

### 5. Quick Examples

#### Events and Commands Example
```python
import asyncio
from decorators.on import on, command_on
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher

# Regular event
@on("greet").execute()  # Note: Must use .execute()
def say_hello(name):
    return f"Hello, {name}!"

# Command processing
@command_on("add", "/add").execute()  # Note: Must use .execute()
def add_command(args=None):
    # Default parser passes arguments as args list
    if args and len(args) >= 2:
        a, b = int(args[0]), int(args[1])
        return f"{a} + {b} = {a + b}"
    return "Please provide two numbers, e.g.: /add 10 20"

async def main():
    # Event triggering
    dispatcher = EventDispatcher()
    result = await dispatcher.trigger_event("greet", "World")
    print(result)  # Output: Hello, World!
    
    # Command processing
    cmd_dispatcher = DecisionCommandDispatcher()
    result = await cmd_dispatcher.handle("/add 10 20")
    print(result)  # Output: 10 + 20 = 30

if __name__ == "__main__":
    asyncio.run(main())


### 5. Complete Feature Demonstration
Run `complete_demo.py` to see the complete framework feature demonstration:

```bash
python complete_demo.py
```

This demo includes:
- Dependency injection system demonstration
- Call chain interceptor functionality
- Task management and cancellation
- Priority queue intelligent scheduling
- Event system priority control
- Command system decision tree
- Regular expression task matching
- Async function support
- Resource limit management
- Queue statistics monitoring
```

### 6. Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_basic.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_priority_queue.py -v
```

### 3. Scheduled Tasks Example
```python
import asyncio
from decorators.on import time_on
from nucleus.dispatcher import TimeTaskScheduler

# Define scheduled tasks
@time_on("heartbeat", priority=1, interval=3).execute()  # Note: Must use .execute()
async def heartbeat_task():
    print("💓 Heartbeat check: System running normally")

@time_on("cleanup", priority=2, interval=5).execute()  # Note: Must use .execute()
async def cleanup_logs():
    print("🧹 Cleaning log files...")

async def main():
    scheduler = TimeTaskScheduler()
    await scheduler.start()
    
    print("Scheduled tasks started, running for 20 seconds...")
    await asyncio.sleep(20)
    
    await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## 2. Advanced Features in Detail

### Priority Queue System Integration
The framework integrates a priority queue system, supporting task priority management and resource control:

```python
from nucleus import PriorityQueue, ResourceController
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler

# Create event dispatcher with priority support
event_dispatcher = EventDispatcher()

# Register event handler (supports priority)
event_dispatcher.register_event("user_action", EventHandlerExample)

# Trigger high priority event
await event_dispatcher.trigger_event("user_action", priority=1, data={"user_id": 123})

# Get queue statistics
stats = event_dispatcher.get_event_queue_stats()
print(f"Event queue statistics: {stats}")
```

### Regular Expression Tasks (@re_on)
Trigger tasks by matching text content with regular expressions:

```python
from decorators.on import re_on
from nucleus.dispatcher import ReTaskScheduler

# 1. Define regex tasks
@re_on("greeting", "Greeting", r"你好|您好|hi|hello").execute()  # Note: Must use .execute()
def handle_greeting():
    return "Hello! How can I help you?"

@re_on("weather_query", "Weather query", r"天气|weather|temperature").execute()  # Note: Must use .execute()
def handle_weather():
    return "Today is sunny, temperature 25°C"

# 2. Use scheduler
async def test_regex():
    scheduler = ReTaskScheduler()
    
    # Match all related tasks
    results = await scheduler.match_content("Hello, what's the weather today?")
    print(results)  # Output: ['Hello! How can I help you?', 'Today is sunny, temperature 25°C']
```

### Decision Tree Command System (@command_on)
Intelligent command parsing system based on decision tree:

```python
from decorators.on import command_on
from nucleus.dispatcher import DecisionCommandDispatcher

# 1. Define commands
@command_on("help_cmd", "/help").execute()  # Note: Must use .execute()
def smart_help(args=None):
    return """🤖 Smart Assistant Command List:
/help - Display help information
/weather [city] - Query weather"""

@command_on("weather_cmd", "/weather").execute()  # Note: Must use .execute()
def weather_command(args=None):
    city = args[0] if args else "Beijing"
    return f"🌤️ {city} Weather: Today is sunny, temperature 25°C"

# 2. Use command dispatcher
async def test_commands():
    dispatcher = DecisionCommandDispatcher()
    
    print(await dispatcher.handle("/help"))
    print(await dispatcher.handle("/weather Shanghai"))
```

### Command Parameter Parsing
Support complex parameter parsing:

```python
@command_on("add", "/add", 
           arg_parser=lambda s: {"a": int(s.split()[0]), "b": int(s.split()[1])}
).execute()  # Note: Must use .execute()
def add_numbers(a: int, b: int):
    return f"{a} + {b} = {a + b}"

# Usage example
# /add 10 20  -> Returns "10 + 20 = 30"
```

### Async Support
The framework fully supports async functions, all decorators can be used with async functions:

```python
@on("async_event").execute()  # Note: Must use .execute()
async def async_handler(data):
    await asyncio.sleep(1)
    return f"Async processing completed: {data}"

@time_on("async_task", priority=1, interval=5).execute()  # Note: Must use .execute()
async def async_timed_task():
    await asyncio.sleep(0.5)
    print("Async scheduled task execution completed")
```

## 3. Parameter Reference

### @time_on Decorator Parameters
- `name`: Task name (must be unique)
- `priority`: Priority, smaller numbers have higher priority (default: 1)
- `interval`: Execution interval time (in seconds)

### @command_on Decorator Parameters
- `name`: Command name
- `command`: Command string (must start with "/")
- `aliases`: Command alias list (optional)
- `cooldown`: Cooldown time (seconds, optional)
- `arg_parser`: Parameter parsing function (optional)

### @re_on Decorator Parameters
- `name`: Task name
- `content`: Task description
- `pattern`: Regular expression pattern
- `priority`: Priority (default: 1)

## 4. Testing & Validation

### Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_basic.py -v
python -m pytest tests/test_core_integration.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_priority_queue.py -v
```

### Function Validation Examples
```python
import asyncio
from nucleus.dispatcher import *

async def test_all():
    # Test event system
    ed = EventDispatcher()
    print(await ed.trigger_event("greet", "Python"))
    
    # Test command system
    cd = DecisionCommandDispatcher()
    print(await cd.handle("/help"))
    
    # Test regex system
    rd = ReTaskScheduler()
    print(await rd.match_content("Hello World"))

asyncio.run(test_all())

# Additional framework tests
import asyncio

async def extended_tests():
    # Framework integration test
    from nucleus import enable_framework_integration
    enable_framework_integration()
    
    # Dependency injection test
    from nucleus import get_dependency_container
    container = get_dependency_container()
    print(f"Registered services: {len(container.services)}")
    
    # Event system test with priority
    dispatcher = EventDispatcher()
    result = await dispatcher.trigger_event("test_event", "test_data", priority=1)
    print(f"Event system test: {result}")

asyncio.run(extended_tests())
```

## 5. Debugging Tips

1. **View registered tasks**: Task list will be displayed when scheduler starts
2. **Task execution logs**: Execution information will be output when each task runs
3. **Error handling**: Framework will catch and display exceptions during task execution
4. **Priority debugging**: Observe task execution order by setting different priority values
5. **Dependency injection debugging**: Use `get_dependency_container()` to view registered services
6. **Call chain debugging**: Use interceptors to record detailed execution flow

## 6. Contributing

Issues and Pull Requests are welcome!

## 7. License

MIT License

## 8. Documentation System

### Core Documentation
- **Main Documentation**: [EN_README.md](EN_README.md) | [README.md](README.md) - Framework introduction and quick start
- **API Reference**: [API_REFERENCE_EN.md](API_REFERENCE_EN.md) | [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- **Best Practices**: [BEST_PRACTICES_EN.md](BEST_PRACTICES_EN.md) | [BEST_PRACTICES.md](BEST_PRACTICES.md) - Development guidelines

### Deployment & Testing
- **Production Guide**: [PRODUCTION_DEPLOYMENT_GUIDE_EN.md](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) | [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md) - Deployment instructions
- **Test Guide**: [RUN_TESTS_EN.md](RUN_TESTS_EN.md) | [RUN_TESTS.md](RUN_TESTS.md) - Testing documentation
- **PyPI Upload Guide**: [PYPI_UPLOAD_GUIDE.md](PYPI_UPLOAD_GUIDE.md) - Package publishing guide

### Usage Examples
- **Complete Demo**: `complete_demo.py` - Full framework feature demonstration
- **Quick Start**: `examples/quick_start_example.py` - Quick start example
- **Dependency Injection**: `examples/on_di_example.py` - Decorator + dependency injection example
- **Priority Queue**: `examples/priority_queue_example.py` - Queue system demonstration