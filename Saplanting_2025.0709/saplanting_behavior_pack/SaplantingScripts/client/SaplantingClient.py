# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
落地生根客户端主逻辑
处理树苗落地检测、自动种植等客户端功能
"""

from random import random
import mod.client.extraClientApi as clientApi

from .BaseClientSystem import BaseClientSystem
from ..config.heyconfig import ClientSetting
from ..config.sapling import default_saplings
from ..util.common import Singleton
from ..util.listen import Listen

# 创建组件工厂
compFactory = clientApi.GetEngineCompFactory()
# 获取引擎命名空间和系统名称
engineName = clientApi.GetEngineNamespace()
engineSystem = clientApi.GetEngineSystemName()


class ClientMasterSetting(object):
    """
    客户端主设置类
    管理树苗种植相关的设置和计时逻辑
    """
    __metaclass__ = Singleton  # 单例模式

    # 时间范围常量
    wait_time_range = 5  # 等待时间范围
    check_time_range = 15  # 检查时间范围

    def __init__(self):
        """初始化默认设置"""
        self.saplings = default_saplings  # 树苗集合
        self.min_wait_time = 3  # 最小等待时间
        self.check_min_wait_time = 15 + self.min_wait_time  # 最小检查等待时间

    def load_config(self, data):
        """
        加载配置数据

        Args:
            data: 配置数据字典
        """
        if "saplings" in data:
            # 将列表转换为集合元组
            self.saplings = set(tuple(value) for value in data["saplings"])
        if "min_wait_time" in data:
            # 确保最小等待时间不小于0
            self.min_wait_time = max(0, data["min_wait_time"])
            # 更新最小检查等待时间
            self.check_min_wait_time = 15 + self.min_wait_time

    def get_wait_time(self):
        """
        获取随机等待时间

        Returns:
            float: 随机等待时间
        """
        return random() * self.wait_time_range + self.min_wait_time

    def get_check_wait_time(self):
        """
        获取随机检查等待时间

        Returns:
            float: 随机检查等待时间
        """
        return random() * self.check_time_range + self.check_min_wait_time


class SaplantingClient(BaseClientSystem):
    """
    落地生根客户端主类
    处理树苗落地检测和自动种植逻辑
    """

    def __init__(self, namespace, name):
        """
        初始化客户端系统

        Args:
            namespace: 命名空间
            name: 系统名称
        """
        super(SaplantingClient, self).__init__(namespace, name)
        self.game_comp = compFactory.CreateGame(self.levelId)  # 游戏组件
        self.master_setting = ClientMasterSetting()  # 主设置实例
        self.item_entities = {}  # 跟踪的树苗物品实体字典
        self.client_setting = ClientSetting()  # 客户端设置实例

    @Listen.on("LoadClientAddonScriptsAfter")
    def on_enabled(self, event=None):
        """
        客户端脚本加载完成后事件处理
        加载配置并注册配置界面
        """
        self.client_setting.load()  # 加载客户端设置
        # 创建配置组件
        comp = clientApi.CreateComponent(self.levelId, "HeyPixel", "Config")
        if comp:
            from ..config.heyconfig import register_config
            # 注册配置界面
            comp.register_config(register_config)

    @Listen.on("UiInitFinished")
    def on_local_player_stop_loading(self, event=None):
        """
        UI初始化完成事件处理
        同步玩家的砍树状态到服务器
        """
        self.NotifyToServer("SyncPlayerTreeFallingState", {
            "playerId": self.playerId,
            "state": self.client_setting.tree_felling
        })

    def reload_client_setting(self):
        """
        重新加载客户端设置
        并同步状态到服务器
        """
        self.client_setting.load()  # 重新加载设置
        # 同步砍树状态到服务器
        self.NotifyToServer("SyncPlayerTreeFallingState", {
            "playerId": self.playerId,
            "state": self.client_setting.tree_felling
        })

    @Listen.server("SyncMasterSetting")
    def on_sync_master_setting(self, data):
        """
        接收服务器同步的主设置
        """
        self.master_setting.load_config(data)  # 加载主设置

    @Listen.on("AddEntityClientEvent")
    def on_add_sapling_item(self, event):
        """
        添加实体事件处理
        检测新添加的实体是否为树苗物品
        """
        # 获取实体ID
        entityId = event["id"]

        # 创建物品组件
        itemComp = compFactory.CreateItem(entityId)

        # 检查是否为物品实体
        if itemComp:
            # 获取物品信息
            itemDict = itemComp.GetEngineItemDict()

            # 检查是否获取到有效物品信息
            if itemDict:
                # 提取物品名称和附加值
                itemName = itemDict.get("itemName", "")
                auxValue = itemDict.get("auxValue", 0)

                # 检查是否为树苗
                if (itemName, auxValue) in self.master_setting.saplings:
                    # 检查是否已跟踪该实体
                    if entityId not in self.item_entities:
                        # 记录树苗物品实体
                        self.item_entities[entityId] = (itemName, auxValue)
                        # 添加定时器检查是否落地
                        self.game_comp.AddTimer(
                            self.master_setting.get_check_wait_time(),
                            self.check_on_ground,
                            entityId
                        )

    @Listen.on("RemoveEntityClientEvent")
    def on_remove_entity(self, event):
        """
        移除实体事件处理
        清理已移除的树苗物品实体记录
        """
        entityId = event["id"]
        if entityId in self.item_entities:
            # 从跟踪字典中移除
            self.item_entities.pop(entityId)

    @Listen.on("OnGroundClientEvent")
    def on_sapling_on_ground(self, event):
        """
        实体落地事件处理
        处理树苗物品落地情况
        """
        entityId = event["id"]
        if entityId in self.item_entities:
            # 添加定时器通知服务器
            self.game_comp.AddTimer(
                self.master_setting.get_wait_time(),
                self.on_ground_notify,
                entityId
            )

    def on_ground_notify(self, entityId):
        """
        通知服务器树苗落地
        """
        if entityId in self.item_entities:
            # 获取物品信息
            itemName, auxValue = self.item_entities[entityId]
            # 通知服务器树苗落地
            self.NotifyToServer("onSaplingOnGround", {
                "playerId": self.playerId,
                "entityId": entityId,
                "itemName": itemName,
                "auxValue": auxValue
            })

    def check_on_ground(self, entityId):
        """
        检查树苗物品是否落地
        """
        if entityId in self.item_entities:
            # 获取属性组件
            attrComp = compFactory.CreateAttr(entityId)
            if attrComp and attrComp.isEntityOnGround():
                # 如果已落地，通知服务器
                self.on_ground_notify(entityId)
            else:
                # 如果未落地，继续检查
                self.game_comp.AddTimer(
                    self.master_setting.get_check_wait_time(),
                    self.check_on_ground,
                    entityId
                )

    def reload_master_setting(self):
        """
        重新加载主设置
        请求服务器同步最新设置
        """
        self.NotifyToServer("ReloadMasterSetting", {})
