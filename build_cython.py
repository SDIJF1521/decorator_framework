#!/usr/bin/env python3
"""
Cython编译脚本
编译除了cs.py和test_re_task.py之外的所有Python文件
"""

import os
import sys
import shutil
from pathlib import Path
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 需要排除的文件
EXCLUDED_FILES = {
    'cs.py',
    'test_re_task.py',
    'build_cython.py',
    'setup.py'
}

# 需要编译的Python文件
def find_python_files():
    """查找需要编译的Python文件"""
    python_files = []
    
    # 检查decorators目录
    decorators_dir = PROJECT_ROOT / 'decorators'
    if decorators_dir.exists():
        for py_file in decorators_dir.glob('*.py'):
            if py_file.name not in EXCLUDED_FILES:
                python_files.append(str(py_file))
    
    # 检查nucleus目录
    nucleus_dir = PROJECT_ROOT / 'nucleus'
    if nucleus_dir.exists():
        for py_file in nucleus_dir.glob('*.py'):
            if py_file.name not in EXCLUDED_FILES:
                python_files.append(str(py_file))
    
    return python_files

def clean_build():
    """清理之前的构建文件"""
    build_dirs = ['build', '__pycache__']
    for dir_name in build_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
    
    # 清理.pyc文件和.c文件
    for pycache in PROJECT_ROOT.rglob('__pycache__'):
        shutil.rmtree(pycache)
    
    for c_file in PROJECT_ROOT.rglob('*.c'):
        c_file.unlink()
    
    for pyd_file in PROJECT_ROOT.rglob('*.pyd'):
        pyd_file.unlink()
    
    for so_file in PROJECT_ROOT.rglob('*.so'):
        so_file.unlink()

def build_extensions():
    """构建Cython扩展"""
    python_files = find_python_files()
    
    if not python_files:
        print("没有找到需要编译的Python文件！")
        return
    
    print(f"找到 {len(python_files)} 个需要编译的Python文件:")
    for file in python_files:
        print(f"  - {file}")
    
    # 创建扩展模块
    extensions = []
    for py_file in python_files:
        py_path = Path(py_file)
        module_name = py_path.parent.name + '.' + py_path.stem if py_path.parent.name in ['decorators', 'nucleus'] else py_path.stem
        
        extensions.append(
            Extension(
                name=module_name,
                sources=[py_file],
                include_dirs=[np.get_include()],
                define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
                language='c++'
            )
        )
    
    # 编译设置
    setup(
        name="decorator_framework_compiled",
        ext_modules=cythonize(
            extensions,
            compiler_directives={
                'language_level': 3,
                'embedsignature': True,
                'boundscheck': False,
                'wraparound': False,
                'cdivision': True,
                'profile': False,
                'linetrace': False
            },
            build_dir="build"
        ),
        zip_safe=False,
        script_args=['build_ext', '--inplace']
    )

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        print("清理构建文件...")
        clean_build()
        print("清理完成！")
    else:
        print("开始编译Python文件...")
        clean_build()
        build_extensions()
        print("编译完成！")