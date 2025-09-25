# -*- coding: utf-8 -*-
# @Time    : 2023/7/24 11:13
# @Author  : taokyla
# @File    : base.py
# -*- coding: utf-8 -*-
"""
配置系统基类
提供配置数据的加载、保存、重置等基础功能
"""


class BaseConfig(object):
    """
    配置基类
    提供配置数据的通用操作方法
    """

    def dump(self):
        """
        序列化配置数据为字典

        Returns:
            dict: 配置数据的字典表示
        """
        # 遍历所有不以"_"开头的属性
        # 如果属性值是BaseConfig实例，则调用其dump方法
        return dict(
            (k, v.dump() if isinstance(v, BaseConfig) else v)
            for k, v in self.__dict__.iteritems()
            if not k.startswith("_")  # 排除私有属性
        )

    def load_data(self, data):
        """
        从字典加载配置数据

        Args:
            data: 包含配置数据的字典
        """
        for key in data:
            if hasattr(self, key):
                value = getattr(self, key)
                # 如果属性是BaseConfig实例，递归加载数据
                if isinstance(value, BaseConfig):
                    value.load_data(data[key])
                else:
                    # 直接设置属性值
                    setattr(self, key, data[key])

    def reset(self):
        """
        重置配置为类定义时的默认值
        """
        for key in self.__dict__:
            # 只重置类中定义的属性（排除实例添加的属性）
            if key in self.__class__.__dict__:
                # 重置为类属性值
                self.__dict__[key] = self.__class__.__dict__[key]

    def get(self, key, default=None):
        """
        获取配置项的值

        Args:
            key: 配置项名称
            default: 默认值（如果配置项不存在）

        Returns:
            配置项的值或默认值
        """
        if key in self.__dict__:
            return self.__dict__[key]
        return default

    def set(self, key, value):
        """
        设置配置项的值

        Args:
            key: 配置项名称
            value: 要设置的值
        """
        if key in self.__dict__:
            setattr(self, key, value)


class SavableConfig(BaseConfig):
    """
    可保存配置基类
    扩展BaseConfig，添加保存和加载功能
    """
    _KEY = "config_data_key"  # 配置存储键名（子类需覆盖）

    def load(self):
        """
        加载配置数据（抽象方法）
        子类必须实现此方法
        """
        raise NotImplementedError("Subclasses must implement load method")

    def update_config(self, config):
        """
        更新配置并保存

        Args:
            config: 包含新配置数据的字典
        """
        # 加载新配置数据
        self.load_data(config)
        # 保存配置
        self.save()

    def save(self):
        """
        保存配置数据（抽象方法）
        子类必须实现此方法
        """
        raise NotImplementedError("Subclasses must implement save method")