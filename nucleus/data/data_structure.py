"""
基础数据结构类 - 为框架提供统一的数据结构接口
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class DataStructure(ABC):
    """所有数据结构的抽象基类"""
    
    @abstractmethod
    def __init__(self):
        """初始化数据结构"""
        pass
    
    @abstractmethod
    def put(self, data: Any) -> bool:
        """添加数据项"""
        pass
    
    @abstractmethod
    def get(self) -> Optional[Any]:
        """获取数据项"""
        pass
    
    @abstractmethod
    def empty(self) -> bool:
        """检查是否为空"""
        pass
    
    @abstractmethod
    def clear(self):
        """清空数据结构"""
        pass
    
    def __len__(self) -> int:
        """返回大小"""
        return 0