#!/usr/bin/env python3
"""
测试编译后的模块是否可以直接调用
"""

import sys
import os

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(__file__))

def test_compiled_modules():
    """测试编译后的模块"""
    print("测试编译后的模块...")
    
    try:
        # 测试decorators.on模块
        from decorators import on
        print("✓ decorators.on 模块加载成功")
        print(f"  模块类型: {type(on)}")
        print(f"  模块文件: {on.__file__}")
        
        # 测试nucleus.dispatcher模块
        from nucleus import dispatcher
        print("✓ nucleus.dispatcher 模块加载成功")
        print(f"  模块类型: {type(dispatcher)}")
        print(f"  模块文件: {dispatcher.__file__}")
        
        # 测试nucleus.Myclass模块
        from nucleus import Myclass
        print("✓ nucleus.Myclass 模块加载成功")
        print(f"  模块类型: {type(Myclass)}")
        print(f"  模块文件: {Myclass.__file__}")
        
        # 测试功能是否正常
        if hasattr(on, 'on'):
            print("✓ decorators.on.on 函数可用")
        
        if hasattr(dispatcher, 'Dispatcher'):
            print("✓ nucleus.dispatcher.Dispatcher 类可用")
        
        if hasattr(Myclass, 'MyClass'):
            print("✓ nucleus.Myclass.MyClass 类可用")
        
        print("\n所有编译后的模块都可以正常调用！")
        
    except ImportError as e:
        print(f"✗ 导入错误: {e}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

if __name__ == "__main__":
    test_compiled_modules()