#!/usr/bin/env python3
"""
验证实际加载的是.pyd文件还是.py文件
"""

import os
import sys

def verify_module_source():
    """验证模块的实际来源"""
    print("=== 验证模块加载来源 ===\n")
    
    # 验证decorators.on
    from decorators import on
    on_file = on.__file__
    print(f"decorators.on 模块来源:")
    print(f"  文件路径: {on_file}")
    print(f"  文件类型: {'.pyd' if on_file.endswith('.pyd') else '.py'}")
    print(f"  是否为编译模块: {on_file.endswith('.pyd')}")
    
    # 验证nucleus.dispatcher
    from nucleus import dispatcher
    dispatcher_file = dispatcher.__file__
    print(f"\nnucleus.dispatcher 模块来源:")
    print(f"  文件路径: {dispatcher_file}")
    print(f"  文件类型: {'.pyd' if dispatcher_file.endswith('.pyd') else '.py'}")
    print(f"  是否为编译模块: {dispatcher_file.endswith('.pyd')}")
    
    # 验证nucleus.Myclass
    from nucleus import Myclass
    Myclass_file = Myclass.__file__
    print(f"\nnucleus.Myclass 模块来源:")
    print(f"  文件路径: {Myclass_file}")
    print(f"  文件类型: {'.pyd' if Myclass_file.endswith('.pyd') else '.py'}")
    print(f"  是否为编译模块: {Myclass_file.endswith('.pyd')}")
    
    # 检查是否存在.py文件（用于对比）
    print("\n=== 文件系统检查 ===")
    
    decorators_on_py = os.path.join('decorators', 'on.py')
    decorators_on_pyd = os.path.join('decorators', 'on.cp310-win_amd64.pyd')
    
    nucleus_dispatcher_py = os.path.join('nucleus', 'dispatcher.py')
    nucleus_dispatcher_pyd = os.path.join('nucleus', 'dispatcher.cp310-win_amd64.pyd')
    
    nucleus_myclass_py = os.path.join('nucleus', 'Myclass.py')
    nucleus_myclass_pyd = os.path.join('nucleus', 'Myclass.cp310-win_amd64.pyd')
    
    files_to_check = [
        (decorators_on_py, "decorators/on.py"),
        (decorators_on_pyd, "decorators/on.cp310-win_amd64.pyd"),
        (nucleus_dispatcher_py, "nucleus/dispatcher.py"),
        (nucleus_dispatcher_pyd, "nucleus/dispatcher.cp310-win_amd64.pyd"),
        (nucleus_myclass_py, "nucleus/Myclass.py"),
        (nucleus_myclass_pyd, "nucleus/Myclass.cp310-win_amd64.pyd")
    ]
    
    for file_path, description in files_to_check:
        exists = os.path.exists(file_path)
        print(f"  {description}: {'存在' if exists else '不存在'}")

if __name__ == "__main__":
    verify_module_source()