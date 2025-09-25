# -*- coding: utf-8 -*-
"""
落地生根模组主注册类
负责模组在客户端和服务器的初始化和销毁
"""

import mod.client.extraClientApi as clientApi  # 客户端API
import mod.server.extraServerApi as serverApi  # 服务器API
from mod.common.mod import Mod  # 模组基类

from .config.modConfig import *  # 导入模组配置常量


@Mod.Binding(name=ModName, version=ModVersion)
class SaplantingMod(object):
    """
    落地生根模组主类
    使用Mod SDK装饰器定义模组生命周期
    """

    def __init__(self):
        """
        模组初始化
        可以在此处添加全局初始化逻辑
        """
        pass

    @Mod.InitServer()
    def server_init(self):
        """
        服务器初始化
        在服务器端加载模组时调用
        注册服务器系统
        """
        # 注册服务器系统
        serverApi.RegisterSystem(
            ModName,  # 模组名称
            ServerSystemName,  # 服务器系统名称
            ServerSystemClsPath  # 服务器系统类路径
        )

    @Mod.InitClient()
    def client_init(self):
        """
        客户端初始化
        在客户端加载模组时调用
        注册客户端系统
        """
        # 注册客户端系统
        clientApi.RegisterSystem(
            ModName,  # 模组名称
            ClientSystemName,  # 客户端系统名称
            ClientSystemClsPath  # 客户端系统类路径
        )

    @Mod.DestroyClient()
    def destroy_client(self):
        """
        客户端销毁
        在客户端卸载模组时调用
        可以在此处添加客户端资源清理逻辑
        """
        pass

    @Mod.DestroyServer()
    def destroy_server(self):
        """
        服务器销毁
        在服务器卸载模组时调用
        可以在此处添加服务器资源清理逻辑
        """
        pass