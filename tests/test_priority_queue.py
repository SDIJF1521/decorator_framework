"""
优先级队列测试
"""
import pytest
import time
from nucleus.data.priority_queue import PriorityQueue, PriorityQueueItem, ResourceController


class TestPriorityQueueItem:
    """测试优先级队列项"""
    
    def test_item_creation(self):
        """测试项的创建"""
        item = PriorityQueueItem("test_data", priority=1)
        assert item.data == "test_data"
        assert item.priority == 1
        assert item.retry_count == 0
        assert item.max_retries == 3
    
    def test_item_comparison(self):
        """测试项的比较"""
        item1 = PriorityQueueItem("data1", priority=1)
        time.sleep(0.01)  # 确保时间戳不同
        item2 = PriorityQueueItem("data2", priority=2)
        
        assert item1 < item2  # 优先级1 < 优先级2
        assert not (item2 < item1)
    
    def test_item_equal_priority_comparison(self):
        """测试相同优先级的比较"""
        item1 = PriorityQueueItem("data1", priority=1)
        time.sleep(0.01)  # 确保时间戳不同
        item2 = PriorityQueueItem("data2", priority=1)
        
        assert item1 < item2  # 先创建的优先级更高


class TestResourceController:
    """测试资源控制器"""
    
    def test_resource_controller_initialization(self):
        """测试资源控制器初始化"""
        controller = ResourceController(max_size=100, max_memory_mb=50)
        assert controller.max_size == 100
        assert controller.max_memory_mb == 50
        assert controller.current_size == 0
        assert controller.current_memory_mb == 0
    
    def test_can_add_item(self):
        """测试是否可以添加项"""
        controller = ResourceController(max_size=2, max_memory_mb=1.0)
        
        assert controller.can_add_item(0.5) == True
        controller.add_item(0.5)
        assert controller.current_size == 1
        assert controller.current_memory_mb == 0.5
        
        assert controller.can_add_item(0.3) == True
        controller.add_item(0.3)
        assert controller.current_size == 2
        assert controller.current_memory_mb == 0.8
        
        # 超过大小限制
        assert controller.can_add_item(0.1) == False
        
        # 超过内存限制
        controller2 = ResourceController(max_size=10, max_memory_mb=1.0)
        controller2.add_item(0.9)
        assert controller2.can_add_item(0.2) == False
    
    def test_remove_item(self):
        """测试移除项"""
        controller = ResourceController()
        controller.add_item(0.5)
        controller.add_item(0.3)
        assert controller.current_size == 2
        assert controller.current_memory_mb == 0.8
        
        controller.remove_item(0.3)
        assert controller.current_size == 1
        assert controller.current_memory_mb == 0.5
        
        # 测试不会变成负数
        controller.remove_item(1.0)
        assert controller.current_size == 0
        assert controller.current_memory_mb == 0.0
    
    def test_get_resource_usage(self):
        """测试获取资源使用情况"""
        controller = ResourceController(max_size=100, max_memory_mb=50)
        controller.add_item(10)
        controller.add_item(5)
        
        usage = controller.get_resource_usage()
        assert usage['current_size'] == 2
        assert usage['max_size'] == 100
        assert usage['size_usage_percent'] == 2.0
        assert usage['current_memory_mb'] == 15.0
        assert usage['max_memory_mb'] == 50
        assert usage['memory_usage_percent'] == 30.0


class TestPriorityQueue:
    """测试优先级队列"""
    
    def test_queue_initialization(self):
        """测试队列初始化"""
        queue = PriorityQueue(max_size=100, max_memory_mb=50, name="test_queue")
        assert queue.name == "test_queue"
        assert queue.empty() == True
        assert len(queue) == 0
    
    def test_put_and_get_basic(self):
        """测试基本的put和get操作"""
        queue = PriorityQueue()
        
        assert queue.put("item1", priority=1) == True
        assert queue.put("item2", priority=2) == True
        assert queue.qsize() == 2
        
        # 获取优先级最高的项
        item = queue.get()
        assert item == "item1"  # 优先级1比优先级2高
        assert queue.qsize() == 1
    
    def test_priority_ordering(self):
        """测试优先级排序"""
        queue = PriorityQueue()
        
        queue.put("low", priority=5)
        queue.put("high", priority=1)
        queue.put("medium", priority=3)
        queue.put("highest", priority=0)
        
        assert queue.get() == "highest"  # 优先级0
        assert queue.get() == "high"     # 优先级1
        assert queue.get() == "medium"   # 优先级3
        assert queue.get() == "low"      # 优先级5
    
    def test_same_priority_fifo(self):
        """测试相同优先级的FIFO顺序"""
        queue = PriorityQueue()
        
        queue.put("first", priority=1)
        time.sleep(0.01)  # 确保时间戳不同
        queue.put("second", priority=1)
        time.sleep(0.01)
        queue.put("third", priority=1)
        
        assert queue.get() == "first"
        assert queue.get() == "second"
        assert queue.get() == "third"
    
    def test_peek_operation(self):
        """测试peek操作"""
        queue = PriorityQueue()
        
        assert queue.peek() == None  # 空队列
        
        queue.put("item1", priority=1)
        queue.put("item2", priority=2)
        
        assert queue.peek() == "item1"  # 查看但不移除
        assert queue.qsize() == 2       # 队列大小不变
    
    def test_remove_operation(self):
        """测试移除操作"""
        queue = PriorityQueue()
        
        queue.put("item1", priority=1)
        queue.put("item2", priority=2)
        queue.put("item3", priority=3)
        
        assert queue.remove("item2") == True
        assert queue.qsize() == 2
        
        assert queue.get() == "item1"
        assert queue.get() == "item3"
        assert queue.get() == None  # 队列已空
    
    def test_update_priority(self):
        """测试更新优先级"""
        queue = PriorityQueue()
        
        queue.put("item1", priority=5)
        queue.put("item2", priority=3)
        
        queue.update_priority("item1", 1)  # 将item1的优先级提高到1
        
        assert queue.get() == "item1"  # 现在item1优先级更高
        assert queue.get() == "item2"
    
    def test_resource_limit(self):
        """测试资源限制"""
        queue = PriorityQueue(max_size=2, max_memory_mb=1.0)
        
        assert queue.put("item1", item_size_mb=0.4) == True
        assert queue.put("item2", item_size_mb=0.4) == True
        assert queue.put("item3", item_size_mb=0.4) == False  # 超过资源限制
        
        assert queue.qsize() == 2
    
    def test_get_with_timeout(self):
        """测试带超时的get操作"""
        queue = PriorityQueue()
        
        # 空队列，立即返回None
        assert queue.get(timeout=0.1) == None
        
        queue.put("item1")
        assert queue.get(timeout=1.0) == "item1"
    
    def test_clear_operation(self):
        """测试清空操作"""
        queue = PriorityQueue()
        
        queue.put("item1")
        queue.put("item2")
        assert queue.qsize() == 2
        
        queue.clear()
        assert queue.qsize() == 0
        assert queue.empty() == True
    
    def test_stats(self):
        """测试统计功能"""
        queue = PriorityQueue(name="test_stats")
        
        queue.put("item1")
        queue.put("item2")
        queue.get()
        
        stats = queue.get_stats()
        assert stats['current_size'] == 1
        assert stats['total_processed'] == 1
        assert stats['peak_size'] == 2
        assert 'resource_usage' in stats
        assert 'uptime_seconds' in stats
        assert stats['name'] == "test_stats"
    
    def test_iteration(self):
        """测试迭代功能"""
        queue = PriorityQueue()
        
        queue.put("item3", priority=3)
        queue.put("item1", priority=1)
        queue.put("item2", priority=2)
        
        items = list(queue)
        assert items == ["item1", "item2", "item3"]  # 按优先级顺序
    
    def test_get_all_items(self):
        """测试获取所有项"""
        queue = PriorityQueue()
        
        queue.put("item1", priority=1)
        queue.put("item2", priority=2)
        
        items = queue.get_all_items()
        assert len(items) == 2
        assert ("item1", 1) in items
        assert ("item2", 2) in items
    
    def test_len_function(self):
        """测试len函数"""
        queue = PriorityQueue()
        
        assert len(queue) == 0
        queue.put("item1")
        assert len(queue) == 1
        queue.put("item2")
        assert len(queue) == 2
    
    def test_repr_function(self):
        """测试repr函数"""
        queue = PriorityQueue(name="test_queue")
        queue.put("item1")
        
        repr_str = repr(queue)
        assert "PriorityQueue" in repr_str
        assert "test_queue" in repr_str
        assert "size=1" in repr_str


class TestPriorityQueueIntegration:
    """集成测试"""
    
    def test_concurrent_operations(self):
        """测试并发操作"""
        import threading
        
        queue = PriorityQueue(max_size=100)
        results = []
        
        def producer():
            for i in range(50):
                queue.put(f"item_{i}", priority=i % 5)
        
        def consumer():
            for _ in range(30):
                item = queue.get(timeout=0.1)
                if item:
                    results.append(item)
        
        # 启动生产者和消费者线程
        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)
        
        producer_thread.start()
        consumer_thread.start()
        
        producer_thread.join()
        consumer_thread.join()
        
        # 验证结果
        assert len(results) > 0
        assert queue.qsize() >= 0
    
    def test_resource_control_integration(self):
        """测试资源控制集成"""
        queue = PriorityQueue(max_size=5, max_memory_mb=2.0)
        
        # 添加多个项
        for i in range(5):
            assert queue.put(f"item_{i}", item_size_mb=0.3) == True
        
        # 资源已满
        assert queue.put("overflow_item", item_size_mb=0.3) == False
        
        # 释放一些资源
        queue.get()
        
        # 现在可以添加新项
        assert queue.put("new_item", item_size_mb=0.3) == True
        
        stats = queue.get_stats()
        assert stats['current_size'] == 5
        assert stats['resource_usage']['current_size'] == 5


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])