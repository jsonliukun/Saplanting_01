# -*- coding: utf-8 -*-
"""
服务器端专用工具函数
包含物品处理、玩家交互等服务器相关功能
"""

from copy import deepcopy
import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import ItemPosType

# 创建组件工厂和物品组件
compFactory = serverApi.GetEngineCompFactory()
itemComp = compFactory.CreateItem(serverApi.GetLevelId())

# 缓存物品基本信息
cachedItemInfos = {}


def GetItemInfo(itemName, auxValue, isEnchanted=False):
    """
    获取物品基本信息（带缓存）

    Args:
        itemName: 物品名称
        auxValue: 物品附加值
        isEnchanted: 是否附魔

    Returns:
        dict: 物品基本信息
    """
    key = (itemName, auxValue, isEnchanted)
    if key in cachedItemInfos:
        return cachedItemInfos[key]

    # 从引擎获取物品信息
    info = itemComp.GetItemBasicInfo(itemName, auxValue, isEnchanted=isEnchanted)
    cachedItemInfos[key] = info
    return info


# 缓存斧头类物品判断结果
axe_items_cache = {}


def isAxe(itemName, auxValue=0):
    """
    判断物品是否为斧头

    Args:
        itemName: 物品名称
        auxValue: 物品附加值

    Returns:
        bool: 是否为斧头
    """
    if itemName in axe_items_cache:
        return axe_items_cache[itemName]

    # 获取物品信息并判断类型
    info = GetItemInfo(itemName, auxValue)
    if info and info["itemType"] == "axe":
        axe_items_cache[itemName] = True
        return True

    axe_items_cache[itemName] = False
    return False


def is_same_item_ignore_count(old, new):
    """
    比较两个物品是否相同（忽略数量）

    Args:
        old: 第一个物品字典
        new: 第二个物品字典

    Returns:
        bool: 是否相同
    """
    # 比较名称和附加值
    if old["newAuxValue"] == new["newAuxValue"] and old["newItemName"] == new["newItemName"]:
        # 比较用户数据
        old_userData = old.get("userData")
        new_userData = new.get("userData")
        return old_userData == new_userData
    return False


def AddItemToPlayerInventory(playerId, spawnitem):
    """
    添加物品到玩家背包
    优先放入背包，背包满时生成物品实体

    Args:
        playerId: 玩家ID
        spawnitem: 要添加的物品字典

    Returns:
        bool: 是否成功添加
    """
    itemName = spawnitem["newItemName"]
    auxValue = spawnitem["newAuxValue"]
    count = spawnitem.get('count', 0)

    # 检查物品数量
    if count <= 0:
        return True

    # 获取物品基本信息
    info = itemComp.GetItemBasicInfo(itemName, auxValue)
    maxStackSize = info['maxStackSize'] if info else 1

    # 获取玩家背包组件
    itemcomp = compFactory.CreateItem(playerId)
    # 获取玩家背包所有物品
    playerInv = itemcomp.GetPlayerAllItems(ItemPosType.INVENTORY, True)

    # 尝试放入已有物品槽位
    for slotId, itemDict in enumerate(playerInv):
        if count <= 0:
            return True

        if itemDict:
            # 槽位有相同物品，尝试堆叠
            if is_same_item_ignore_count(itemDict, spawnitem):
                canspawncount = maxStackSize - itemDict['count']
                if canspawncount > 0:
                    spawncount = min(canspawncount, count)
                    # 更新物品数量
                    itemcomp.SetInvItemNum(slotId, itemDict['count'] + spawncount)
                    count -= spawncount
        else:
            # 空槽位，放入新物品
            spawncount = min(maxStackSize, count)
            itemDict = deepcopy(spawnitem)
            itemDict['count'] = spawncount
            itemcomp.SpawnItemToPlayerInv(itemDict, playerId, slotId)
            count -= spawncount

    # 处理剩余物品（背包已满）
    while count > 0:
        spawncount = min(maxStackSize, count)
        itemDict = deepcopy(spawnitem)
        itemDict['count'] = spawncount

        # 获取玩家位置
        dim = compFactory.CreateDimension(playerId).GetEntityDimensionId()
        pos = compFactory.CreatePos(playerId).GetPos()
        # 在玩家脚下生成物品实体
        itemComp.SpawnItemToLevel(itemDict, dim, (pos[0], pos[1] - 1, pos[2]))
        count -= spawncount

    return True


def AddItemToContainer(chestpos, spawnitem, dimension=0):
    """
    添加物品到容器（如箱子）

    Args:
        chestpos: 容器位置 (x, y, z)
        spawnitem: 要添加的物品字典
        dimension: 维度ID

    Returns:
        bool: 是否成功添加
    """
    # 获取容器大小
    size = itemComp.GetContainerSize(chestpos, dimension)
    if size < 0:
        return False

    itemName = spawnitem["newItemName"]
    auxValue = spawnitem["newAuxValue"]
    count = spawnitem.get('count', 0)

    # 检查物品数量
    if count <= 0:
        return True

    # 获取物品基本信息
    info = itemComp.GetItemBasicInfo(itemName, auxValue)
    maxStackSize = info['maxStackSize'] if info else 1

    # 计算容器剩余空间
    totalcanspawn = 0
    canspawnslotlist = []
    for slotId in range(size):
        if totalcanspawn < count:
            itemDict = itemComp.GetContainerItem(chestpos, slotId, dimension, getUserData=True)
            if itemDict:
                # 槽位有相同物品，计算可堆叠数量
                if is_same_item_ignore_count(itemDict, spawnitem):
                    canspawncount = maxStackSize - itemDict['count']
                    if canspawncount > 0:
                        totalcanspawn += canspawncount
                        canspawnslotlist.append([slotId, canspawncount])
            else:
                # 空槽位，可放入一组物品
                totalcanspawn += maxStackSize
                canspawnslotlist.append([slotId, maxStackSize])
        else:
            break

    # 检查容器是否有足够空间
    if totalcanspawn < count:
        return False

    # 添加物品到容器
    spawnResult = False
    for slotId, canspawncount in canspawnslotlist:
        if count <= 0:
            break

        # 计算本次可添加的数量
        spawncount = min(canspawncount, count)
        itemDict = itemComp.GetContainerItem(chestpos, slotId, dimension, getUserData=True)

        if not itemDict:
            # 空槽位，创建新物品
            itemDict = deepcopy(spawnitem)
            itemDict['count'] = 0

        # 更新物品数量
        itemDict['count'] += spawncount
        # 放入容器
        r = itemComp.SpawnItemToContainer(itemDict, slotId, chestpos, dimension)
        if r:
            spawnResult = True
        count -= spawncount

    return spawnResult