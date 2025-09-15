# 测试运行指南

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements-dev.txt
```

### 2. 运行测试

#### 方式1: 使用pytest (推荐)
```bash
# 运行所有测试
python -m pytest tests/test_correct_framework.py -v

# 运行特定测试类
python -m pytest tests/test_correct_framework.py::TestEventSystem -v

# 运行特定测试方法
python -m pytest tests/test_correct_framework.py::TestEventSystem::test_basic_event_triggering -v
```

#### 方式2: 直接运行测试脚本
```bash
# 运行简单功能测试
python test_correct_usage.py

# 运行测试套件
python tests/test_correct_framework.py
```

## 测试结构

### 测试文件说明
- `tests/test_correct_framework.py` - 完整的pytest测试套件
- `test_correct_usage.py` - 简单的功能验证脚本
- `cs.py` - 框架使用示例

### 测试类别
- **TestEventSystem**: 事件系统测试
- **TestTimeScheduler**: 定时任务调度器测试  
- **TestReSystem**: 正则表达式系统测试
- **TestIntegration**: 集成测试

## 常见问题和解决方案

### 1. 模块导入错误
如果遇到 `ModuleNotFoundError: No module named 'decorators'`，测试文件已自动处理路径问题。

### 2. 装饰器使用方式
正确的装饰器使用格式：
```python
@on("event_name").execute()
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
- ✅ 事件注册和触发
- ✅ 异步函数支持
- ✅ 多参数事件
- ✅ 未知事件处理
- ✅ 定时任务调度
- ✅ 正则表达式匹配
- ✅ 集成工作流

## 验证成功

所有测试已通过：
```
============================= test session starts ==============================
collected 11 items
tests/test_correct_framework.py::TestEventSystem::test_event_registration PASSED
... (11个测试全部通过)
============================== 11 passed in 0.35s ===============================
```