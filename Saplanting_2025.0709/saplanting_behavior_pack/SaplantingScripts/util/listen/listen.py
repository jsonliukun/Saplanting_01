# -*- coding: utf-8 -*-
from .event import BaseEvent
"""
事件监听框架
提供装饰器用于注册事件监听器
"""


class UnknowEvent(Exception):
    """未知事件异常"""
    pass


class Listen:
    """
    事件监听类
    提供事件注册的装饰器和类型常量
    """

    class CallableStr(str):
        """
        可调用字符串类
        用于简化事件监听装饰器的使用
        """

        def __call__(self, event_class, priority=0):
            """
            调用装饰器

            Args:
                event_class: 事件类
                priority: 监听优先级

            Returns:
                装饰器函数
            """
            return Listen.on(event_class, _type=self, priority=priority)

    # 事件监听类型常量
    server = CallableStr('server')  # 服务器事件
    minecraft = CallableStr('minecraft')  # 引擎事件
    mc = CallableStr('minecraft')  # 引擎事件别名
    client = CallableStr('client')  # 客户端事件

    @staticmethod
    def on(event_class, _type="minecraft", priority=0):
        """
        事件监听装饰器
        用于注册事件处理方法

        Args:
            event_class: 事件类或事件名称
            _type: 事件类型
            priority: 监听优先级

        Returns:
            装饰器函数
        """
        # 确定事件名称
        if isinstance(event_class, basestring):
            event_name = event_class
        elif issubclass(event_class, BaseEvent):
            event_name = event_class.__name__
        else:
            raise UnknowEvent("unknown listening event")

        def decorator(func):
            """
            装饰器内部函数
            为方法添加监听属性

            Args:
                func: 被装饰的方法

            Returns:
                装饰后的方法
            """
            # 添加监听属性
            func.listen_type = _type  # 事件类型
            func.listen_event = event_name  # 事件名称
            func.listen_priority = priority  # 监听优先级
            return func

        return decorator