# -*- coding: utf-8 -*-
# @Time    : 2023/12/8 14:28
# @Author  : taokyla
# @File    : heyconfig.py

"""
客户端配置类定义
处理客户端的设置和配置界面注册
"""

from .modConfig import CLIENT_SETTING_CONFIG_NAME, ModName, ClientSystemName
from .model.client import ClientSavableConfig


class ClientSetting(ClientSavableConfig):
    """
    客户端设置类
    继承自ClientSavableConfig，用于管理客户端的持久化设置
    """
    _KEY = CLIENT_SETTING_CONFIG_NAME  # 配置存储键名
    _ISGLOBAL = True  # 是否为全局配置

    # 类属性默认值
    tree_felling = True  # 是否启用砍树功能

    def __init__(self):
        """
        初始化客户端设置
        设置默认值
        """
        self.tree_felling = True  # 实例属性初始化


# 配置界面注册字典
register_config = {
    "name": "落地生根",  # 配置显示名称
    "mod": ModName,     # 所属模组名称
    "categories": [
        {
            "name": "客户端设置",  # 分类名称
            "key": CLIENT_SETTING_CONFIG_NAME,  # 分类键名
            "title": "落地生根客户端设置",  # 分类标题
            "icon": "textures/ui/anvil_icon",  # 分类图标
            "global": True,  # 是否为全局设置
            "callback": {  # 回调函数配置
                "function": "CALLBACK",
                "extra": {
                    "name": ModName,
                    "system": ClientSystemName,
                    "function": "reload_client_setting"  # 重新加载设置的函数名
                }
            },
            "items": [  # 配置项列表
                {
                    "name": "gui.quick_suit.client.tree_felling.name",  # 显示名称键
                    "key": "tree_felling",  # 配置键名
                    "type": "toggle",  # 控件类型：开关
                    "default": ClientSetting.tree_felling  # 默认值
                }
            ]
        }
    ]
}