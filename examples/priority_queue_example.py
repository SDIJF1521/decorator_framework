"""
优先级队列使用示例
展示如何在框架中使用优先级队列进行资源控制
"""
import time
import threading
import sys
sys.path.insert(0, '.')
from nucleus.data.priority_queue import PriorityQueue


def basic_usage_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建优先级队列
    queue = PriorityQueue(max_size=10, max_memory_mb=5, name="任务队列")
    
    # 添加任务，优先级数字越小优先级越高
    queue.put("紧急任务1", priority=0)
    queue.put("普通任务1", priority=5)
    queue.put("紧急任务2", priority=0)
    queue.put("普通任务2", priority=5)
    
    print(f"队列大小: {queue.qsize()}")
    print(f"队列状态: {queue}")
    
    # 按优先级获取任务
    while not queue.empty():
        task = queue.get()
        print(f"处理任务: {task}")
    
    print()


def resource_control_example():
    """资源控制示例"""
    print("=== 资源控制示例 ===")
    
    # 创建资源受限的队列
    queue = PriorityQueue(max_size=3, max_memory_mb=1.0, name="资源受限队列")
    
    # 尝试添加不同大小的任务
    tasks = [
        ("小任务1", 0.3),
        ("小任务2", 0.3),
        ("小任务3", 0.3),
        ("小任务4", 0.3),  # 这个应该失败 - 超过内存限制
    ]
    
    for task_name, size in tasks:
        success = queue.put(task_name, priority=1, item_size_mb=size)
        print(f"添加任务 '{task_name}' (大小: {size}MB): {'成功' if success else '失败'}")
    
    print(f"当前队列大小: {queue.qsize()}")
    
    # 显示资源使用情况
    stats = queue.get_stats()
    resource_usage = stats['resource_usage']
    print(f"资源使用: {resource_usage['size_usage_percent']:.1f}% 大小, {resource_usage['memory_usage_percent']:.1f}% 内存")
    
    print()


def priority_management_example():
    """优先级管理示例"""
    print("=== 优先级管理示例 ===")
    
    queue = PriorityQueue(name="动态优先级队列")
    
    # 添加初始任务
    queue.put("低优先级任务", priority=5)
    queue.put("高优先级任务", priority=1)
    queue.put("中等优先级任务", priority=3)
    
    print("原始顺序:")
    for i, (task, priority) in enumerate(queue.get_all_items()):
        print(f"  {i+1}. {task} (优先级: {priority})")
    
    # 动态修改优先级
    queue.update_priority("中等优先级任务", 0)  # 提升到最高优先级
    
    print("\n修改优先级后:")
    for i, (task, priority) in enumerate(queue.get_all_items()):
        print(f"  {i+1}. {task} (优先级: {priority})")
    
    print("\n实际处理顺序:")
    while not queue.empty():
        task = queue.get()
        print(f"  处理: {task}")
    
    print()


def concurrent_access_example():
    """并发访问示例"""
    print("=== 并发访问示例 ===")
    
    queue = PriorityQueue(max_size=50, name="并发队列")
    results = []
    
    def producer(producer_id, num_tasks):
        """生产者线程"""
        for i in range(num_tasks):
            task_name = f"生产者{producer_id}-任务{i}"
            priority = i % 3  # 0, 1, 2
            if queue.put(task_name, priority=priority):
                print(f"  [生产者{producer_id}] 添加: {task_name} (优先级: {priority})")
            time.sleep(0.01)
    
    def consumer(consumer_id, num_tasks):
        """消费者线程"""
        for _ in range(num_tasks):
            task = queue.get(timeout=0.1)
            if task:
                results.append(task)
                print(f"  [消费者{consumer_id}] 获取: {task}")
            time.sleep(0.02)
    
    # 启动生产者和消费者线程
    producer_thread = threading.Thread(target=producer, args=(1, 10))
    consumer_thread = threading.Thread(target=consumer, args=(1, 8))
    
    producer_thread.start()
    consumer_thread.start()
    
    producer_thread.join()
    consumer_thread.join()
    
    print(f"\n共处理 {len(results)} 个任务")
    print(f"队列剩余: {queue.qsize()} 个任务")
    
    print()


def advanced_features_example():
    """高级功能示例"""
    print("=== 高级功能示例 ===")
    
    queue = PriorityQueue(name="高级功能队列")
    
    # 添加一些任务
    tasks = ["任务A", "任务B", "任务C", "任务D", "任务E"]
    for i, task in enumerate(tasks):
        queue.put(task, priority=i % 3)
    
    print(f"队列中的任务: {queue.get_all_items()}")
    
    # 查看即将处理的任务（不移除）
    next_task = queue.peek()
    print(f"下一个任务: {next_task}")
    print(f"查看后队列大小: {queue.qsize()}")  # 应该不变
    
    # 移除特定任务
    removed = queue.remove("任务C")
    print(f"移除任务C: {'成功' if removed else '失败'}")
    print(f"移除后队列中的任务: {queue.get_all_items()}")
    
    # 获取统计信息
    stats = queue.get_stats()
    print(f"\n队列统计:")
    print(f"  当前大小: {stats['current_size']}")
    print(f"  已处理总数: {stats['total_processed']}")
    print(f"  峰值大小: {stats['peak_size']}")
    print(f"  运行时间: {stats['uptime_seconds']:.1f} 秒")
    
    # 清空队列
    queue.clear()
    print(f"\n清空后队列大小: {queue.qsize()}")
    
    print()


def timeout_example():
    """超时功能示例"""
    print("=== 超时功能示例 ===")
    
    queue = PriorityQueue(name="超时测试队列")
    
    print("尝试从空队列获取任务（超时1秒）...")
    start_time = time.time()
    result = queue.get(timeout=1.0)
    end_time = time.time()
    
    print(f"结果: {result}")
    print(f"耗时: {end_time - start_time:.1f} 秒")
    
    # 立即添加任务并获取
    queue.put("快速任务")
    result = queue.get(timeout=1.0)
    print(f"立即获取结果: {result}")
    
    print()


if __name__ == "__main__":
    print("优先级队列使用示例")
    print("=" * 50)
    
    # 运行所有示例
    basic_usage_example()
    resource_control_example()
    priority_management_example()
    concurrent_access_example()
    advanced_features_example()
    timeout_example()
    
    print("所有示例完成！")
    
    # 性能测试
    print("\n=== 性能测试 ===")
    queue = PriorityQueue(name="性能测试队列")
    
    # 测试大量数据插入性能
    start_time = time.time()
    for i in range(1000):
        queue.put(f"任务{i}", priority=i % 10)
    insert_time = time.time() - start_time
    
    # 测试大量数据获取性能
    start_time = time.time()
    count = 0
    while not queue.empty():
        queue.get()
        count += 1
    get_time = time.time() - start_time
    
    print(f"插入1000个任务耗时: {insert_time:.3f} 秒")
    print(f"获取{count}个任务耗时: {get_time:.3f} 秒")
    print(f"总吞吐量: {1000 / (insert_time + get_time):.1f} 任务/秒")