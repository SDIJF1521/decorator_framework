from typing import Any, List, Tuple, Optional, Iterator
from heapq import heappush, heappop, heapify
from threading import Lock
import time
from .data_structure import DataStructure

class PriorityQueueItem:
    """优先级队列项，封装数据和优先级"""
    
    def __init__(self, data: Any, priority: int = 0, timestamp: Optional[float] = None):
        self.data = data
        self.priority = priority  # 优先级
        self.timestamp = timestamp or time.time()  # 入队时间，用于相同优先级的FIFO
        self.retry_count = 0  # 重试次数
        self.max_retries = 3  # 最大重试次数
    
    def __lt__(self, other: 'PriorityQueueItem') -> bool:
        """比较函数：先比较优先级，再比较时间戳"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp
    
    def __eq__(self, other: 'PriorityQueueItem') -> bool:
        return (self.priority == other.priority and 
                self.timestamp == other.timestamp and
                self.data == other.data)
    
    def __repr__(self) -> str:
        return f"PriorityQueueItem(data={self.data}, priority={self.priority}, retry={self.retry_count})"


class ResourceController:
    """资源控制器，管理队列资源使用"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self.current_size = 0
        self.current_memory_mb = 0
        self._lock = Lock()
    
    def can_add_item(self, item_size_mb: float = 0.1) -> bool:
        """检查是否可以添加新项"""
        with self._lock:
            if self.current_size >= self.max_size:
                return False
            if self.current_memory_mb + item_size_mb > self.max_memory_mb:
                return False
            return True
    
    def add_item(self, item_size_mb: float = 0.1):
        """添加项时更新资源计数"""
        with self._lock:
            self.current_size += 1
            self.current_memory_mb += item_size_mb
    
    def remove_item(self, item_size_mb: float = 0.1):
        """移除项时更新资源计数"""
        with self._lock:
            self.current_size = max(0, self.current_size - 1)
            self.current_memory_mb = max(0.0, self.current_memory_mb - item_size_mb)
            return True
    
    def get_resource_usage(self) -> dict:
        """获取资源使用情况"""
        with self._lock:
            return {
                'current_size': self.current_size,
                'max_size': self.max_size,
                'size_usage_percent': (self.current_size / self.max_size) * 100,
                'current_memory_mb': self.current_memory_mb,
                'max_memory_mb': self.max_memory_mb,
                'memory_usage_percent': (self.current_memory_mb / self.max_memory_mb) * 100
            }


class PriorityQueue(DataStructure):
    """线程安全的优先级队列，用于框架资源控制"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100, name: str = ""):
        self.name = name
        self._queue: List[PriorityQueueItem] = []
        self._lock = Lock()
        self._resource_controller = ResourceController(max_size, max_memory_mb)
        self._stats = {
            'total_processed': 0,
            'total_failed': 0,
            'peak_size': 0,
            'created_at': time.time()
        }
    
    def put(self, data: Any, priority: int = 0, item_size_mb: float = 0.1) -> bool:
        """
        添加项到队列
        
        Args:
            data: 要存储的数据
            priority: 优先级，数字越小优先级越高（默认0）
            item_size_mb: 项的预估内存大小（MB）
            
        Returns:
            bool: 是否成功添加
        """
        if not self._resource_controller.can_add_item(item_size_mb):
            return False
        
        with self._lock:
            item = PriorityQueueItem(data, priority)
            heappush(self._queue, item)
            self._resource_controller.add_item(item_size_mb)
            
            # 更新统计
            current_size = len(self._queue)
            self._stats['peak_size'] = max(self._stats['peak_size'], current_size)
            
        return True
    
    def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        从队列获取优先级最高的项
        
        Args:
            timeout: 超时时间（秒），None表示不等待
            
        Returns:
            数据或None（如果队列为空或超时）
        """
        if timeout is not None:
            start_time = time.time()
            while len(self._queue) == 0:
                if time.time() - start_time >= timeout:
                    return None
                time.sleep(0.01)
        
        with self._lock:
            if not self._queue:
                return None
            
            item = heappop(self._queue)
            self._resource_controller.remove_item()
            self._stats['total_processed'] += 1
            
            return item.data
    
    def peek(self) -> Optional[Any]:
        """查看优先级最高的项（不移除）"""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0].data
    
    def remove(self, data: Any) -> bool:
        """移除指定的数据项"""
        with self._lock:
            for i, item in enumerate(self._queue):
                if item.data == data:
                    # 从堆中移除指定项
                    self._queue[i] = self._queue[-1]  # 用最后一项替换
                    self._queue.pop()  # 移除最后一项
                    heapify(self._queue)  # 重新堆化
                    self._resource_controller.remove_item()
                    return True
            return False
    
    def update_priority(self, data: Any, new_priority: int) -> bool:
        """更新指定数据的优先级"""
        with self._lock:
            for item in self._queue:
                if item.data == data:
                    item.priority = new_priority
                    heapify(self._queue)  # 重新堆化
                    return True
            return False
    
    def qsize(self) -> int:
        """获取队列大小"""
        with self._lock:
            return len(self._queue)
    
    def empty(self) -> bool:
        """检查队列是否为空"""
        return self.qsize() == 0
    
    def clear(self):
        """清空队列"""
        with self._lock:
            self._queue.clear()
            # 重置资源计数
            self._resource_controller.current_size = 0
            self._resource_controller.current_memory_mb = 0
    
    def get_stats(self) -> dict:
        """获取队列统计信息"""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'name': self.name,
                'current_size': len(self._queue),
                'resource_usage': self._resource_controller.get_resource_usage(),
                'uptime_seconds': time.time() - self._stats['created_at']
            })
            return stats
    
    def get_all_items(self) -> List[Tuple[Any, int]]:
        """获取所有项的数据和优先级（用于调试）"""
        with self._lock:
            return [(item.data, item.priority) for item in self._queue]
    
    def __iter__(self) -> Iterator[Any]:
        """迭代器，按优先级顺序"""
        temp_queue = self.get_all_items()
        temp_queue.sort(key=lambda x: x[1])  # 按优先级排序
        for data, _ in temp_queue:
            yield data
    
    def __len__(self) -> int:
        return self.qsize()
    
    def __repr__(self) -> str:
        return f"PriorityQueue(name='{self.name}', size={self.qsize()})"