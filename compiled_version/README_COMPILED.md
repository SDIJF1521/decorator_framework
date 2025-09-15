
# 使用编译后的模块示例

## 导入方式
```python
# 直接导入编译后的模块
from decorators.on import on, command_on, time_on, re_on
from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler, ReTaskScheduler

# 使用方式与之前完全相同
@on("test_event").execute()
def test_function():
    return "Hello from compiled module!"
```

## 验证使用的是.pyd文件
```python
import decorators.on
print(decorators.on.__file__)  # 应该显示 .pyd 文件路径
```

## 运行测试
```bash
python cs.py  # 现在使用的是编译后的.pyd文件
```
