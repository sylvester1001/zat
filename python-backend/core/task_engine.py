"""
任务引擎
负责执行任务流程
"""
import asyncio
import logging
from typing import Optional

from core.adb_controller import ADBController
from core.image_matcher import image_matcher
from utils.logger import LogBroadcaster

logger = logging.getLogger("zat.task")


class TaskEngine:
    """任务引擎"""
    
    # 游戏启动页面的关键文字
    CLICK_TO_START_TEXT = "点击任意处开始游戏"
    
    def __init__(self, adb: ADBController, log_broadcaster: LogBroadcaster):
        self.adb = adb
        self.log_broadcaster = log_broadcaster
        
        self.current_state: Optional[str] = None
        self.loop_count: int = 0
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None
    
    def is_running(self) -> bool:
        """检查任务是否正在运行"""
        return self._running
    
    async def start(self, task_name: str):
        """启动任务"""
        if self._running:
            raise RuntimeError("任务已在运行")
        
        self._running = True
        self.loop_count = 0
        self.current_state = "STARTING"
        
        # 创建任务
        self._task = asyncio.create_task(self._run_task(task_name))
        
        logger.info(f"任务引擎已启动: {task_name}")
    
    async def stop(self):
        """停止任务"""
        if not self._running:
            return
        
        self._running = False
        self.current_state = "STOPPING"
        
        # 取消任务
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        self.current_state = "STOPPED"
        logger.info("任务引擎已停止")
    
    async def wait_for_game_ready(self, timeout: int = 60, check_interval: float = 2.0) -> bool:
        """
        等待游戏加载完成，检测「点击任意处开始游戏」文字
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检测间隔（秒）
        
        Returns:
            True 如果成功进入游戏，False 如果超时
        """
        logger.info("等待游戏加载...")
        self.current_state = "WAITING_GAME_READY"
        
        elapsed = 0
        while elapsed < timeout:
            if not self._running:
                return False
            
            try:
                # 截图
                screen = await self.adb.screencap_array()
                h, w = screen.shape[:2]
                
                logger.debug(f"截图成功，尺寸: {w}x{h}")
                
                # OCR 查找「点击任意处开始游戏」
                # 先搜索整个屏幕，确保能找到
                result = image_matcher.ocr_find_text(
                    screen, 
                    self.CLICK_TO_START_TEXT
                )
                
                if result:
                    x, y, confidence = result
                    logger.info(f"检测到游戏启动页面，点击文字位置 ({x}, {y}) 进入游戏...")
                    
                    # 点击识别到的文字位置
                    await self.adb.tap(x, y)
                    
                    # 等待一下让游戏响应
                    await asyncio.sleep(1.5)
                    
                    self.current_state = "GAME_READY"
                    logger.info("已进入游戏")
                    return True
                
            except Exception as e:
                logger.warning(f"检测游戏状态失败: {e}")
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            logger.debug(f"等待游戏加载... ({elapsed:.0f}s/{timeout}s)")
        
        logger.warning(f"等待游戏加载超时 ({timeout}s)")
        return False
    
    async def _run_task(self, task_name: str):
        """运行任务（内部方法）"""
        try:
            logger.info(f"开始执行任务: {task_name}")
            
            # TODO: 加载任务配置
            # TODO: 执行任务流程
            
            # 临时：简单的测试循环
            while self._running:
                self.current_state = "RUNNING"
                self.loop_count += 1
                
                logger.info(f"任务循环 #{self.loop_count}")
                
                # 模拟任务执行
                await asyncio.sleep(5)
            
        except asyncio.CancelledError:
            logger.info("任务已取消")
            raise
        except Exception as e:
            logger.error(f"任务执行失败: {e}", exc_info=True)
            self.current_state = "ERROR"
        finally:
            self._running = False
