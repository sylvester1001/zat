"""
副本导航器
基于场景图实现游戏导航
"""
import asyncio
import logging
from typing import Optional

from core.adb_controller import ADBController
from core.image_matcher import image_matcher
from core.scene_graph import (
    scene_navigator, 
    Scene, 
    Transition, 
    ActionType,
    SCENES
)

logger = logging.getLogger("zat.dungeon")


class GameNavigator:
    """游戏导航器"""
    
    def __init__(self, adb: ADBController):
        self.adb = adb
        # 设置操作处理器
        scene_navigator.set_action_handler(self._execute_transition)
    
    async def _execute_transition(self, transition: Transition, from_scene: Scene) -> bool:
        """
        执行场景转移操作
        
        Args:
            transition: 转移定义
            from_scene: 来源场景
        
        Returns:
            成功返回 True
        """
        try:
            # 如果需要滑动，先滑动
            if transition.scroll:
                await self._scroll(transition.scroll, transition.scroll_distance)
                await asyncio.sleep(0.3)
            
            # 执行操作
            if transition.action == ActionType.CLICK:
                if not transition.template:
                    logger.error("CLICK 操作需要 template")
                    return False
                success = await self._click_template(transition.template)
                
            elif transition.action == ActionType.CLICK_TEXT:
                if not transition.text:
                    logger.error("CLICK_TEXT 操作需要 text")
                    return False
                success = await self._click_text(transition.text)
                
            elif transition.action == ActionType.BACK:
                if transition.template:
                    success = await self._click_template(transition.template)
                else:
                    # 默认点击返回按钮位置或使用系统返回
                    success = await self._press_back()
                    
            elif transition.action == ActionType.SWIPE:
                await self._scroll(transition.scroll or "down", transition.scroll_distance)
                success = True
            else:
                logger.error(f"未知操作类型: {transition.action}")
                return False
            
            if success:
                await asyncio.sleep(transition.wait_after)
            
            return success
            
        except Exception as e:
            logger.error(f"执行转移失败: {e}")
            return False
    
    async def _click_template(self, template_name: str, timeout: float = 5.0) -> bool:
        """点击模板"""
        elapsed = 0
        interval = 0.3
        
        while elapsed < timeout:
            screen = await self.adb.screencap_array()
            result = image_matcher.match_template(screen, template_name, threshold=0.7)
            
            if result:
                x, y, confidence = result
                await self.adb.tap(x, y)
                logger.debug(f"点击模板: {template_name} at ({x}, {y})")
                return True
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        logger.warning(f"未找到模板: {template_name}")
        return False
    
    async def _click_text(self, text: str, timeout: float = 5.0) -> bool:
        """点击文字"""
        elapsed = 0
        interval = 0.5
        
        while elapsed < timeout:
            screen = await self.adb.screencap_array()
            result = image_matcher.ocr_find_text(screen, text)
            
            if result:
                x, y, confidence = result
                await self.adb.tap(x, y)
                logger.debug(f"点击文字: {text} at ({x}, {y})")
                return True
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        logger.warning(f"未找到文字: {text}")
        return False
    
    async def _scroll(self, direction: str, distance: int = 500):
        """滑动屏幕"""
        screen = await self.adb.screencap_array()
        h, w = screen.shape[:2]
        
        start_x = w // 2
        start_y = h // 2
        
        if direction == "down":
            end_y = start_y + distance
        elif direction == "up":
            end_y = start_y - distance
        else:
            logger.warning(f"未知滑动方向: {direction}")
            return
        
        await self.adb.swipe(start_x, start_y, start_x, end_y, duration=300)
        logger.debug(f"滑动: {direction} {distance}px")
        await asyncio.sleep(0.5)
    
    async def _press_back(self) -> bool:
        """按返回键"""
        # 使用 Android 系统返回键
        cmd = f'"{self.adb.adb_path}" -s {self.adb.device} shell input keyevent KEYCODE_BACK'
        await self.adb._run_command(cmd)
        logger.debug("按下返回键")
        return True
    
    async def detect_current_scene(self) -> Optional[str]:
        """
        检测当前场景
        
        Returns:
            场景ID，如果无法识别返回 None
        """
        screen = await self.adb.screencap_array()
        
        # 优先检测底部导航栏（最可靠）
        tab_scenes = ["home", "note", "character", "guild", "world"]
        for scene_id in tab_scenes:
            scene = SCENES.get(scene_id)
            if scene:
                for template in scene.detect_templates:
                    if image_matcher.match_template(screen, template, threshold=0.7):
                        logger.info(f"检测到场景: {scene.name}")
                        scene_navigator.current_scene = scene_id
                        return scene_id
        
        # 检测其他场景
        for scene_id, scene in SCENES.items():
            if scene_id in tab_scenes:
                continue
            
            # 检测模板
            for template in scene.detect_templates:
                if image_matcher.match_template(screen, template, threshold=0.7):
                    logger.info(f"检测到场景: {scene.name}")
                    scene_navigator.current_scene = scene_id
                    return scene_id
            
            # 检测文字
            for text in scene.detect_texts:
                if image_matcher.ocr_find_text(screen, text):
                    logger.info(f"检测到场景: {scene.name}")
                    scene_navigator.current_scene = scene_id
                    return scene_id
        
        logger.warning("无法识别当前场景")
        scene_navigator.current_scene = None
        return None
    
    async def navigate_to(self, target_scene: str) -> bool:
        """
        导航到目标场景
        
        Args:
            target_scene: 目标场景ID
        
        Returns:
            成功返回 True
        """
        # 如果当前场景未知，先检测
        if scene_navigator.current_scene is None:
            detected = await self.detect_current_scene()
            if not detected:
                logger.error("无法检测当前场景，尝试返回主界面")
                # 尝试多次按返回键回到主界面
                for _ in range(5):
                    await self._press_back()
                    await asyncio.sleep(0.5)
                    detected = await self.detect_current_scene()
                    if detected:
                        break
                
                if not detected:
                    logger.error("无法确定当前场景")
                    return False
        
        return await scene_navigator.navigate_to(target_scene)
    
    async def navigate_to_dungeon(self, dungeon_id: str) -> bool:
        """
        导航到指定副本
        
        Args:
            dungeon_id: 副本ID (world_tree, mount_mechagod, sea_palace, mizumoto_shrine)
        
        Returns:
            成功返回 True
        """
        target_scene = f"dungeon:{dungeon_id}"
        
        if target_scene not in SCENES:
            logger.error(f"未知副本: {dungeon_id}")
            return False
        
        return await self.navigate_to(target_scene)
    
    def set_current_scene(self, scene_id: str):
        """手动设置当前场景（用于已知状态时跳过检测）"""
        if scene_id in SCENES:
            scene_navigator.current_scene = scene_id
            logger.info(f"设置当前场景: {SCENES[scene_id].name}")
        else:
            logger.warning(f"未知场景: {scene_id}")
    
    def get_current_scene(self) -> Optional[str]:
        """获取当前场景"""
        return scene_navigator.current_scene
