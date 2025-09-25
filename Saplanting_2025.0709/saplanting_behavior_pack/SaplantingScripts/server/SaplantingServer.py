# -*- coding: utf-8 -*-
"""
落地生根模组服务器主逻辑
处理种植、砍树、配置管理等核心功能
"""

import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import ItemPosType, Facing

from .BaseServerSystem import BaseServerSystem
from ..config.heyconfig_server import MasterSetting
from ..config.sapling import special_saplings, BLOCKSURROUNDINGS, LEAVE_BLOCKS
from ..util.common import get_block_pos
from ..util.listen import Listen, ServerChatEvent, DelServerPlayerEvent
from ..util.server_util import isAxe

# 创建组件工厂实例
compFactory = serverApi.GetEngineCompFactory()


class SaplantingServer(BaseServerSystem):
    """
    落地生根服务器主类
    继承自BaseServerSystem，实现具体的种植和砍树逻辑
    """

    def __init__(self, namespace, name):
        """
        初始化服务器系统

        Args:
            namespace: 命名空间
            name: 系统名称
        """
        super(SaplantingServer, self).__init__(namespace, name)
        self.masterId = None  # 房主玩家ID
        self.player_tree_falling_state = {}  # type: dict[str,bool]  # 玩家砍树状态字典
        self.player_destroying = {}  # type: dict[str,set]  # 玩家正在破坏的方块集合

        # 创建各种引擎组件
        self.game_comp = compFactory.CreateGame(self.levelId)  # 游戏组件
        self.item_comp = compFactory.CreateItem(self.levelId)  # 物品组件
        self.msg_comp = compFactory.CreateMsg(self.levelId)  # 消息组件
        self.block_info_comp = compFactory.CreateBlockInfo(self.levelId)  # 方块信息组件
        self.block_state_comp = compFactory.CreateBlockState(self.levelId)  # 方块状态组件

        # 加载主设置
        self.master_setting = MasterSetting()
        self.master_setting.load()

    @Listen.on("OnCarriedNewItemChangedServerEvent")
    def on_player_hand_item_change(self, event):
        """
        玩家手持物品变化事件处理
        当玩家切换手持物品时，检查是否为斧头并显示砍树状态提示

        Args:
            event: 事件数据，包含玩家ID和新物品信息
        """
        if not self.master_setting.tree_felling:  # 检查砍树功能是否开启
            return

        newItemDict = event["newItemDict"]
        # 检查新物品是否为斧头
        if newItemDict and isAxe(newItemDict["newItemName"], newItemDict["newAuxValue"]):
            playerId = event["playerId"]
            # 获取玩家当前的砍树状态
            state = self.player_tree_falling_state.get(playerId, False)
            # 显示状态提示消息
            self.game_comp.SetOneTipMessage(playerId, "连锁砍树:{}".format("§a开" if state else "§c关"))

    @Listen.client("SyncPlayerTreeFallingState")
    def on_sync_player_tree_falling_state(self, event):
        """
        同步玩家砍树状态事件处理
        接收客户端发送的砍树状态变更

        Args:
            event: 事件数据，包含玩家ID和状态
        """
        playerId = event["__id__"] if "__id__" in event else event["playerId"]
        self.player_tree_falling_state[playerId] = event["state"]

    @Listen.on(ServerChatEvent)
    def on_command(self, event):
        """
        服务器聊天事件处理
        处理玩家输入的管理命令（添加/移除树苗和木头）

        Args:
            event: 聊天事件数据，包含玩家ID和消息内容
        """
        playerId = event["playerId"]
        # 只允许房主执行命令
        if playerId == self.masterId:
            message = event["message"].lower()

            # 处理添加/移除树苗命令
            if message == "#hpldsg":
                event["cancel"] = True  # 取消原始聊天消息
                # 获取玩家手持物品
                handItem = compFactory.CreateItem(playerId).GetPlayerItem(ItemPosType.CARRIED)
                if not handItem:
                    self.msg_comp.NotifyOneMessage(playerId, "§a[落地生根]§c没有物品在手上，添加失败")
                    return

                item_key = handItem["newItemName"], handItem["newAuxValue"]
                # 检查物品是否已在树苗列表中
                if item_key not in self.master_setting.saplings:
                    # 添加物品到树苗列表
                    self.master_setting.saplings.add(item_key)
                    self.master_setting.save()
                    # 同步设置到所有客户端
                    data = self.master_setting.get_client_data(add_min_wait_time=False)
                    self.BroadcastToAllClient("SyncMasterSetting", data)
                    self.msg_comp.NotifyOneMessage(playerId,
                                                   "§a[落地生根]§a添加方块{}:{}到白名单成功".format(*item_key))
                else:
                    # 从树苗列表中移除物品
                    self.master_setting.saplings.discard(item_key)
                    self.master_setting.save()
                    data = self.master_setting.get_client_data(add_min_wait_time=False)
                    self.BroadcastToAllClient("SyncMasterSetting", data)
                    self.msg_comp.NotifyOneMessage(playerId, "§a[落地生根]§a方块{}:{}已移出白名单".format(*item_key))

            # 处理添加/移除木头命令
            elif message == "#hpldsgmt":
                event["cancel"] = True
                handItem = compFactory.CreateItem(playerId).GetPlayerItem(ItemPosType.CARRIED)
                if not handItem:
                    self.msg_comp.NotifyOneMessage(playerId, "§a[落地生根]§c没有物品在手上，添加失败")
                    return

                item_name = handItem["newItemName"]
                # 检查方块是否已在木头列表中
                if item_name not in self.master_setting.log_blocks:
                    # 添加方块到木头列表
                    self.master_setting.log_blocks.add(item_name)
                    self.master_setting.save()
                    self.msg_comp.NotifyOneMessage(playerId,
                                                   "§a[落地生根]§a已添加方块{}为木头，忽略子id".format(item_name))
                else:
                    # 从木头列表中移除方块
                    self.master_setting.log_blocks.discard(item_name)
                    self.master_setting.save()
                    self.msg_comp.NotifyOneMessage(playerId, "§a[落地生根]§a已取消将方块{}识别为木头".format(item_name))

    @Listen.client("ReloadMasterSetting")
    def on_reload_master_setting(self, event=None):
        """
        重新加载主设置事件处理
        当配置界面修改设置后调用此方法

        Args:
            event: 事件数据（可选）
        """
        self.master_setting.load()  # 重新加载设置
        # 同步设置到所有客户端（不包含树苗列表）
        data = self.master_setting.get_client_data(add_saplings=False)
        self.BroadcastToAllClient("SyncMasterSetting", data)

    @Listen.on("LoadServerAddonScriptsAfter")
    def on_enabled(self, event=None):
        """
        服务器脚本加载完成后事件处理
        注册配置界面

        Args:
            event: 事件数据（可选）
        """
        comp = serverApi.CreateComponent(self.levelId, "HeyPixel", "Config")
        if comp:
            from ..config.heyconfig_server import register_config_server
            comp.register_config(register_config_server)  # 注册服务器配置界面

    @Listen.on("ClientLoadAddonsFinishServerEvent")
    def on_player_login_finish(self, event):
        """
        玩家加载完插件后事件处理
        初始化玩家数据和同步设置

        Args:
            event: 事件数据，包含玩家ID
        """
        playerId = event["playerId"]
        # 设置第一个登录的玩家为房主
        if self.masterId is None:
            self.masterId = playerId

        # 初始化玩家的破坏方块集合
        self.player_destroying[playerId] = set()
        # 向客户端同步主设置
        self.NotifyToClient(playerId, "SyncMasterSetting", self.master_setting.get_client_data())

    @Listen.on(DelServerPlayerEvent)
    def on_player_leave(self, event):
        """
        玩家离开游戏事件处理
        清理玩家相关数据

        Args:
            event: 事件数据，包含玩家ID
        """
        playerId = event["id"]
        if playerId in self.player_destroying:
            self.player_destroying.pop(playerId)  # 移除玩家的破坏数据

    @Listen.client("onSaplingOnGround")
    def on_sapling_on_ground(self, event):
        """
        树苗落地事件处理
        实现自动种植功能

        Args:
            event: 事件数据，包含物品实体信息和位置
        """
        # print "receive sapling on ground", event
        playerId = event["__id__"] if "__id__" in event else event["playerId"]
        entityId = event["entityId"]

        # 检查实体是否存活
        if not self.game_comp.IsEntityAlive(entityId):
            # print "entity not exists"
            return

        # 获取实体所在维度和位置
        dim = compFactory.CreateDimension(entityId).GetEntityDimensionId()
        item_entity_pos = compFactory.CreatePos(entityId).GetFootPos()
        entityId_block_pos = get_block_pos(item_entity_pos)

        # 检查目标位置是否可种植
        block = self.block_info_comp.GetBlockNew(entityId_block_pos, dimensionId=dim)
        if block:
            # 如果是耕地，则向上移动一格（在耕地上种植）
            if block["name"] == "minecraft:farmland":
                entityId_block_pos = entityId_block_pos[0], entityId_block_pos[1] + 1, entityId_block_pos[2]
                block = self.block_info_comp.GetBlockNew(entityId_block_pos, dimensionId=dim)
                if not block:
                    return
            # 检查方块是否可替换（只能是空气或水）
            if block["name"] not in {"minecraft:air", "minecraft:water", "minecraft:flowing_water"}:
                return

        # 获取物品信息
        itemName = event["itemName"]
        auxValue = event["auxValue"]
        item_key = itemName, auxValue

        # 检查是否为特殊树苗（需要转换为作物方块）
        if item_key in special_saplings:
            itemName, auxValue = special_saplings[item_key]

        # 检查是否可以放置方块
        result = compFactory.CreateItem(playerId).MayPlaceOn(itemName, auxValue, entityId_block_pos, Facing.Up)
        if not result and auxValue == 0:
            result = self.block_info_comp.MayPlace(itemName, entityId_block_pos, Facing.Up, dimensionId=dim)

        # print "plant", itemName, auxValue, "at", entityId_block_pos, result
        if result:
            # 获取掉落物品信息
            item = self.item_comp.GetDroppedItem(entityId, getUserData=True)
            if item["count"] == 1:
                # 如果只有一个物品，直接销毁实体并放置方块
                self.DestroyEntity(entityId)
                self.block_info_comp.SetBlockNew(entityId_block_pos, {"name": itemName, "aux": auxValue},
                                                 dimensionId=dim)
            else:
                # 如果有多个物品，减少数量并重新创建物品实体
                item["count"] -= 1
                self.DestroyEntity(entityId)
                self.block_info_comp.SetBlockNew(entityId_block_pos, {"name": itemName, "aux": auxValue},
                                                 dimensionId=dim)
                self.CreateEngineItemEntity(item, dimensionId=dim, pos=item_entity_pos)

    def add_vein(self, playerId, affected_list):
        """
        执行连锁破坏方块
        按顺序破坏方块列表中的所有方块

        Args:
            playerId: 玩家ID
            affected_list: 受影响的方块位置列表
        """
        if affected_list:
            # 将方块添加到玩家破坏集合中
            self.player_destroying[playerId].update(affected_list)
            player_block_info_comp = compFactory.CreateBlockInfo(playerId)

            # 破坏所有方块（最后一个方块触发掉落）
            for pos in affected_list[:-1]:
                player_block_info_comp.PlayerDestoryBlock(pos, 0, False)  # 不触发掉落
            player_block_info_comp.PlayerDestoryBlock(affected_list[-1], 0, True)  # 触发掉落

            # 清空玩家破坏集合
            self.player_destroying[playerId].clear()

    @staticmethod
    def get_tree_type(state, fullName):
        """
        获取树木类型
        根据方块状态和名称确定树木种类

        Args:
            state: 方块状态字典
            fullName: 方块完整名称

        Returns:
            str: 树木类型标识
        """
        if fullName == "minecraft:log":
            return state["old_log_type"]  # 旧版原木类型
        elif fullName == "minecraft:log2":
            return state["new_log_type"]  # 新版原木类型
        return fullName  # 直接返回方块名称

    @Listen.on("DestroyBlockEvent")
    def on_player_destroy_block(self, event):
        """
        方块破坏事件处理
        实现连锁砍树功能

        Args:
            event: 破坏事件数据，包含方块信息和玩家信息
        """
        # 检查砍树功能是否开启且限制数量大于0
        if not self.master_setting.tree_felling or self.master_setting.tree_felling_limit_count <= 0:
            return

        fullName = event["fullName"]
        # 检查破坏的方块是否为木头
        if fullName not in self.master_setting.log_blocks:
            return

        pos = event["x"], event["y"], event["z"]
        playerId = event["playerId"]

        # 检查该方块是否正在被破坏（避免重复处理）
        if pos in self.player_destroying[playerId]:
            self.player_destroying[playerId].discard(pos)
            return

        # 检查玩家是否开启了砍树功能
        state = self.player_tree_falling_state.get(playerId, False)
        if not state:
            return

        # 检查玩家手持的是否为斧头
        handItem = compFactory.CreateItem(playerId).GetPlayerItem(ItemPosType.CARRIED)
        if not handItem or not isAxe(handItem["newItemName"], handItem["newAuxValue"]):
            return

        dimensionId = event["dimensionId"]
        # 获取方块状态并确定树木类型
        oldBlockState = self.block_state_comp.GetBlockStatesFromAuxValue(fullName, event["auxData"])
        tree_type = self.get_tree_type(oldBlockState, fullName)

        # 使用广度优先搜索查找相连的木头方块
        searched = set()  # 已搜索的位置集合
        affected = []  # 受影响的方块列表
        queue = [pos]  # 待搜索的队列
        found_one_with_leaves = not self.master_setting.check_leave_persistent_bit  # 是否发现天然树叶

        while queue:
            start_pos = queue.pop()
            # 搜索周围的所有方向
            for offset in BLOCKSURROUNDINGS:
                search_pos = start_pos[0] + offset[0], start_pos[1] + offset[1], start_pos[2] + offset[2]
                if search_pos in searched:
                    continue
                searched.add(search_pos)

                # 获取搜索位置的方块信息
                block = self.block_info_comp.GetBlockNew(search_pos, dimensionId)
                if not block:
                    continue

                # 检查是否为同种木头
                if block["name"] == fullName:
                    state = self.block_state_comp.GetBlockStates(search_pos, dimensionId)
                    if not state or self.get_tree_type(state, block["name"]) == tree_type:
                        affected.append(search_pos)
                        queue.append(search_pos)
                        # 检查是否达到数量限制
                        if len(affected) >= self.master_setting.tree_felling_limit_count:
                            if not found_one_with_leaves:
                                # 没有发现天然树叶，不执行连锁
                                return
                            else:
                                # 执行连锁破坏
                                self.add_vein(playerId, affected)
                                return
                # 检查是否为树叶（用于验证是否为自然生成的树）
                elif not found_one_with_leaves and block["name"] in LEAVE_BLOCKS:
                    state = self.block_state_comp.GetBlockStates(search_pos, dimensionId)
                    if state and "persistent_bit" in state and not state["persistent_bit"]:
                        found_one_with_leaves = True  # 发现天然树叶

        # 如果发现天然树叶，执行连锁破坏
        if found_one_with_leaves:
            self.add_vein(playerId, affected)