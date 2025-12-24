"""
副本执行器
组合导航和战斗，执行完整副本流程
"""
import asyncio
import logging
from typing import Optional, Callable, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

from core.adb_controller import ADBController
from core.game_navigator import GameNavigator
from core.battle_loop import BattleLoop, BattleResult, BattlePhase
from core.image_matcher import image_matcher

logger = logging.getLogger("zat.dungeon")


class DungeonState(str, Enum):
    """副本运行状态"""
    IDLE = "idle"
    NAVIGATING = "navigating"  # 进入中
    MATCHING = "matching"      # 匹配中
    BATTLING = "battling"      # 进行中
    FINISHED = "finished"      # 已完成


# 难度模板映射
DIFFICULTY_TEMPLATES = {
    "normal": "daily_dungeon/difficulty/normal",
    "hard": "daily_dungeon/difficulty/hard",
    "nightmare": "daily_dungeon/difficulty/nightmare",
}

DIFFICULTY_SELECTED_TEMPLATES = {
    "normal": "daily_dungeon/difficulty/normal_selected",
    "hard": "daily_dungeon/difficulty/hard_selected",
    "nightmare": "daily_dungeon/difficulty/nightmare_selected",
}


@dataclass
class DungeonResult:
    """单次副本结果"""
    success: bool
    rank: Optional[str] = None
    message: str = ""


@dataclass
class DungeonRecord:
    """副本运行记录"""
    id: int
    dungeon_id: str
    dungeon_name: str
    difficulty: str
    difficulty_name: str
    rank: Optional[str]
    time: str  # HH:MM 格式
    status: str  # completed, failed, running


@dataclass
class DungeonRunResult:
    """多次副本运行结果"""
    total: int = 0
    completed: int = 0
    failed: int = 0
    ranks: list = field(default_factory=list)  # 每次的评级
    
    @property
    def success_rate(self) -> float:
        return self.completed / self.total if self.total > 0 else 0


# 副本名称映射
DUNGEON_NAMES = {
    "world_tree": "世界之树",
    "mount_mechagod": "机神山",
    "sea_palace": "海之宫遗迹",
    "mizumoto_shrine": "源水大社",
}

# 难度名称映射
DIFFICULTY_NAMES = {
    "normal": "普通",
    "hard": "困难",
    "nightmare": "噩梦",
}


class DungeonRunner:
    """副本执行器"""
    
    MAX_HISTORY = 10  # 最多保留的历史记录数
    
    def __init__(self, adb: ADBController, navigator: GameNavigator):
        self.adb = adb
        self.navigator = navigator
        self.battle_loop = BattleLoop(adb)
        self._running = False
        self._state = DungeonState.IDLE
        self._history: List[DungeonRecord] = []
        self._record_id = 0
        self._current_record: Optional[DungeonRecord] = None
        
        # 设置战斗阶段回调
        self.battle_loop.set_phase_callback(self._on_battle_phase_change)
    
    def _on_battle_phase_change(self, phase: BattlePhase):
        """战斗阶段变化回调"""
        if phase == BattlePhase.MATCHING:
            self._set_state(DungeonState.MATCHING)
        elif phase == BattlePhase.BATTLING:
            self._set_state(DungeonState.BATTLING)
    
    @property
    def state(self) -> DungeonState:
        """获取当前状态"""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running
    
    @property
    def history(self) -> List[DungeonRecord]:
        """获取历史记录"""
        return self._history.copy()
    
    def _set_state(self, state: DungeonState):
        """设置状态"""
        self._state = state
        logger.debug(f"状态变更: {state.value}")
    
    def _add_record(self, dungeon_id: str, difficulty: str, status: str = "running") -> DungeonRecord:
        """添加一条记录"""
        self._record_id += 1
        record = DungeonRecord(
            id=self._record_id,
            dungeon_id=dungeon_id,
            dungeon_name=DUNGEON_NAMES.get(dungeon_id, dungeon_id),
            difficulty=difficulty,
            difficulty_name=DIFFICULTY_NAMES.get(difficulty, difficulty),
            rank=None,
            time=datetime.now().strftime("%H:%M"),
            status=status,
        )
        self._history.insert(0, record)
        # 保持历史记录数量限制
        if len(self._history) > self.MAX_HISTORY:
            self._history = self._history[:self.MAX_HISTORY]
        self._current_record = record
        return record
    
    def _update_current_record(self, status: str, rank: Optional[str] = None):
        """更新当前记录"""
        if self._current_record:
            self._current_record.status = status
            if rank:
                self._current_record.rank = rank
    
    async def select_difficulty(self, difficulty: str) -> bool:
        """选择难度"""
        template = DIFFICULTY_TEMPLATES.get(difficulty)
        if not template:
            logger.error(f"未知难度: {difficulty}")
            return False
        
        # 检查是否已选中
        selected_template = DIFFICULTY_SELECTED_TEMPLATES.get(difficulty)
        if selected_template:
            screen = await self.adb.screencap_array()
            if image_matcher.match_template(screen, selected_template, threshold=0.7):
                logger.info(f"难度 {difficulty} 已选中")
                return True
        
        success = await self.navigator.click_template(template, timeout=3.0)
        if success:
            logger.info(f"已选择难度: {difficulty}")
        return success
    
    async def click_match(self) -> bool:
        """点击匹配按钮"""
        logger.info("点击匹配按钮")
        return await self.navigator.click_template("daily_dungeon/match", timeout=5.0)
    
    async def exit_result_screen(self) -> bool:
        """退出结算界面"""
        logger.info("退出结算界面")
        success = await self.navigator.click_template("back", timeout=5.0)
        if not success:
            logger.warning("点击返回失败，尝试按返回键")
            await self.navigator.press_back()
        return True
    
    async def run_once(self, dungeon_id: str, difficulty: str = "normal") -> DungeonResult:
        """
        执行单次副本
        
        流程：导航 -> 选难度 -> 匹配 -> 战斗循环 -> 退出结算
        """
        logger.info(f"开始副本: {dungeon_id} ({difficulty})")
        self._running = True
        
        # 添加记录
        self._add_record(dungeon_id, difficulty, "running")
        
        try:
            # 1. 导航到副本
            self._set_state(DungeonState.NAVIGATING)
            target_scene = f"dungeon:{dungeon_id}"
            if not await self.navigator.navigate_to(target_scene):
                self._set_state(DungeonState.IDLE)
                self._update_current_record("failed")
                return DungeonResult(success=False, message="导航到副本失败")
            
            await asyncio.sleep(0.5)
            
            # 2. 选择难度
            if not await self.select_difficulty(difficulty):
                self._set_state(DungeonState.IDLE)
                self._update_current_record("failed")
                return DungeonResult(success=False, message="选择难度失败")
            
            await asyncio.sleep(0.3)
            
            # 3. 点击匹配
            self._set_state(DungeonState.MATCHING)
            if not await self.click_match():
                self._set_state(DungeonState.IDLE)
                self._update_current_record("failed")
                return DungeonResult(success=False, message="点击匹配失败")
            
            # 4. 战斗循环（状态由 battle_loop 回调更新）
            battle_result = await self.battle_loop.run()
            if not battle_result.success:
                self._set_state(DungeonState.IDLE)
                self._update_current_record("failed")
                return DungeonResult(success=False, message=battle_result.message)
            
            await asyncio.sleep(1.0)
            
            # 5. 退出结算界面
            self._set_state(DungeonState.FINISHED)
            await self.exit_result_screen()
            
            logger.info(f"副本完成: {dungeon_id} ({difficulty}) - 评级: {battle_result.rank}")
            self._set_state(DungeonState.IDLE)
            self._update_current_record("completed", battle_result.rank)
            return DungeonResult(success=True, rank=battle_result.rank, message="副本完成")
        finally:
            self._running = False
            self._current_record = None
    
    async def run(self, dungeon_id: str, difficulty: str = "normal", count: int = 1) -> DungeonRunResult:
        """
        执行多次副本
        
        Args:
            dungeon_id: 副本ID
            difficulty: 难度
            count: 执行次数
        
        Returns:
            DungeonRunResult
        """
        logger.info(f"开始刷副本: {dungeon_id} ({difficulty}) x {count}")
        self._running = True
        
        result = DungeonRunResult(total=count)
        
        for i in range(count):
            if not self._running:
                logger.info("副本运行被中断")
                break
            
            logger.info(f"=== 第 {i + 1}/{count} 次 ===")
            
            dungeon_result = await self.run_once(dungeon_id, difficulty)
            
            if dungeon_result.success:
                result.completed += 1
                result.ranks.append(dungeon_result.rank)
            else:
                result.failed += 1
                logger.error(f"第 {i + 1} 次失败: {dungeon_result.message}")
                # 失败后尝试恢复到安全状态
                await self._try_recover()
            
            # 两次之间稍作等待
            if i < count - 1 and self._running:
                await asyncio.sleep(2.0)
        
        self._running = False
        logger.info(f"副本运行完成: {result.completed}/{result.total} 成功")
        return result
    
    async def _try_recover(self):
        """尝试恢复到安全状态"""
        logger.info("尝试恢复...")
        # 多次按返回键
        for _ in range(3):
            await self.navigator.press_back()
            await asyncio.sleep(0.5)
        
        # 重新检测场景
        await self.navigator.detect_current_scene()
    
    def stop(self):
        """停止运行"""
        self._running = False
        self._state = DungeonState.IDLE
        self.battle_loop.stop()
        logger.info("副本运行已停止")
