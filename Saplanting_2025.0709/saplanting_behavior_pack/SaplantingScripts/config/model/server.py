# -*- coding: utf-8 -*-
# @Time    : 2023/7/24 11:15
# @Author  : taokyla
# @File    : server.py
# -*- coding: utf-8 -*-
"""
服务器可保存配置实现
使用服务器额外数据组件存储配置数据
"""

import mod.server.extraServerApi as serverApi

from .base import SavableConfig
from ...util.common import dealunicode, Singleton

# 创建组件工厂和额外数据组件
compFactory = serverApi.GetEngineCompFactory()
extraDataComp = compFactory.CreateExtraData(serverApi.GetLevelId())


class ServerSavableConfig(SavableConfig):
    """
    服务器可保存配置类
    使用服务器额外数据组件存储配置数据
    采用单例模式确保全局唯一实例
    """
    __metaclass__ = Singleton  # 单例元类

    def load(self):
        """
        从服务器额外数据组件加载配置数据
        """
        # 获取配置数据并处理Unicode编码
        data = dealunicode(extraDataComp.GetExtraData(self._KEY))
        if data:
            # 加载数据到当前实例
            self.load_data(data)

    def save(self):
        """
        保存配置数据到服务器额外数据组件
        """
        # 将当前配置序列化并保存
        extraDataComp.SetExtraData(self._KEY, self.dump(), autoSave=True)
        # 手动保存额外数据
        extraDataComp.SaveExtraData()


class PlayerSavableConfig(SavableConfig):
    """
    玩家可保存配置类
    为每个玩家单独存储配置数据
    """

    def __init__(self, playerId):
        """
        初始化玩家配置

        Args:
            playerId: 玩家ID
        """
        super(PlayerSavableConfig, self).__init__()
        self._playerId = playerId
        # 为玩家创建额外数据组件
        self._extraDataComp = compFactory.CreateExtraData(playerId)

    @property
    def playerId(self):
        """获取玩家ID"""
        return self._playerId

    def load(self):
        """
        从玩家额外数据组件加载配置数据
        """
        # 获取配置数据并处理Unicode编码
        data = dealunicode(self._extraDataComp.GetExtraData(self._KEY))
        if data:
            # 加载数据到当前实例
            self.load_data(data)

    def save(self):
        """
        保存配置数据到玩家额外数据组件
        """
        # 将当前配置序列化并保存
        self._extraDataComp.SetExtraData(self._KEY, self.dump(), autoSave=True)
        # 手动保存额外数据
        self._extraDataComp.SaveExtraData()