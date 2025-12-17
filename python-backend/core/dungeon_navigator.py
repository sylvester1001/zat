"""
副本导航器
负责从主界面导航到指定副本
"""
import asyncio
import logging
from typing import Optional
from enum import Enum

from core.adb_controller import ADBController
from core.image_matcher import image_matcher

logger = logging.getLogger("zat.dungeon")


class DungeonType(str, Enum):
    """副本类型"""
    WORLD_TREE = "world-tree"           # 世界之树
    MOUNT_MECHAGOD = "mount-mechagod"   # 机神山
    SEA_PALACE = "sea-palace"           # 海之宫遗迹
    MIZUMOTO_SHRINE = "mizumoto-shrine" # 源水大社


class DungeonDifficulty(str, Enum):
    """副本难度"""
    NORMAL = "normal"     # 普通
    HARD = "hard"         # 困难
    NIGHTMARE = "nightmare"  # 噩梦 (仅源水大社)


# 副本信息配置
DUNGEON_CONFIG = {
    DungeonType.WORLD_TREE: {
        "name": "世界之树",
        "template": "daily-dungeon/world-tree",
        "needs_scroll": True,  # 需要向上滑动才能看到
        "difficulties": [DungeonDifficulty.NORMAL, DungeonDifficulty.HARD],
    },
    DungeonType.MOUNT_MECHAGOD: {
        "name": "机神山",
        "template": "daily-dungeon/mount-mechagod",
        "needs_scroll": True,
        "difficulties": [DungeonDifficulty.NORMAL, DungeonDifficulty.HARD],
    },
    DungeonType.SEA_PALACE: {
        "name": "海之宫遗迹",
        "template": "daily-dungeon/sea-palace",
        "needs_scroll": False,
        "difficulties": [DungeonDifficulty.NORMAL, DungeonDifficulty.HARD],
    },
    DungeonType.MIZUMOTO_SHRINE: {
        "name": "源水大社",
        "template": "daily-dungeon/mizumoto-shrine",
        "needs_scroll": False,
        "difficulties": [DungeonDifficulty.NORMAL, DungeonDifficulty.HARD, DungeonDifficulty.NIGHTMARE],
    },
}


class DungeonNavigator:
    """副本导航器"""
    
    def __init__(self, adb: ADBController):
        self.adb = adb
    
    async def _wait_and_find(
        self, 
        template_name: str, 
        timeout: float = 5.0,
        threshold: float = 0.7,
        interval: float = 0.3
    ) -> Optional[tuple[int, int]]:
        """
        等待并查找模板
        
        Returns:
            找到返回 (x, y)，超时返回 None
        """
        elapsed = 0
        while elapsed < timeout:
            screen = await self.adb.screencap_array()
            result = image_matcher.match_template(screen, template_name, threshold)
            if result:
                return (result[0], result[1])
            await asyncio.sleep(interval)
            elapsed += interval
        return None
    
    async def _click_template(
        self, 
        template_name: str, 
        timeout: float = 5.0,
        threshold: float = 0.7
    ) -> bool:
        """
        查找并点击模板
        
        Returns:
            成功返回 True，失败返回 False
        """
        pos = await self._wait_and_find(template_name, timeout, threshold)
        if pos:
            await self.adb.tap(pos[0], pos[1])
            logger.info(f"点击: {template_name} at ({pos[0]}, {pos[1]})")
            return True
        logger.warning(f"未找到模板: {template_name}")
        return False
    
    async def _scroll_down(self, distance: int = 400):
        """向下滑动（手指从下往上滑，内容向下滚动）"""
        screen = await self.adb.screencap_array()
        h, w = screen.shape[:2]
        start_x = w // 2
        start_y = h // 2
        end_y = start_y + distance  # 向下滑动
        
        await self.adb.swipe(start_x, start_y, start_x, end_y, duration=300)
        logger.debug(f"向下滑动: {distance}px")
        await asyncio.sleep(0.5)  # 等待滑动动画
    
    async def navigate_to_dungeon(
        self, 
        dungeon_type: DungeonType,
        difficulty: DungeonDifficulty = DungeonDifficulty.NORMAL
    ) -> bool:
        """
        从主界面导航到指定副本
        
        流程:
        1. 点击「笔记」标签
        2. 点击「日常副本」
        3. 如果需要，向上滑动
        4. 点击目标副本
        
        Args:
            dungeon_type: 副本类型
            difficulty: 副本难度
        
        Returns:
            成功返回 True，失败返回 False
        """
        config = DUNGEON_CONFIG.get(dungeon_type)
        if not config:
            logger.error(f"未知副本类型: {dungeon_type}")
            return False
        
        # 检查难度是否支持
        if difficulty not in config["difficulties"]:
            logger.error(f"副本 {config['name']} 不支持难度: {difficulty}")
            return False
        
        logger.info(f"开始导航到副本: {config['name']} ({difficulty.value})")
        
        # Step 1: 点击「笔记」标签
        logger.info("Step 1: 点击笔记标签")
        if not await self._click_template("note", timeout=3.0):
            # 可能已经在笔记页面，检查是否已选中
            screen = await self.adb.screencap_array()
            if not image_matcher.match_template(screen, "note-selected", 0.7):
                logger.error("无法找到笔记标签")
                return False
            logger.info("已在笔记页面")
        
        await asyncio.sleep(0.8)  # 等待页面切换
        
        # Step 2: 点击「日常副本」
        logger.info("Step 2: 点击日常副本")
        if not await self._click_template("daily-dungeon/daily-dungeon", timeout=5.0):
            logger.error("无法找到日常副本入口")
            return False
        
        await asyncio.sleep(1.0)  # 等待副本列表加载
        
        # Step 3: 如果需要，向下滑动（世界之树和机神山在列表上方，需要向下滑动才能看到）
        if config["needs_scroll"]:
            logger.info("Step 3: 向下滑动查看更多副本")
            await self._scroll_down(500)
            await asyncio.sleep(0.5)
        
        # Step 4: 点击目标副本
        logger.info(f"Step 4: 点击副本 {config['name']}")
        if not await self._click_template(config["template"], timeout=5.0, threshold=0.6):
            logger.error(f"无法找到副本: {config['name']}")
            return False
        
        await asyncio.sleep(0.5)
        
        # TODO: Step 5: 选择难度（下一阶段实现）
        
        logger.info(f"成功导航到副本: {config['name']}")
        return True
    
    async def get_current_tab(self) -> Optional[str]:
        """
        检测当前所在的标签页
        
        Returns:
            标签名称: home, note, character, guild, world
            如果无法识别返回 None
        """
        screen = await self.adb.screencap_array()
        
        tabs = ["home", "note", "character", "guild", "world"]
        for tab in tabs:
            if image_matcher.match_template(screen, f"{tab}-selected", 0.7):
                return tab
        
        return None
