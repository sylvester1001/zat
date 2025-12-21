"""
战斗状态循环
负责战斗中的状态检测和操作
"""
import asyncio
import logging
from typing import Optional
from dataclasses import dataclass

from core.adb_controller import ADBController
from core.image_matcher import image_matcher

logger = logging.getLogger("zat.battle")


@dataclass
class BattleResult:
    """战斗结果"""
    success: bool
    rank: Optional[str] = None  # S/A/B/C
    message: str = ""


# 评级模板
RANK_TEMPLATES = {
    "S": "daily_dungeon/level/s",
    "A": "daily_dungeon/level/a",
    "B": "daily_dungeon/level/b",
    "C": "daily_dungeon/level/c",
}


class BattleLoop:
    """战斗状态循环"""
    
    def __init__(self, adb: ADBController):
        self.adb = adb
        self._running = False
    
    async def _detect_and_click(self, screen, template: str, threshold: float = 0.7) -> bool:
        """检测模板并点击（单次检测）"""
        result = image_matcher.match_template(screen, template, threshold=threshold)
        if result:
            x, y, confidence = result
            await self.adb.tap(x, y)
            logger.debug(f"点击: {template} at ({x}, {y})")
            return True
        return False
    
    async def _detect_rank(self, screen) -> Optional[str]:
        """检测评级"""
        for rank, template in RANK_TEMPLATES.items():
            if image_matcher.match_template(screen, template, threshold=0.7):
                return rank
        return None
    
    async def run(self, timeout: float = 600.0) -> BattleResult:
        """
        运行战斗循环
        
        持续检测屏幕，按优先级处理：
        1. 准备按钮 - 最高优先级（多个子地图都需要点击）
        2. 接受按钮 - 匹配成功后出现
        3. 评级 (S/A/B/C) - 战斗结束标志
        
        Args:
            timeout: 总超时时间（秒），默认10分钟
        
        Returns:
            BattleResult
        """
        logger.info("进入战斗循环...")
        self._running = True
        
        elapsed = 0
        interval = 1.5
        idle_time = 0
        max_idle = 90  # 最大无操作时间
        
        while self._running and elapsed < timeout:
            screen = await self.adb.screencap_array()
            action_taken = False
            
            # 优先级1: 检测准备按钮
            if await self._detect_and_click(screen, "ready"):
                logger.info("点击准备按钮")
                action_taken = True
                idle_time = 0
                await asyncio.sleep(1.0)
                continue
            
            # 优先级2: 检测接受按钮
            if await self._detect_and_click(screen, "accept"):
                logger.info("点击接受按钮")
                action_taken = True
                idle_time = 0
                await asyncio.sleep(0.5)
                continue
            
            # 优先级3: 检测评级（战斗结束）
            rank = await self._detect_rank(screen)
            if rank:
                logger.info(f"战斗完成，评级: {rank}")
                self._running = False
                return BattleResult(success=True, rank=rank, message="战斗完成")
            
            # 无操作，累计空闲时间
            if not action_taken:
                idle_time += interval
                if idle_time >= max_idle:
                    logger.warning(f"超过 {max_idle} 秒无操作")
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        self._running = False
        
        if elapsed >= timeout:
            return BattleResult(success=False, message="战斗超时")
        
        return BattleResult(success=False, message="战斗被中断")
    
    def stop(self):
        """停止战斗循环"""
        self._running = False
        logger.info("战斗循环已停止")
