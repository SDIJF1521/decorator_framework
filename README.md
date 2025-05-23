# 使用说明

- `decorator_framework` 是一个用于自动注册类的元类（metaclass），当你定义继承它的类时，这些类将自动被注册到一个全局注册表中，方便在运行时动态调用或查找。

## 📁 模块结构
 - 该功能位于模块：

    - nucleus/Myclass.py - 核心元类实现

    - nucleus/dispatcher.py - 可能是使用注册表的调度逻辑（目前与 Myclass.py 内容重复）

## ✨ 功能简介
- 自动注册：类定义时自动加入注册表。

- 唯一性校验：要求每个类必须定义唯一的 fun_name。

- 快速访问：通过 ClassNucleus.get_registry() 获取所有注册类。

- 可测试性：提供 clear_registry() 方法清空注册表，方便单元测试。

## 📦 安装使用
- 确保你已经将 nucleus/ 模块路径包含在你的项目或 PYTHONPATH 中。

- ```python
    from nucleus.Myclass import ClassNucleus
    ```
## 🧩 如何使用
### ✅ 正确示例
- ```python

    from nucleus.Myclass import ClassNucleus
    
    class MyHandler(metaclass=ClassNucleus):
        fun_name = "my_handler"
    
        def handle(self):
            print("Handling in MyHandler")
  ```
- 当你定义上述类时，它会自动注册到 ClassNucleus 的注册表中。

### ❌ 错误示例
- ```python
    # 缺少 fun_name，会引发异常
    class InvalidHandler(metaclass=ClassNucleus):
        def handle(self):
            pass
    ```
-  ```python

    # 重复 fun_name，也会引发异常
    class HandlerA(metaclass=ClassNucleus):
        fun_name = "duplicate"
    
    class HandlerB(metaclass=ClassNucleus):
        fun_name = "duplicate"  # 报错：Duplicate fun_name: "duplicate"
     ```
## 🔍 接口说明
- `ClassNucleus.get_registry() -> dict`
- 返回当前注册的所有类：

  - ```python
      registry = ClassNucleus.get_registry()
      print(registry["my_handler"])  # 输出：<class '__main__.MyHandler'>
      ClassNucleus.clear_registry() -> None
      ```
- 清空所有注册类。注意：通常仅用于测试。


  - ```python

      ClassNucleus.clear_registry()\
      ```
