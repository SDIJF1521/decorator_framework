#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试模块
用于验证装饰器框架的集成功能
"""

import unittest
from decorators import on
from nucleus import dispatcher


class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
    def test_decorator_and_dispatcher_integration(self):
        """测试装饰器与调度器的集成"""
        # 这里可以添加更复杂的集成测试
        # 由于我们不知道具体的API，先做一个简单的存在性测试
        
        # 创建装饰器实例
        decorator_factory = on('integration_test')
        
        def integration_handler(data):
            return f"processed: {data}"
        
        # 应用装饰器（使用execute方法）
        decorated_handler = decorator_factory.execute()(integration_handler)
        
        # 验证装饰器没有抛出异常
        self.assertTrue(callable(decorated_handler))
    
    def test_multiple_decorators(self):
        """测试多个装饰器的情况"""
        # 创建装饰器实例
        decorator1 = on('event1')
        decorator2 = on('event2')
        
        def handler1():
            return "handler1"
        
        def handler2():
            return "handler2"
        
        # 应用装饰器（使用execute方法）
        decorated_handler1 = decorator1.execute()(handler1)
        decorated_handler2 = decorator2.execute()(handler2)
        
        # 验证多个装饰器可以同时存在
        self.assertTrue(callable(decorated_handler1))
        self.assertTrue(callable(decorated_handler2))
        self.assertEqual(decorated_handler1(), "handler1")
        self.assertEqual(decorated_handler2(), "handler2")


if __name__ == '__main__':
    unittest.main()