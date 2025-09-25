# -*- coding: utf-8 -*-

"""
模组基础配置常量定义文件
定义模组名称、版本、系统名称等核心常量
"""

# Mod Info
ModName = "Saplanting" #模组名称
ModVersion = "0.0.1"   #模组版本号
TeamName = "HeyPixel"  #开发团队名称

# Server System
ServerSystemName = ModName + "ServerSystem" #服务器系统名称
ServerSystemClsPath = "SaplantingScripts.server." + ModName + "Server." + ModName + "Server"  #服务器系统路径

# Client System
ClientSystemName = ModName + "ClientSystem"# 客户端系统名称
ClientSystemClsPath = "SaplantingScripts.client." + ModName + "Client." + ModName + "Client"# 客户端系统类路径

ootDir = "SaplantingScripts"  # 根目录名称
# Engine
Minecraft = "Minecraft"  # 目标游戏引擎

CLIENT_SETTING_CONFIG_NAME = TeamName + ModName + "ClientSetting"  # 客户端设置配置键名
MASTER_SETTING_CONFIG_NAME = TeamName + ModName + "MasterSetting"   # 服务器主设置配置键名