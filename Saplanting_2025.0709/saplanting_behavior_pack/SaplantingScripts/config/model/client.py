# -*- coding: utf-8 -*-
# @Time    : 2023/7/24 11:14
# @Author  : taokyla
# @File    : client.py

# -*- coding: utf-8 -*-
"""
客户端可保存配置实现
使用客户端配置组件存储配置数据
"""

import mod.client.extraClientApi as clientApi

from .base import SavableConfig
from ...util.common import dealunicode, Singleton

# 创建组件工厂和配置组件
compFactory = clientApi.GetEngineCompFactory()
configComp = compFactory.CreateConfigClient(clientApi.GetLevelId())


class ClientSavableConfig(SavableConfig):
    """
    客户端可保存配置类
    使用客户端配置组件存储配置数据
    采用单例模式确保全局唯一实例
    """
    __metaclass__ = Singleton  # 单例元类
    _ISGLOBAL = False  # 是否为全局配置（True表示全局，False表示玩家本地）

    def load(self):
        """
        从客户端配置组件加载配置数据
        """
        # 获取配置数据并处理Unicode编码
        data = dealunicode(configComp.GetConfigData(self._KEY, self._ISGLOBAL))
        if data:
            # 加载数据到当前实例
            self.load_data(data)

    def save(self):
        """
        保存配置数据到客户端配置组件
        """
        # 将当前配置序列化并保存
        configComp.SetConfigData(self._KEY, self.dump(), isGlobal=self._ISGLOBAL)