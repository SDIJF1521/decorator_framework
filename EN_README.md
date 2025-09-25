# Decorator Framework

A lightweight, easy-to-use Python decorator framework supporting event triggering, command processing, scheduled tasks, and regular expression matching.

## 🌐 Documentation Languages
- [English Version](EN_README.md) - Current Document (English)
- [中文版本](README.md) - Chinese Documentation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### ⚠️ Important: Decorator Usage
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

### 2. Basic Usage
The framework provides four core decorators:
- `@on()` - Regular event registration
- `@command_on()` - Command registration (supports decision tree)
- `@time_on()` - Scheduled tasks
- `@re_on()` - Regular expression tasks

### 3. Project Structure
```
decorator_framework/
├── decorators/
│   ├── __init__.py    # Decorator module initialization
│   └── on.py          # Four decorator implementations
├── nucleus/
│   ├── __init__.py
│   ├── dispatcher.py   # Four dispatchers
│   └── Myclass.py     # Core classes
├── tests/
│   ├── __init__.py
│   ├── test_basic.py  # Basic functionality tests
│   └── test_integration.py # Integration tests
├── test_timer_demo.py  # Scheduled task example
├── test_re_decision_demo.py  # Regex + decision tree example
├── cs.py              # Comprehensive example
├── requirements.txt   # Project dependencies
└── README.md
```

## 📋 Complete Examples

### 1. Events and Commands Example
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
```

### 2. Scheduled Tasks Example
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

## 🔧 Advanced Usage

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

## 📊 Parameter Reference

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

## 🧪 Testing

### Run All Tests
```bash
# Run complete test suite
python -m pytest tests/ -v
```

### Manual Testing
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
```

## 📝 Debugging Tips

1. **View registered tasks**: Task list will be displayed when scheduler starts
2. **Task execution logs**: Execution information will be output when each task runs
3. **Error handling**: Framework will catch and display exceptions during task execution
4. **Priority debugging**: Observe task execution order by setting different priority values

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 🔗 Document Navigation

### Framework Documentation
- **Main Documentation**: [EN_README.md](EN_README.md) | [README.md](README.md)
- **API Reference**: [API_REFERENCE_EN.md](API_REFERENCE_EN.md) | [API_REFERENCE.md](API_REFERENCE.md)
- **Best Practices**: [BEST_PRACTICES_EN.md](BEST_PRACTICES_EN.md) | [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Production Guide**: [PRODUCTION_DEPLOYMENT_GUIDE_EN.md](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) | [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
- **Test Guide**: [RUN_TESTS_EN.md](RUN_TESTS_EN.md) | [RUN_TESTS.md](RUN_TESTS.md)

### Quick Links
- [English API Reference](API_REFERENCE_EN.md) - Complete API documentation
- [English Best Practices](BEST_PRACTICES_EN.md) - Development guidelines
- [English Production Guide](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) - Deployment instructions
- [English Test Guide](RUN_TESTS_EN.md) - Testing documentation