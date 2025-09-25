# -*- coding: utf-8 -*-
# @Time    : 2023/12/8 9:41
# @Author  : taokyla
# @File    : heyconfig_server.py

"""
服务器主配置类定义
处理服务器的设置、数据序列化和配置界面注册
"""

from .modConfig import MASTER_SETTING_CONFIG_NAME, ModName, ClientSystemName
from .model.server import ServerSavableConfig
from .sapling import default_saplings, LOG_BLOCKS


class MasterSetting(ServerSavableConfig):
    """
    服务器主设置类
    继承自ServerSavableConfig，用于管理服务器的持久化设置
    """
    _KEY = MASTER_SETTING_CONFIG_NAME  # 配置存储键名

    # 类属性默认值
    saplings = default_saplings  # 默认树苗集合
    min_wait_time = 3  # 最小等待时间（秒）
    tree_felling = True  # 是否启用砍树功能
    check_leave_persistent_bit = True  # 是否检查树叶持久化位
    tree_felling_limit_count = 255  # 砍树数量限制
    log_blocks = LOG_BLOCKS  # 木头方块集合

    def __init__(self):
        """
        初始化服务器设置
        设置实例属性的默认值
        """
        self.saplings = default_saplings  # type: set[tuple[str, int]]  # 树苗集合
        self.min_wait_time = 3  # 最小等待时间
        self.tree_felling = True  # 砍树功能开关
        self.check_leave_persistent_bit = True  # 树叶持久化检查
        self.tree_felling_limit_count = 255  # 砍树数量限制
        self.log_blocks = LOG_BLOCKS  # 木头方块集合

    def load_data(self, data):
        """
        加载数据时的预处理
        对特定字段进行数据验证和类型转换

        Args:
            data: 要加载的配置数据字典
        """
        if "min_wait_time" in data:
            # 确保最小等待时间不小于0
            data["min_wait_time"] = max(0, data["min_wait_time"])
        if "saplings" in data:
            # 将列表转换为集合元组
            data["saplings"] = set(tuple(value) for value in data["saplings"])
        if "log_blocks" in data:
            # 将列表转换为集合
            data["log_blocks"] = set(data["log_blocks"])
        # 调用父类方法完成加载
        super(MasterSetting, self).load_data(data)

    def dump(self):
        """
        序列化配置数据
        将集合类型转换为列表以便JSON序列化

        Returns:
            dict: 可序列化的配置数据
        """
        data = super(MasterSetting, self).dump()  # 获取父类序列化数据
        if "saplings" in data:
            # 将集合转换为列表的列表
            data["saplings"] = list(list(value) for value in data["saplings"])
        if "log_blocks" in data:
            # 将集合转换为列表
            data["log_blocks"] = list(data["log_blocks"])
        return data

    def get_client_data(self, add_min_wait_time=True, add_saplings=True):
        """
        获取发送给客户端的数据
        只包含客户端需要知道的配置项

        Args:
            add_min_wait_time: 是否包含最小等待时间
            add_saplings: 是否包含树苗列表

        Returns:
            dict: 客户端数据字典
        """
        data = {}
        if add_min_wait_time:
            data["min_wait_time"] = self.min_wait_time
        if add_saplings:
            # 将集合转换为列表的列表以便序列化
            data["saplings"] = list(list(value) for value in self.saplings)
        return data


# 服务器配置界面注册字典
register_config_server = {
    "name": "落地生根",  # 配置显示名称
    "mod": ModName,  # 所属模组名称
    "permission": "host",  # 所需权限：房主
    "categories": [
        {
            "name": "房主设置",  # 分类名称
            "key": MASTER_SETTING_CONFIG_NAME,  # 分类键名
            "title": "落地生根房主设置",  # 分类标题
            "icon": "textures/ui/op",  # 分类图标
            "permission": "host",  # 所需权限
            "global": True,  # 是否为全局设置
            "callback": {  # 回调函数配置
                "function": "CALLBACK",
                "extra": {
                    "name": ModName,
                    "system": ClientSystemName,
                    "function": "reload_master_setting"  # 重新加载设置的函数名
                }
            },
            "items": [  # 配置项列表
                {
                    "type": "label",  # 文本标签
                    "size": 0.9,  # 字体大小
                    "name": "房主手持物品，聊天栏输入\"§l§a#hpldsg§r\"即可添加手持物品到种子白名单，该种子会尝试落地生根(仅对§a方块id§f和§a物品id§c相同§f的作物生效，不区分大小写，注意使用英文的#符号)。"
                },
                {
                    "type": "label",
                    "size": 0.9,
                    "name": "再次在聊天栏输入，可删除该物品的白名单"
                },
                {
                    "type": "label",
                    "size": 0.9,
                    "name": "聊天栏输入\"§l§a#hpldsgmt§r\"添加手持方块为木头，连锁砍树将识别并砍伐；再次输入移除"
                },
                {
                    "name": "gui.saplanting.server.min_wait_time.name",  # 显示名称键
                    "key": "min_wait_time",  # 配置键名
                    "type": "input",  # 控件类型：输入框
                    "format": "int",  # 输入格式：整数
                    "range": [0],  # 数值范围：最小值0
                    "default": MasterSetting.min_wait_time  # 默认值
                },
                {
                    "name": "gui.saplanting.server.tree_felling.name",
                    "key": "tree_felling",
                    "type": "toggle",  # 控件类型：开关
                    "default": MasterSetting.tree_felling
                },
                {
                    "name": "gui.saplanting.server.check_leave_persistent_bit.name",
                    "key": "check_leave_persistent_bit",
                    "type": "toggle",
                    "default": MasterSetting.check_leave_persistent_bit
                },
                {
                    "name": "gui.saplanting.server.tree_felling_limit_count.name",
                    "key": "tree_felling_limit_count",
                    "type": "input",
                    "format": "int",
                    "range": [0],
                    "default": MasterSetting.tree_felling_limit_count
                },
                {
                    "name": "gui.saplanting.reset.name",
                    "type": "button",  # 控件类型：按钮
                    "function": "RESET",  # 按钮功能：重置
                    "need_confirm": True  # 需要确认
                }
            ]
        }
    ]
}