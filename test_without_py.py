#!/usr/bin/env python3
"""
测试在没有.py文件的情况下，是否只使用.pyd文件
"""

import os
import shutil
import sys

def backup_and_remove_py_files():
    """备份并移除.py文件"""
    
    # 创建备份目录
    backup_dir = "backup_py_files"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 需要备份的.py文件
    py_files = [
        "decorators/on.py",
        "nucleus/dispatcher.py", 
        "nucleus/Myclass.py"
    ]
    
    # 备份.py文件
    for py_file in py_files:
        if os.path.exists(py_file):
            backup_path = os.path.join(backup_dir, py_file.replace('/', '_'))
            shutil.copy2(py_file, backup_path)
            print(f"已备份: {py_file} -> {backup_path}")
            
            # 移除.py文件
            os.remove(py_file)
            print(f"已移除: {py_file}")

def test_import_without_py():
    """测试在没有.py文件的情况下导入"""
    print("\n=== 测试只使用.pyd文件 ===")
    
    try:
        # 清除已加载的模块缓存
        modules_to_clear = [
            'decorators.on', 'nucleus.dispatcher', 'nucleus.Myclass',
            'decorators', 'nucleus'
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # 重新导入
        from decorators import on
        from nucleus import dispatcher, Myclass
        
        print("✓ 成功从.pyd文件导入所有模块")
        print(f"  decorators.on: {on.__file__}")
        print(f"  nucleus.dispatcher: {dispatcher.__file__}")
        print(f"  nucleus.Myclass: {Myclass.__file__}")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def restore_py_files():
    """恢复.py文件"""
    backup_dir = "backup_py_files"
    
    if os.path.exists(backup_dir):
        for backup_file in os.listdir(backup_dir):
            if backup_file.endswith('.py'):
                # 从backup_file解析原始路径
                if 'on.py' in backup_file and 'decorators' in backup_file:
                    original_path = "decorators/on.py"
                elif 'dispatcher.py' in backup_file and 'nucleus' in backup_file:
                    original_path = "nucleus/dispatcher.py"
                elif 'Myclass.py' in backup_file and 'nucleus' in backup_file:
                    original_path = "nucleus/Myclass.py"
                else:
                    continue
                
                shutil.copy2(os.path.join(backup_dir, backup_file), original_path)
                print(f"已恢复: {original_path}")

if __name__ == "__main__":
    print("开始测试只使用.pyd文件...")
    
    # 备份并移除.py文件
    backup_and_remove_py_files()
    
    # 测试导入
    success = test_import_without_py()
    
    # 恢复.py文件（便于开发）
    restore_py_files()
    
    if success:
        print("\n✅ 验证成功：.pyd文件可以独立使用，无需.py文件")
    else:
        print("\n❌ 验证失败")