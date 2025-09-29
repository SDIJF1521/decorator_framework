"""
决策树模块 - 用于命令和事件处理的决策逻辑
"""

from typing import Any, Dict, Optional, Callable, List
import asyncio


class TreeNode:
    """决策树节点"""
    
    def __init__(self, name: str, condition: Optional[Callable] = None, 
                 action: Optional[Callable] = None, children: Optional[List['TreeNode']] = None):
        self.name = name
        self.condition = condition
        self.action = action
        self.children = children or []
    
    async def evaluate(self, context: Dict[str, Any]) -> Any:
        """评估节点"""
        # 检查条件
        if self.condition:
            if asyncio.iscoroutinefunction(self.condition):
                condition_result = await self.condition(context)
            else:
                condition_result = self.condition(context)
            
            if not condition_result:
                return None
        
        # 执行动作
        if self.action:
            if asyncio.iscoroutinefunction(self.action):
                result = await self.action(context)
            else:
                result = self.action(context)
            
            if result is not None:
                return result
        
        # 评估子节点
        for child in self.children:
            result = await child.evaluate(context)
            if result is not None:
                return result
        
        return None


class Tree:
    """决策树 - 用于处理命令和事件的决策逻辑"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.root = TreeNode("root")
        self._nodes: Dict[str, TreeNode] = {"root": self.root}
    
    def add_node(self, name: str, parent: str = "root", 
                 condition: Optional[Callable] = None,
                 action: Optional[Callable] = None) -> TreeNode:
        """添加节点到树"""
        if parent not in self._nodes:
            raise ValueError(f"父节点 '{parent}' 不存在")
        
        node = TreeNode(name, condition, action)
        self._nodes[name] = node
        self._nodes[parent].children.append(node)
        return node
    
    def get_node(self, name: str) -> Optional[TreeNode]:
        """获取节点"""
        return self._nodes.get(name)
    
    def remove_node(self, name: str) -> bool:
        """移除节点"""
        if name == "root":
            return False
        
        if name not in self._nodes:
            return False
        
        # 从父节点的子节点列表中移除
        for node in self._nodes.values():
            if name in [child.name for child in node.children]:
                node.children = [child for child in node.children if child.name != name]
                break
        
        # 递归移除所有子节点
        node_to_remove = self._nodes[name]
        for child in node_to_remove.children:
            self.remove_node(child.name)
        
        del self._nodes[name]
        return True
    
    async def evaluate(self, context: Dict[str, Any]) -> Any:
        """评估整个树"""
        return await self.root.evaluate(context)
    
    def clear(self):
        """清空树（保留根节点）"""
        self.root.children.clear()
        # 只保留根节点
        self._nodes = {"root": self.root}
    
    def get_structure(self) -> Dict[str, Any]:
        """获取树的结构信息"""
        def _get_node_structure(node: TreeNode) -> Dict[str, Any]:
            return {
                "name": node.name,
                "has_condition": node.condition is not None,
                "has_action": node.action is not None,
                "children": [_get_node_structure(child) for child in node.children]
            }
        
        return {
            "name": self.name,
            "total_nodes": len(self._nodes),
            "structure": _get_node_structure(self.root)
        }
    
    def __repr__(self) -> str:
        return f"Tree(name='{self.name}', nodes={len(self._nodes)})"


# 预定义的决策条件和动作
def always_true(context: Dict[str, Any]) -> bool:
    """总是返回True的条件"""
    return True


def has_command(context: Dict[str, Any]) -> bool:
    """检查是否有命令"""
    return bool(context.get('command'))


def has_event(context: Dict[str, Any]) -> bool:
    """检查是否有事件"""
    return bool(context.get('event_name'))


def default_action(context: Dict[str, Any]) -> str:
    """默认动作"""
    return "处理完成"


def command_action(context: Dict[str, Any]) -> str:
    """命令处理动作"""
    command = context.get('command', 'unknown')
    args = context.get('args', {})
    return f"命令 '{command}' 处理完成，参数: {args}"


def event_action(context: Dict[str, Any]) -> str:
    """事件处理动作"""
    event_name = context.get('event_name', 'unknown')
    return f"事件 '{event_name}' 处理完成"



def create_default_tree() -> Tree:
    """创建决策树"""
    tree = Tree("default")
    
    # 添加命令处理分支
    tree.add_node("command_handler", "root", has_command, command_action)
    
    # 添加事件处理分支
    tree.add_node("event_handler", "root", has_event, event_action)
    
    # 添加默认处理分支
    tree.add_node("default_handler", "root", always_true, default_action)
    
    return tree