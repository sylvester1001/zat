# 游戏启动器
# 负责游戏的启动、停止和状态检测

import asyncio
import logging
from typing import Optional

from core.adb_controller import ADBController
from core.image_matcher import image_matcher

logger = logging.getLogger("zat.game")

# 游戏配置
GAME_PACKAGE = "com.leiting.zjcs"
GAME_ACTIVITY = "com.leiting.unity.AppActivity"


class GameLauncher:
    # 游戏启动器
    
    # 游戏启动页面的关键文字
    CLICK_TO_START_TEXT = "点击任意处开始游戏"
    
    def __init__(self, adb: ADBController):
        self.adb = adb
        self._waiting = False  # 是否正在等待游戏加载
    
    async def start(self, wait_ready: bool = False, timeout: int = 60) -> dict:
        # 启动游戏
        # wait_ready: 是否等待游戏加载完成并自动点击进入
        # timeout: 等待超时时间（秒）
        # Returns: {success, package, entered?, message?}
        try:
            await self.adb.start_app(GAME_PACKAGE, GAME_ACTIVITY)
            logger.info(f"游戏已启动: {GAME_PACKAGE}")
            
            if wait_ready:
                self._waiting = True
                try:
                    entered = await self._wait_for_ready(timeout)
                    if not self._waiting:
                        # 被中断
                        return {"success": True, "package": GAME_PACKAGE, "entered": False, "message": "已取消"}
                    if not entered:
                        return {"success": True, "package": GAME_PACKAGE, "entered": False, "message": "等待进入超时"}
                    return {"success": True, "package": GAME_PACKAGE, "entered": True}
                finally:
                    self._waiting = False
            
            return {"success": True, "package": GAME_PACKAGE}
        except Exception as e:
            logger.error(f"启动游戏失败: {e}")
            return {"success": False, "message": str(e)}
    
    async def stop(self) -> dict:
        # 停止游戏
        # Returns: {success, message?}
        try:
            # 中断等待
            self._waiting = False
            
            await self.adb.stop_app(GAME_PACKAGE)
            logger.info(f"游戏已停止: {GAME_PACKAGE}")
            return {"success": True}
        except Exception as e:
            logger.error(f"停止游戏失败: {e}")
            return {"success": False, "message": str(e)}
    
    async def is_running(self) -> bool:
        # 检查游戏是否正在运行
        try:
            return await self.adb.is_app_running(GAME_PACKAGE)
        except Exception:
            return False
    
    def is_waiting(self) -> bool:
        # 检查是否正在等待游戏加载
        return self._waiting
    
    async def _wait_for_ready(self, timeout: int = 60, check_interval: float = 0.5) -> bool:
        # 等待游戏加载完成，检测「点击任意处开始游戏」文字
        # timeout: 超时时间（秒）
        # check_interval: 检测间隔（秒）
        # Returns: True 如果成功进入游戏，False 如果超时或被中断
        logger.info("等待游戏加载...")
        
        elapsed = 0
        check_count = 0
        
        while elapsed < timeout:
            # 检查是否被中断
            if not self._waiting:
                logger.info("等待游戏加载被中断")
                return False
            
            check_count += 1
            try:
                screen = await self.adb.screencap_array()
                h, w = screen.shape[:2]
                
                # 每 20 次检测输出一次日志
                if check_count % 20 == 1:
                    logger.debug(f"检测中... ({elapsed:.1f}s/{timeout}s)")
                
                # 只搜索屏幕下方 1/4 区域
                region = (0, int(h * 0.75), w, int(h * 0.25))
                
                # 优先使用模板匹配（速度快）
                result = image_matcher.match_template(screen, "start", threshold=0.7)
                
                # 如果模板匹配失败，使用 OCR 作为备用
                if not result:
                    result = image_matcher.ocr_find_text(
                        screen,
                        self.CLICK_TO_START_TEXT,
                        region=region
                    )
                
                if result:
                    x, y, confidence = result
                    logger.info(f"检测到游戏启动页面 (置信度: {confidence:.2f})，点击进入...")
                    
                    await self.adb.tap(x, y)
                    await asyncio.sleep(1.0)
                    
                    logger.info("已进入游戏")
                    return True
                
            except Exception as e:
                if not self._waiting:
                    return False
                logger.warning(f"检测游戏状态失败: {e}")
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        logger.warning(f"等待游戏加载超时 ({timeout}s)")
        return False
