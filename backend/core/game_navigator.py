"""
游戏场景导航器
负责场景检测和导航
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

logger = logging.getLogger("zat.navigator")


class GameNavigator:
    """游戏场景导航器"""
    
    def __init__(self, adb: ADBController):
        self.adb = adb
        scene_navigator.set_action_handler(self._execute_transition)
    
    async def _execute_transition(self, transition: Transition, from_scene: Scene) -> bool:
        """执行场景转移操作"""
        try:
            if transition.scroll:
                await self._scroll(transition.scroll, transition.scroll_distance)
                await asyncio.sleep(0.3)
            
            if transition.action == ActionType.CLICK:
                if not transition.template:
                    logger.error("CLICK 操作需要 template")
                    return False
                success = await self.click_template(transition.template)
                
            elif transition.action == ActionType.CLICK_TEXT:
                if not transition.text:
                    logger.error("CLICK_TEXT 操作需要 text")
                    return False
                success = await self._click_text(transition.text)
                
            elif transition.action == ActionType.BACK:
                if transition.template:
                    success = await self.click_template(transition.template)
                else:
                    success = await self.press_back()
                    
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
    
    async def click_template(self, template_name: str, timeout: float = 5.0, threshold: float = 0.7) -> bool:
        # 等待并点击模板
        elapsed = 0
        interval = 0.3
        attempt = 0
        
        while elapsed < timeout:
            attempt += 1
            screen = await self.adb.screencap_array()
            
            # 调试：每次都输出状态
            logger.debug(f"[{template_name}] 尝试 {attempt}, 帧率: {self.adb.capture_fps:.1f}")
            
            result = image_matcher.match_template(screen, template_name, threshold=threshold)
            
            if result:
                x, y, confidence = result
                await self.adb.tap(x, y)
                logger.info(f"点击模板: {template_name} at ({x}, {y}), 置信度: {confidence:.3f}")
                return True
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        # 匹配失败时保存当前帧用于调试
        import cv2
        import os
        debug_dir = os.path.dirname(os.path.dirname(__file__))
        debug_path = os.path.join(debug_dir, f"debug_fail_{template_name.replace('/', '_')}.png")
        cv2.imwrite(debug_path, screen)
        logger.warning(f"未找到模板: {template_name}, 已保存: {debug_path}")
        return False
    
    async def click_template_if_exists(self, screen, template_name: str, threshold: float = 0.7) -> bool:
        """检测模板存在则点击（单次检测，不等待）"""
        result = image_matcher.match_template(screen, template_name, threshold=threshold)
        if result:
            x, y, confidence = result
            await self.adb.tap(x, y)
            logger.debug(f"点击: {template_name} at ({x}, {y})")
            return True
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
    
    async def press_back(self) -> bool:
        """按返回键"""
        cmd = f'"{self.adb.adb_path}" -s {self.adb.device} shell input keyevent KEYCODE_BACK'
        await self.adb._run_command(cmd)
        logger.debug("按下返回键")
        return True
    
    async def detect_current_scene(self) -> Optional[str]:
        """检测当前场景"""
        screen = await self.adb.screencap_array()
        
        # 优先检测底部导航栏
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
            
            for template in scene.detect_templates:
                if image_matcher.match_template(screen, template, threshold=0.7):
                    logger.info(f"检测到场景: {scene.name}")
                    scene_navigator.current_scene = scene_id
                    return scene_id
            
            for text in scene.detect_texts:
                if image_matcher.ocr_find_text(screen, text):
                    logger.info(f"检测到场景: {scene.name}")
                    scene_navigator.current_scene = scene_id
                    return scene_id
        
        logger.warning("无法识别当前场景")
        scene_navigator.current_scene = None
        return None
    
    async def navigate_to(self, target_scene: str) -> bool:
        """导航到目标场景"""
        if scene_navigator.current_scene is None:
            detected = await self.detect_current_scene()
            if not detected:
                logger.error("无法检测当前场景，尝试返回主界面")
                for _ in range(5):
                    await self.press_back()
                    await asyncio.sleep(0.5)
                    detected = await self.detect_current_scene()
                    if detected:
                        break
                
                if not detected:
                    logger.error("无法确定当前场景")
                    return False
        
        return await scene_navigator.navigate_to(target_scene)
    
    def set_current_scene(self, scene_id: str):
        """手动设置当前场景"""
        if scene_id in SCENES:
            scene_navigator.current_scene = scene_id
            logger.info(f"设置当前场景: {SCENES[scene_id].name}")
        else:
            logger.warning(f"未知场景: {scene_id}")
    
    def get_current_scene(self) -> Optional[str]:
        """获取当前场景"""
        return scene_navigator.current_scene
