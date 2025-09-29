# 测试运行指南

## 文档语言
- [English Version](RUN_TESTS_EN.md) - 英文测试指南
- [中文版本](RUN_TESTS.md) - 当前文档（中文测试指南）

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements-dev.txt
```

### 2. 运行测试

#### 方式1: 使用pytest (推荐)
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_basic.py -v
python -m pytest tests/test_integration.py -v

# 运行特定测试类
python -m pytest tests/test_basic.py::TestBasicFunctionality -v
```

#### 方式2: 直接运行测试脚本
```bash
# 运行简单功能测试
python test_correct_usage.py

# 运行旧的测试套件（如果存在）
python tests/test_correct_framework.py
```

## 测试结构

### 测试文件说明
- `tests/test_basic.py` - 基本功能测试（新）
- `tests/test_integration.py` - 集成测试（新）
- `tests/test_correct_framework.py` - 完整的pytest测试套件（旧）
- `test_correct_usage.py` - 简单的功能验证脚本

### 测试类别
- **TestEventSystem**: 事件系统测试
- **TestTimeScheduler**: 定时任务调度器测试  
- **TestReSystem**: 正则表达式系统测试
- **TestIntegration**: 集成测试

## 常见问题和解决方案

### 1. 模块导入错误
如果遇到 `ModuleNotFoundError: No module named 'decorators'`，测试文件已自动处理路径问题。

### 3. 装饰器使用方式
正确的装饰器使用格式（必须使用 `.execute()` 方法）：
```python
@on("event_name").execute()  # 注意：必须调用 .execute()
def handler_function(data):
    return f"处理结果: {data}"
```

### 3. 事件触发
```python
from nucleus.dispatcher import EventDispatcher

dispatcher = EventDispatcher()
result = asyncio.run(dispatcher.trigger_event("event_name", "参数"))
```

## 测试覆盖率

当前测试覆盖：
- ✅ 装饰器导入和使用
- ✅ 装饰器 `.execute()` 方法
- ✅ 基本事件注册
- ✅ 多个装饰器同时使用
- ✅ 装饰器与调度器集成
- ✅ 模块导入验证

## 验证成功

所有测试已通过：
```
====================================================== test session starts ======================================================
collected 7 items
tests\test_basic.py::TestBasicFunctionality::test_dispatcher_import PASSED
tests\test_basic.py::TestBasicFunctionality::test_myclass_import PASSED
tests\test_basic.py::TestBasicFunctionality::test_nucleus_modules_available PASSED
tests\test_basic.py::TestBasicFunctionality::test_on_decorator_basic PASSED
tests\test_basic.py::TestBasicFunctionality::test_on_decorator_import PASSED
tests\test_integration.py::TestIntegration::test_decorator_and_dispatcher_integration PASSED
tests\test_integration.py::TestIntegration::test_multiple_decorators PASSED
======================================================= 7 passed in 0.12s =======================================================
```