# 副本执行器
# 组合导航和战斗，执行完整副本流程

import asyncio
import logging
from typing import Optional, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from core.adb_controller import ADBController
from core.game_navigator import GameNavigator
from core.battle_loop import BattleLoop, BattlePhase
from core.image_matcher import image_matcher

logger = logging.getLogger("zat.dungeon")


class DungeonState(str, Enum):
    # 副本运行状态
    IDLE = "idle"
    NAVIGATING = "navigating"
    MATCHING = "matching"
    BATTLING = "battling"
    FINISHED = "finished"


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
    # 单次副本结果
    success: bool
    rank: Optional[str] = None
    message: str = ""


@dataclass
class DungeonRecord:
    # 副本运行记录
    id: int
    dungeon_id: str
    dungeon_name: str
    difficulty: str
    difficulty_name: str
    rank: Optional[str]
    time: str
    status: str


@dataclass
class DungeonRunResult:
    # 多次副本运行结果
    total: int = 0
    completed: int = 0
    failed: int = 0
    ranks: list = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        return self.completed / self.total if self.total > 0 else 0


DUNGEON_NAMES = {
    "world_tree": "世界之树",
    "mount_mechagod": "机神山",
    "sea_palace": "海之宫遗迹",
    "mizumoto_shrine": "源水大社",
}

DIFFICULTY_NAMES = {
    "normal": "普通",
    "hard": "困难",
    "nightmare": "噩梦",
}


class DungeonRunner:
    # 副本执行器
    
    MAX_HISTORY = 10
    
    def __init__(self, adb: ADBController, navigator: GameNavigator):
        self.adb = adb
        self.navigator = navigator
        self.battle_loop = BattleLoop(adb)
        
        self._running = False
        self._stop_requested = False
        self._state = DungeonState.IDLE
        self._history: List[DungeonRecord] = []
        self._record_id = 0
        self._current_record: Optional[DungeonRecord] = None
        
        self.battle_loop.set_phase_callback(self._on_battle_phase_change)
    
    @property
    def state(self) -> DungeonState:
        return self._state
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    @property
    def history(self) -> List[DungeonRecord]:
        return self._history.copy()
    
    def _on_battle_phase_change(self, phase: BattlePhase):
        if phase == BattlePhase.MATCHING:
            self._set_state(DungeonState.MATCHING)
        elif phase == BattlePhase.BATTLING:
            self._set_state(DungeonState.BATTLING)
    
    def _set_state(self, state: DungeonState):
        self._state = state
        logger.debug(f"状态变更: {state.value}")
    
    def _add_record(self, dungeon_id: str, difficulty: str, status: str = "running") -> DungeonRecord:
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
        if len(self._history) > self.MAX_HISTORY:
            self._history = self._history[:self.MAX_HISTORY]
        self._current_record = record
        return record
    
    def _update_current_record(self, status: str, rank: Optional[str] = None):
        if self._current_record:
            self._current_record.status = status
            if rank:
                self._current_record.rank = rank

    
    # ============================================================
    #  停止控制
    # ============================================================
    
    def stop(self):
        # 外部调用此方法终止运行
        if self._running:
            logger.info("收到停止指令...")
            self._stop_requested = True
            self.battle_loop.stop()
    
    async def _check_stop(self):
        # 内部检查点，如果收到停止请求则抛出异常中断流程
        if self._stop_requested:
            raise asyncio.CancelledError("用户终止操作")
    
    # ============================================================
    #  上下文管理器 - 统一管理 running 状态
    # ============================================================
    
    @asynccontextmanager
    async def _run_context(self):
        # 核心上下文管理器：负责统一管理 running 状态
        # 无论单次还是多次，都必须在这个上下文中运行
        if self._running:
            logger.warning("任务已在运行中，忽略新请求")
            yield False
            return
        
        self._running = True
        self._stop_requested = False
        logger.info("任务启动")
        
        try:
            yield True
        except asyncio.CancelledError:
            logger.info("任务被用户终止")
        except Exception as e:
            logger.error(f"任务发生未捕获异常: {e}", exc_info=True)
        finally:
            self._running = False
            self._stop_requested = False
            self._set_state(DungeonState.IDLE)
            self._current_record = None
            logger.info("任务结束，状态已重置")

    
    # ============================================================
    #  核心逻辑层 (Private) - 只负责"怎么做"，不负责"做几次"
    # ============================================================
    
    async def _execute_dungeon_flow(self, dungeon_id: str, difficulty: str, skip_navigate: bool) -> DungeonResult:
        # 执行一次完整的副本流程
        # 不包含 while 循环，不包含 running 状态的开启/关闭（由调用者负责）
        
        self._add_record(dungeon_id, difficulty, "running")
        
        try:
            await self._check_stop()
            
            # 1. 导航
            if not skip_navigate:
                self._set_state(DungeonState.NAVIGATING)
                target_scene = f"dungeon:{dungeon_id}"
                if not await self.navigator.navigate_to(target_scene):
                    raise Exception("导航失败")
                await asyncio.sleep(0.5)
            
            await self._check_stop()
            
            # 2. 选难度
            if not await self._select_difficulty(difficulty):
                raise Exception("选择难度失败")
            await asyncio.sleep(0.3)
            
            await self._check_stop()
            
            # 3. 匹配
            self._set_state(DungeonState.MATCHING)
            if not await self._click_match():
                raise Exception("点击匹配失败")
            
            # 4. 战斗
            battle_result = await self.battle_loop.run()
            
            await self._check_stop()
            
            if not battle_result.success:
                raise Exception(f"战斗失败: {battle_result.message}")
            
            # 5. 结算
            self._set_state(DungeonState.FINISHED)
            await asyncio.sleep(1.0)
            await self._exit_result_screen()
            
            # 成功完成
            self._update_current_record("completed", battle_result.rank)
            logger.info(f"副本完成: {dungeon_id} ({difficulty}) - 评级: {battle_result.rank}")
            return DungeonResult(success=True, rank=battle_result.rank)
            
        except asyncio.CancelledError:
            self._update_current_record("failed")
            return DungeonResult(success=False, message="用户终止")
        except Exception as e:
            logger.error(f"单次流程异常: {e}")
            self._update_current_record("failed")
            if not self._stop_requested:
                await self._try_recover()
            return DungeonResult(success=False, message=str(e))

    
    # ============================================================
    #  公共接口层 (Public) - 负责"做几次"和"怎么调度"
    # ============================================================
    
    async def run_once(self, dungeon_id: str, difficulty: str = "normal") -> DungeonResult:
        # 单次运行入口
        async with self._run_context() as active:
            if not active:
                return DungeonResult(success=False, message="任务正在运行中")
            return await self._execute_dungeon_flow(dungeon_id, difficulty, skip_navigate=False)
    
    async def run_loop(self, dungeon_id: str, difficulty: str = "normal", count: int = -1) -> DungeonRunResult:
        # 多次/无限循环入口
        async with self._run_context() as active:
            if not active:
                return DungeonRunResult()
            
            is_infinite = count == -1
            result = DungeonRunResult(total=0 if is_infinite else count)
            need_navigate = True
            i = 0
            
            while not self._stop_requested:
                if not is_infinite and i >= count:
                    break
                
                i += 1
                logger.info(f"=== 第 {i}" + (f"/{count}" if not is_infinite else "") + " 次 ===")
                
                step_res = await self._execute_dungeon_flow(dungeon_id, difficulty, skip_navigate=not need_navigate)
                
                if self._stop_requested:
                    break
                
                if is_infinite:
                    result.total = i
                
                if step_res.success:
                    result.completed += 1
                    result.ranks.append(step_res.rank)
                    need_navigate = False
                else:
                    result.failed += 1
                    need_navigate = True
                
                if not self._stop_requested:
                    await asyncio.sleep(1.5)
            
            logger.info(f"副本运行完成: {result.completed}/{result.total} 成功")
            return result

    
    # ============================================================
    #  游戏操作方法 (Private)
    # ============================================================
    
    async def _select_difficulty(self, difficulty: str) -> bool:
        template = DIFFICULTY_TEMPLATES.get(difficulty)
        if not template:
            logger.error(f"未知难度: {difficulty}")
            return False
        
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
    
    async def _click_match(self) -> bool:
        logger.info("点击匹配按钮")
        return await self.navigator.click_template("daily_dungeon/match", timeout=5.0)
    
    async def _click_confirm_skip_reward(self) -> bool:
        # 点击确认跳过奖励弹窗（不是每次都有）
        return await self.navigator.click_template("daily_dungeon/confirm", timeout=2.0, threshold=0.6)
    
    async def _exit_result_screen(self) -> bool:
        logger.info("退出结算界面")
        success = await self.navigator.click_template("back", timeout=5.0)
        if not success:
            logger.warning("点击返回失败，尝试按返回键")
            await self.navigator.press_back()
        
        # 等待动画，处理可能出现的跳过奖励弹窗
        await asyncio.sleep(1.0)
        if await self._click_confirm_skip_reward():
            logger.info("已确认跳过奖励")
            await asyncio.sleep(0.5)
        
        return True
    
    async def _try_recover(self):
        logger.info("尝试恢复...")
        for _ in range(3):
            await self.navigator.press_back()
            await asyncio.sleep(0.5)
        await self.navigator.detect_current_scene()
