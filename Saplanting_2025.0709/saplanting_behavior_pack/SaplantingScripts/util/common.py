# -*- coding: utf-8 -*-
from copy import deepcopy
from math import floor
from random import random
"""
通用工具函数集合
包含数据处理、数学计算、类型转换等实用功能
"""


class Singleton(type):
    """
    单例模式元类
    确保类只有一个实例存在
    """
    _instances = {}

    def __call__(cls, *args,**kwargs):
        """
        创建或获取类的唯一实例

        Args:
            *args: 位置参数
            ​**kwargs: 关键字参数

        Returns:
            类的唯一实例
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instances[cls]


def dealunicode(_instance):
    """
    处理Unicode编码问题
    将数据结构中的所有Unicode字符串转换为UTF-8编码

    Args:
        _instance: 需要处理的数据结构

    Returns:
        处理后的数据结构
    """
    if isinstance(_instance, unicode):
        return _instance.encode('utf8')
    elif isinstance(_instance, list):
        result = []
        for value in _instance:
            result.append(dealunicode(value))
        return result
    elif isinstance(_instance, dict):
        result = {}
        for key, value in _instance.items():
            result[dealunicode(key)] = dealunicode(value)
        return result
    elif isinstance(_instance, tuple):
        return tuple(dealunicode(d) for d in _instance)
    elif isinstance(_instance, set):
        return set(dealunicode(d) for d in _instance)
    elif isinstance(_instance, frozenset):
        return frozenset(dealunicode(d) for d in _instance)
    return _instance


def update_dict(old, new):
    """
    递归更新字典
    将新字典的内容合并到旧字典中

    Args:
        old: 需要更新的旧字典
        new: 包含更新内容的新字典

    Returns:
        更新后的字典
    """
    for key in new:
        if key in old:
            # 如果键存在且值是字典，递归更新
            if isinstance(old[key], dict) and isinstance(new[key], dict):
                update_dict(old[key], new[key])
                continue
        # 更新或添加键值对
        old[key] = deepcopy(new[key])
    return old


def filling_dict(config, default):
    """
    填充字典的缺失项
    根据默认字典填充配置字典中缺失的键值对

    Args:
        config: 需要填充的配置字典
        default: 提供默认值的字典

    Returns:
        填充后的配置字典
    """
    for key in default:
        if key not in config:
            # 添加缺失的键值对
            config[key] = deepcopy(default[key])
        else:
            # 如果值是字典，递归填充
            if isinstance(config[key], dict) and isinstance(default[key], dict):
                filling_dict(config[key], default[key])
    return config


def get_float_color(r, g, b):
    """
    将RGB整数颜色转换为浮点数颜色

    Args:
        r: 红色分量 (0-255)
        g: 绿色分量 (0-255)
        b: 蓝色分量 (0-255)

    Returns:
        (r, g, b, a) 浮点数元组 (0.0-1.0)
    """
    return r / 255.0, g / 255.0, b / 255.0, 1.0


def get_gradient_color(start_color, end_color, progress):
    """
    计算渐变颜色

    Args:
        start_color: 起始颜色 (RGB元组)
        end_color: 结束颜色 (RGB元组)
        progress: 渐变进度 (0.0-1.0)

    Returns:
        渐变过程中的颜色 (RGB元组)
    """
    if start_color == end_color:
        return start_color
    # 计算每个分量的渐变值
    return tuple(int(d[0] + (d[1] - d[0]) * progress) for d in zip(start_color, end_color))


def isRectangleOverlap(rec1, rec2):
    """
    判断两个矩形是否重叠

    Args:
        rec1: 第一个矩形 (x1, y1, x2, y2)
        rec2: 第二个矩形 (x1, y1, x2, y2)

    Returns:
        bool: 是否重叠
    """

    def intersect(p_left, p_right, q_left, q_right):
        """判断区间是否相交"""
        return min(p_right, q_right) > max(p_left, q_left)

    # 检查X轴和Y轴是否都相交
    return intersect(rec1[0], rec1[2], rec2[0], rec2[2]) and intersect(rec1[1], rec1[3], rec2[1], rec2[3])


def intToRoman(num):
    """
    将整数转换为罗马数字

    Args:
        num: 需要转换的整数

    Returns:
        str: 罗马数字字符串
    """
    num = int(num)
    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    numerals = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    res, i = "", 0
    while num:
        # 从大到小依次处理每个值
        res += (num // values[i]) * numerals[i]
        num %= values[i]
        i += 1
    return res


def randomFloatToInt(num):
    """
    将浮点数随机舍入为整数
    根据小数部分的大小随机决定向上或向下取整

    Args:
        num: 需要处理的浮点数

    Returns:
        int: 舍入后的整数
    """
    numInt = int(num)
    left = num - numInt
    if left > 0:
        # 根据小数部分的大小随机决定是否进位
        if random() < left:
            numInt += 1
    return numInt


def get_block_pos(pos):
    """
    将浮点坐标转换为方块坐标

    Args:
        pos: 浮点坐标 (x, y, z)

    Returns:
        (int, int, int): 方块坐标
    """
    return int(floor(pos[0])), int(floor(pos[1])), int(floor(pos[2]))


def reformat_item(item, pop=False):
    """
    格式化物品字典
    清理不必要的字段，使物品字典符合特定格式要求

    Args:
        item: 原始物品字典
        pop: 是否删除不必要字段 (True) 或创建新字典 (False)

    Returns:
        dict: 格式化后的物品字典
    """
    if item:
        if pop: #删除不必要字段
            if 'userData' in item:  #保留核心字段和userData
                for key in item.keys():
                    if key not in {"newItemName", "newAuxValue", "count", "userData"}:
                        item.pop(key)
            else:  # 保留核心字段和可能的额外字段
                for key in item.keys():
                    if key not in {"newItemName", "newAuxValue", "count", "modEnchantData", "enchantData", "durability", "customTips", "extraId", "showInHand"}:
                        item.pop(key)
            return item
        else:
            result = {'newItemName': item['newItemName'], 'newAuxValue': item['newAuxValue'], 'count': item['count']} # 创建新字典，只包含必要字段
            if 'userData' in item: # 添加可能的额外字段
                if item['userData']:
                    result['userData'] = deepcopy(item['userData'])
            else:
                if 'modEnchantData' in item:
                    result['modEnchantData'] = deepcopy(item['modEnchantData'])
                if 'enchantData' in item:
                    result['enchantData'] = deepcopy(item['enchantData'])
                if 'durability' in item:
                    result['durability'] = item['durability']
                if 'customTips' in item:
                    result['customTips'] = item['customTips']
                if 'extraId' in item:
                    result['extraId'] = item['extraId']
                if 'showInHand' in item:
                    result['showInHand'] = item['showInHand']
            return result
    return item
