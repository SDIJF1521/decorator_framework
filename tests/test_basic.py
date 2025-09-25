#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能测试模块
用于验证装饰器框架的核心功能
"""

import unittest
from decorators import on
from nucleus import dispatcher, Myclass


class TestBasicFunctionality(unittest.TestCase):
    """测试基本功能"""
    
    def test_on_decorator_import(self):
        """测试on装饰器导入"""
        self.assertIsNotNone(on)
        self.assertTrue(callable(on))
        # 验证on函数返回RegistryDecoratorTemplate对象
        decorator = on('test_event')
        self.assertIsNotNone(decorator)
        # RegistryDecoratorTemplate对象有execute方法
        self.assertTrue(hasattr(decorator, 'execute'))
        self.assertTrue(callable(decorator.execute))
    
    def test_dispatcher_import(self):
        """测试dispatcher模块导入"""
        self.assertIsNotNone(dispatcher)
    
    def test_myclass_import(self):
        """测试Myclass模块导入"""
        self.assertIsNotNone(Myclass)
    
    def test_on_decorator_basic(self):
        """测试on装饰器基本功能"""
        # 创建装饰器实例
        decorator_factory = on('test_event')
        
        def test_handler():
            return "handled"
        
        # 应用装饰器（使用execute方法）
        decorated_handler = decorator_factory.execute()(test_handler)
        
        # 验证装饰器应用成功
        self.assertTrue(callable(decorated_handler))
        self.assertEqual(decorated_handler(), "handled")
    
    def test_nucleus_modules_available(self):
        """测试nucleus模块可用性"""
        # 验证dispatcher和Myclass模块存在
        self.assertTrue(hasattr(dispatcher, '__name__'))
        self.assertTrue(hasattr(Myclass, '__name__'))


if __name__ == '__main__':
    unittest.main()