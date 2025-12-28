# 战斗状态循环
# 负责战斗中的状态检测和操作

import asyncio
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

from core.adb_controller import ADBController
from core.image_matcher import image_matcher

logger = logging.getLogger("zat.battle")


class BattlePhase(str, Enum):
    # 战斗阶段
    MATCHING = "matching"    # 匹配中（等待接受）
    BATTLING = "battling"    # 进行中（已点击准备）


@dataclass
class BattleResult:
    # 战斗结果
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
    # 战斗状态循环
    
    def __init__(self, adb: ADBController):
        self.adb = adb
        self._running = False
        self._phase = BattlePhase.MATCHING
        self._on_phase_change: Optional[Callable[[BattlePhase], None]] = None
    
    def set_phase_callback(self, callback: Callable[[BattlePhase], None]):
        # 设置阶段变化回调
        self._on_phase_change = callback
    
    def _set_phase(self, phase: BattlePhase):
        # 设置阶段并触发回调
        if self._phase != phase:
            self._phase = phase
            logger.debug(f"战斗阶段: {phase.value}")
            if self._on_phase_change:
                self._on_phase_change(phase)
    
    async def _detect_and_click(self, screen, template: str, threshold: float = 0.7) -> bool:
        # 检测模板并点击（单次检测）
        result = image_matcher.match_template(screen, template, threshold=threshold)
        if result:
            x, y, confidence = result
            await self.adb.tap(x, y)
            logger.debug(f"点击: {template} at ({x}, {y})")
            return True
        return False
    
    async def _detect_rank(self, screen) -> Optional[str]:
        # 检测评级
        for rank, template in RANK_TEMPLATES.items():
            if image_matcher.match_template(screen, template, threshold=0.7):
                return rank
        return None
    
    async def run(self, timeout: float = 600.0) -> BattleResult:
        # 运行战斗循环
        # 阶段流转：
        # - MATCHING: 检测接受按钮，点击后可能被拒绝回到匹配
        # - BATTLING: 点击准备后进入，只检测准备按钮（多子地图）和评级
        # timeout: 总超时时间（秒），默认10分钟
        # Returns: BattleResult
        logger.info("进入战斗循环...")
        self._running = True
        self._set_phase(BattlePhase.MATCHING)
        
        elapsed = 0
        interval = 1.5
        idle_time = 0
        max_idle = 90
        
        try:
            while self._running and elapsed < timeout:
                screen = await self.adb.screencap_array()
                action_taken = False
                
                # 优先级1: 检测准备按钮（点击后进入 BATTLING 阶段）
                if await self._detect_and_click(screen, "ready"):
                    logger.info("点击准备按钮")
                    self._set_phase(BattlePhase.BATTLING)
                    action_taken = True
                    idle_time = 0
                    await asyncio.sleep(1.0)
                    continue
                
                # 优先级2: 检测接受按钮（仅在 MATCHING 阶段）
                if self._phase == BattlePhase.MATCHING:
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
            
            if elapsed >= timeout:
                return BattleResult(success=False, message="战斗超时")
            
            return BattleResult(success=False, message="战斗被中断")
        
        except asyncio.CancelledError:
            logger.info("战斗循环被取消")
            raise
        finally:
            self._running = False
    
    def stop(self):
        # 停止战斗循环
        self._running = False
        logger.info("战斗循环已停止")
