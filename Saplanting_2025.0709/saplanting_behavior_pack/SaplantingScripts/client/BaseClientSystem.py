# -*- coding: utf-8 -*-
"""
客户端系统基类
提供客户端事件监听的基础框架和自动化注册机制
"""

import mod.client.extraClientApi as clientApi

from ..config.modConfig import *  # 导入模组配置常量
from ..util.listen import Listen  # 导入事件监听框架

# 获取引擎命名空间和系统名称
engineName = clientApi.GetEngineNamespace()
engineSystem = clientApi.GetEngineSystemName()


class BaseClientSystem(clientApi.GetClientSystemCls()):
    """
    客户端系统基类
    提供统一的事件监听管理和自动化注册功能

    属性:
        ListenDict: 事件监听类型映射字典
        levelId: 当前关卡ID
        playerId: 本地玩家ID
    """

    # 事件监听类型映射字典，定义不同监听类型对应的命名空间和系统
    ListenDict = {
        Listen.minecraft: (engineName, engineSystem),  # 引擎事件
        Listen.client: (ModName, ClientSystemName),  # 客户端事件
        Listen.server: (ModName, ServerSystemName)  # 服务器事件
    }

    def __init__(self, namespace, name):
        """
        初始化客户端系统

        Args:
            namespace: 命名空间
            name: 系统名称
        """
        super(BaseClientSystem, self).__init__(namespace, name)
        self.levelId = clientApi.GetLevelId()  # 获取关卡ID
        self.playerId = clientApi.GetLocalPlayerId()  # 获取本地玩家ID
        self.onRegister()  # 调用注册方法

    def onRegister(self):
        """
        自动化注册事件监听器
        扫描类中所有带有listen_event属性的方法并注册监听
        """
        for key in dir(self):
            obj = getattr(self, key)
            # 检查方法是否可调用且具有listen_event属性
            if callable(obj) and hasattr(obj, 'listen_event'):
                event = getattr(obj, "listen_event")  # 事件名称
                _type = getattr(obj, "listen_type")  # 监听类型
                priority = getattr(obj, "listen_priority")  # 监听优先级
                # 注册事件监听
                self.listen(event, obj, _type=_type, priority=priority)

    def listen(self, event, func, _type=Listen.minecraft, priority=0):
        """
        注册事件监听

        Args:
            event: 事件名称
            func: 回调函数
            _type: 监听类型（默认为引擎事件）
            priority: 监听优先级（默认为0）
        """
        if _type not in self.ListenDict:
            return
        name, system = self.ListenDict[_type]
        # 调用引擎API注册事件监听
        self.ListenForEvent(name, system, event, self, func, priority=priority)

    def unlisten(self, event, func, _type=Listen.minecraft, priority=0):
        """
        取消事件监听

        Args:
            event: 事件名称
            func: 回调函数
            _type: 监听类型
            priority: 监听优先级
        """
        if _type not in self.ListenDict:
            return
        name, system = self.ListenDict[_type]
        # 调用引擎API取消事件监听
        self.UnListenForEvent(name, system, event, self, func, priority=priority)