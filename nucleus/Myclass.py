# nucleus/Myclass.py
class ClassNucleus(type):
    _registry = {}  # 使用字典而不是列表
    _name_list = []

    def __new__(cls, name, bases, attrs):
        # 检查 fun_name 属性是否存在
        if 'fun_name' not in attrs:
            raise ValueError('Class must define "fun_name" attribute')
        # 检查 fun_name 值是否唯一
        fun_name = attrs['fun_name']
        if fun_name in cls._name_list:
            raise ValueError(f'Duplicate fun_name: "{fun_name}"')
        # 创建类
        new_class = super().__new__(cls, name, bases, attrs)
        # 注册类
        cls._name_list.append(fun_name)
        cls._registry[fun_name] = new_class
        return new_class

    @classmethod
    def get_registry(cls):
        """返回已注册类的字典，键为 fun_name，值为类"""
        return cls._registry

    @classmethod
    def clear_registry(cls):
        """清空注册表（主要用于测试）"""
        cls._registry.clear()
        cls._name_list.clear()