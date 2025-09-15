#!/usr/bin/env python3
"""
性能对比测试：编译前(.py) vs 编译后(.pyd)
"""

import time
import os
import sys
import shutil
import tempfile
from pathlib import Path

class PerformanceTester:
    def __init__(self):
        self.results = {}
        
    def create_py_only_environment(self):
        """创建只有.py文件的环境用于测试"""
        temp_dir = tempfile.mkdtemp(prefix="py_test_")
        
        # 复制必要的.py文件
        dirs_to_copy = ["decorators", "nucleus"]
        files_to_copy = ["cs.py", "test_re_task.py"]
        
        for dir_name in dirs_to_copy:
            src_dir = Path(dir_name)
            dst_dir = Path(temp_dir) / dir_name
            dst_dir.mkdir(exist_ok=True)
            
            # 只复制.py文件
            for py_file in src_dir.glob("*.py"):
                shutil.copy2(py_file, dst_dir)
        
        for file_name in files_to_copy:
            if os.path.exists(file_name):
                shutil.copy2(file_name, Path(temp_dir) / file_name)
                
        return temp_dir
    
    def create_pyd_only_environment(self):
        """创建只有.pyd文件的环境用于测试"""
        temp_dir = tempfile.mkdtemp(prefix="pyd_test_")
        
        # 复制必要的.pyd文件
        dirs_to_copy = ["decorators", "nucleus"]
        files_to_copy = ["cs.py", "test_re_task.py"]
        
        for dir_name in dirs_to_copy:
            src_dir = Path(dir_name)
            dst_dir = Path(temp_dir) / dir_name
            dst_dir.mkdir(exist_ok=True)
            
            # 只复制.pyd文件
            for pyd_file in src_dir.glob("*.pyd"):
                shutil.copy2(pyd_file, dst_dir)
        
        for file_name in files_to_copy:
            if os.path.exists(file_name):
                shutil.copy2(file_name, Path(temp_dir) / file_name)
                
        return temp_dir
    
    def measure_import_time(self, test_dir, test_name):
        """测量模块导入时间"""
        original_cwd = os.getcwd()
        
        try:
            os.chdir(test_dir)
            
            # 清除模块缓存
            modules_to_clear = [
                'decorators', 'nucleus', 'decorators.on', 
                'nucleus.dispatcher', 'nucleus.Myclass'
            ]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            start_time = time.perf_counter()
            
            # 测试导入
            from decorators.on import on, command_on, time_on, re_on
            from nucleus.dispatcher import EventDispatcher, DecisionCommandDispatcher, TimeTaskScheduler, ReTaskScheduler
            from nucleus import Myclass
            
            import_time = time.perf_counter() - start_time
            
            return import_time
            
        finally:
            os.chdir(original_cwd)
    
    def measure_function_calls(self, test_dir, test_name):
        """测量函数调用性能"""
        original_cwd = os.getcwd()
        
        try:
            os.chdir(test_dir)
            
            # 清除模块缓存并重新导入
            modules_to_clear = [
                'decorators', 'nucleus', 'decorators.on', 
                'nucleus.dispatcher', 'nucleus.Myclass'
            ]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            from decorators.on import on
            from nucleus.dispatcher import EventDispatcher
            
            # 预热
            test_event = on("test").execute()
            
            # 测试函数调用性能
            iterations = 10000
            start_time = time.perf_counter()
            
            for i in range(iterations):
                decorator = on(f"event_{i}").execute()
                
            call_time = time.perf_counter() - start_time
            
            return call_time, iterations
            
        finally:
            os.chdir(original_cwd)
    
    def measure_decorator_creation(self, test_dir, test_name):
        """测量装饰器创建性能"""
        original_cwd = os.getcwd()
        
        try:
            os.chdir(test_dir)
            
            # 清除模块缓存并重新导入
            modules_to_clear = [
                'decorators', 'nucleus', 'decorators.on', 
                'nucleus.dispatcher', 'nucleus.Myclass'
            ]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            from decorators.on import on, time_on, command_on
            
            # 测试装饰器创建性能
            iterations = 5000
            start_time = time.perf_counter()
            
            for i in range(iterations):
                decorator = time_on(f"task_{i}", priority=1, interval=5)
                
            creation_time = time.perf_counter() - start_time
            
            return creation_time, iterations
            
        finally:
            os.chdir(original_cwd)
    
    def run_all_tests(self):
        """运行所有性能测试"""
        print("🚀 开始性能对比测试...\n")
        
        # 创建测试环境
        py_dir = self.create_py_only_environment()
        pyd_dir = self.create_pyd_only_environment()
        
        try:
            test_cases = [
                ("模块导入时间", self.measure_import_time),
                ("函数调用性能", self.measure_function_calls),
                ("装饰器创建性能", self.measure_decorator_creation)
            ]
            
            for test_name, test_func in test_cases:
                print(f"📊 测试: {test_name}")
                
                # 测试.py版本
                py_result = test_func(py_dir, "py")
                if isinstance(py_result, tuple):
                    py_time, *py_extra = py_result
                else:
                    py_time = py_result
                    py_extra = []
                
                # 测试.pyd版本
                pyd_result = test_func(pyd_dir, "pyd")
                if isinstance(pyd_result, tuple):
                    pyd_time, *pyd_extra = pyd_result
                else:
                    pyd_time = pyd_result
                    pyd_extra = []
                
                # 计算性能提升
                improvement = ((py_time - pyd_time) / py_time) * 100
                
                self.results[test_name] = {
                    'py_time': py_time,
                    'pyd_time': pyd_time,
                    'improvement': improvement,
                    'iterations': pyd_extra[0] if pyd_extra else None
                }
                
                if pyd_extra:
                    print(f"  .py版本: {py_time:.4f}s ({pyd_extra[0]}次操作)")
                    print(f"  .pyd版本: {pyd_time:.4f}s ({pyd_extra[0]}次操作)")
                else:
                    print(f"  .py版本: {py_time:.4f}s")
                    print(f"  .pyd版本: {pyd_time:.4f}s")
                
                print(f"  性能提升: {improvement:.1f}%")
                print()
                
        finally:
            # 清理临时目录
            shutil.rmtree(py_dir, ignore_errors=True)
            shutil.rmtree(pyd_dir, ignore_errors=True)
    
    def print_summary(self):
        """打印性能总结"""
        print("📈 性能对比总结")
        print("=" * 50)
        
        total_improvement = 0
        count = 0
        
        for test_name, data in self.results.items():
            print(f"{test_name}:")
            print(f"  性能提升: {data['improvement']:.1f}%")
            
            if data['iterations']:
                py_per_op = (data['py_time'] / data['iterations']) * 1000000
                pyd_per_op = (data['pyd_time'] / data['iterations']) * 1000000
                print(f"  每次操作耗时: .py={py_per_op:.2f}μs, .pyd={pyd_per_op:.2f}μs")
            
            total_improvement += data['improvement']
            count += 1
            print()
        
        avg_improvement = total_improvement / count
        print(f"🎯 平均性能提升: {avg_improvement:.1f}%")
        print("=" * 50)

def main():
    tester = PerformanceTester()
    tester.run_all_tests()
    tester.print_summary()

if __name__ == "__main__":
    main()