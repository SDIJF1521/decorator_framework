# Test Running Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### 2. Run Tests

#### Method 1: Using pytest (Recommended)
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_basic.py -v
python -m pytest tests/test_integration.py -v

# Run specific test class
python -m pytest tests/test_basic.py::TestBasicFunctionality -v
```

#### Method 2: Run test scripts directly
```bash
# Run simple function test
python test_correct_usage.py

# Run old test suite (if exists)
python tests/test_correct_framework.py
```

## Test Structure

### Test File Description
- `tests/test_basic.py` - Basic functionality tests (new)
- `tests/test_integration.py` - Integration tests (new)
- `tests/test_correct_framework.py` - Complete pytest test suite (old)
- `test_correct_usage.py` - Simple function verification script

### Test Categories
- **TestEventSystem**: Event system tests
- **TestTimeScheduler**: Scheduled task scheduler tests  
- **TestReSystem**: Regular expression system tests
- **TestIntegration**: Integration tests

## Common Issues and Solutions

### 1. Module Import Error
If you encounter `ModuleNotFoundError: No module named 'decorators'`, the test file has automatically handled the path issue.

### 2. Decorator Usage Format
Correct decorator usage format:
```python
@on("event_name").execute()
def handler_function(data):
    return f"Processing result: {data}"
```

### 3. Event Triggering
```python
from nucleus.dispatcher import EventDispatcher

dispatcher = EventDispatcher()
result = asyncio.run(dispatcher.trigger_event("event_name", "parameter"))
```

## Test Coverage

Current test coverage:
- Decorator import and usage
- Decorator `.execute()` method
- Basic event registration
- Multiple decorators used simultaneously
- Decorator and scheduler integration
- Module import verification

## Verification Success

All tests have passed:
```
====================================================== test session starts =====================================================
collected 7 items
tests/test_basic.py::TestBasicFunctionality::test_dispatcher_import PASSED
tests/test_basic.py::TestBasicFunctionality::test_myclass_import PASSED
tests/test_basic.py::TestBasicFunctionality::test_nucleus_modules_available PASSED
tests/test_basic.py::TestBasicFunctionality::test_on_decorator_basic PASSED
tests/test_basic.py::TestBasicFunctionality::test_on_decorator_import PASSED
tests/test_integration.py::TestIntegration::test_decorator_and_dispatcher_integration PASSED
tests/test_integration.py::TestIntegration::test_multiple_decorators PASSED
======================================================= 7 passed in 0.12s ======================================================
```

## Document Navigation

- [中文测试指南](RUN_TESTS.md) - Chinese Test Guide
- [English README](EN_README.md) - English Documentation
- [中文README](README.md) - Chinese Documentation
- [API Reference](API_REFERENCE_EN.md) - API Documentation
- [Best Practices](BEST_PRACTICES_EN.md) - Best Practices Guide
- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) - Production Deployment

### Framework Documentation
- **Main Documentation**: [EN_README.md](EN_README.md) | [README.md](README.md)
- **API Reference**: [API_REFERENCE_EN.md](API_REFERENCE_EN.md) | [API_REFERENCE.md](API_REFERENCE.md)
- **Best Practices**: [BEST_PRACTICES_EN.md](BEST_PRACTICES_EN.md) | [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Production Guide**: [PRODUCTION_DEPLOYMENT_GUIDE_EN.md](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) | [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
- **Test Guide**: [RUN_TESTS_EN.md](RUN_TESTS_EN.md) | [RUN_TESTS.md](RUN_TESTS.md)

## Document Navigation

- [中文测试指南](RUN_TESTS.md) - Chinese Test Guide
- [English README](EN_README.md) - English Documentation
- [中文README](README.md) - Chinese Documentation
- [API Reference](API_REFERENCE_EN.md) - API Documentation
- [Best Practices](BEST_PRACTICES_EN.md) - Best Practices Guide
- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE_EN.md) - Production Deployment