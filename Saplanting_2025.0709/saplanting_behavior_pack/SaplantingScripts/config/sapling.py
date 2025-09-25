# -*- coding: utf-8 -*-
# @Time    : 2023/12/8 9:45
# @Author  : taokyla
# @File    : sapling.py

"""
树苗和方块相关配置定义
包含默认树苗列表、特殊树苗映射、木头方块定义等
"""

# 默认树苗配置集合，每个元素为(方块ID, 元数据)的元组
default_saplings = {
    ("minecraft:warped_fungus", 0),      # 诡异菌
    ("minecraft:crimson_fungus", 0),     # 绯红菌
    ("minecraft:sapling", 0),            # 橡树树苗
    ("minecraft:sapling", 1),            # 云杉树苗
    ("minecraft:sapling", 2),            # 白桦树苗
    ("minecraft:sapling", 3),            # 丛林树苗
    ("minecraft:sapling", 4),            # 金合欢树苗
    ("minecraft:sapling", 5),            # 深色橡树树苗
    ("minecraft:azalea", 0),             # 杜鹃花丛
    ("minecraft:flowering_azalea", 0),   # 开花杜鹃花丛
    ("minecraft:bamboo", 0),             # 竹子
    ("minecraft:wheat_seeds", 0),        # 小麦种子
    ("minecraft:pumpkin_seeds", 0),      # 南瓜种子
    ("minecraft:melon_seeds", 0),        # 西瓜种子
    ("minecraft:beetroot_seeds", 0),     # 甜菜种子
    ("minecraft:potato", 0),             # 马铃薯
    ("minecraft:carrot", 0),             # 胡萝卜
    ("minecraft:sweet_berries", 0),      # 甜浆果
    ("minecraft:sugar_cane", 0),         # 甘蔗
    ("minecraft:torchflower_seeds", 0),  # 火把花种子
    ("minecraft:pitcher_pod", 0),        # 瓶子草荚果
}

# 特殊树苗映射字典，键为种子物品，值为对应的作物方块
special_saplings = {
    ("minecraft:wheat_seeds", 0): ("minecraft:wheat", 0),              # 小麦种子 -> 小麦作物
    ("minecraft:pumpkin_seeds", 0): ("minecraft:pumpkin_stem", 0),      # 南瓜种子 -> 南瓜梗
    ("minecraft:melon_seeds", 0): ("minecraft:melon_stem", 0),          # 西瓜种子 -> 西瓜梗
    ("minecraft:beetroot_seeds", 0): ("minecraft:beetroot", 0),         # 甜菜种子 -> 甜菜根
    ("minecraft:potato", 0): ("minecraft:potatoes", 0),                 # 马铃薯 -> 马铃薯作物
    ("minecraft:carrot", 0): ("minecraft:carrots", 0),                  # 胡萝卜 -> 胡萝卜作物
    ("minecraft:sweet_berries", 0): ("minecraft:sweet_berry_bush", 0),  # 甜浆果 -> 甜浆果丛
    ("minecraft:glow_berries", 0): ("minecraft:cave_vines", 0),         # 发光浆果 -> 洞穴藤蔓
    ("minecraft:sugar_cane", 0): ("minecraft:reeds", 0),                # 甘蔗 -> 芦苇
    ("minecraft:bamboo", 0): ("minecraft:bamboo_sapling", 0),           # 竹子 -> 竹笋
    ("minecraft:torchflower_seeds", 0): ("minecraft:torchflower_crop", 0),  # 火把花种子 -> 火把花作物
    ("minecraft:pitcher_pod", 0): ("minecraft:pitcher_crop", 0),        # 瓶子草荚果 -> 瓶子草作物
}

# 木头方块集合，用于识别树木
LOG_BLOCKS = {
    "minecraft:log",          # 原木（旧版）
    "minecraft:log2",         # 原木2（旧版）
    "minecraft:oak_log",      # 橡木原木
    "minecraft:spruce_log",   # 云杉原木
    "minecraft:birch_log",    # 白桦原木
    "minecraft:jungle_log",   # 丛林原木
    "minecraft:acacia_log",   # 金合欢原木
    "minecraft:dark_oak_log", # 深色橡木原木
    "minecraft:cherry_log",   # 樱花原木
    "minecraft:mangrove_log", # 红树原木
}

# 方块周围坐标偏移，用于检测相邻方块（3x3x3区域减去中心点）
BLOCKSURROUNDINGS = [
    (1, 0, 0), (0, 0, 1), (0, 0, -1), (-1, 0, 0), (0, 1, 0),     # 直接相邻
    (-1, 1, 0), (0, 1, 1), (-1, 0, -1), (1, 0, -1), (1, 0, 1),   # 对角相邻
    (-1, 0, 1), (0, 1, -1), (1, 1, 0),                           # 更远的相邻
    (1, 1, -1), (-1, 1, 1), (-1, 1, -1), (1, 1, 1)               # 角落相邻
]

# 叶子方块集合，用于树木检测
LEAVE_BLOCKS = {
    "minecraft:leaves",                   # 树叶（旧版）
    "minecraft:leaves2",                  # 树叶2（旧版）
    "minecraft:mangrove_leaves",          # 红树树叶
    "minecraft:cherry_leaves",           # 樱花树叶
    "minecraft:azalea_leaves",           # 杜鹃树叶
    "minecraft:azalea_leaves_flowered"   # 开花杜鹃树叶
}