# 游戏导航器
# 对外暴露的高层 API，封装 SceneNavigator

import logging
from typing import Optional

from core.adb_controller import ADBController
from core.image_matcher import image_matcher
from core.scene_navigator import SceneNavigator
from core.scene_registry import registry

# 导入场景定义（触发注册）
import scenes

logger = logging.getLogger("zat.game_navigator")


class GameNavigator:
    # 游戏导航器：对外暴露的高层 API
    
    def __init__(self, adb: ADBController):
        self.adb = adb
        self.navigator = SceneNavigator(adb, image_matcher)
    
    async def navigate_to(self, target_scene: str) -> bool:
        # 导航到目标场景
        return await self.navigator.navigate_to(target_scene)
    
    async def detect_current_scene(self) -> str:
        # 检测当前场景
        return await self.navigator.observer.observe()
    
    async def click_template(self, template_name: str, timeout: float = 5.0, threshold: float = 0.7) -> bool:
        # 等待并点击模板
        return await self.navigator._click_template(template_name, timeout, threshold)
    
    async def click_template_if_exists(self, screen, template_name: str, threshold: float = 0.7) -> bool:
        # 检测模板存在则点击（单次检测，不等待）
        result = image_matcher.match_template(screen, template_name, threshold=threshold)
        if result:
            x, y, _ = result
            await self.adb.tap(x, y)
            logger.debug(f"点击: {template_name} at ({x}, {y})")
            return True
        return False
    
    async def press_back(self) -> bool:
        # 按返回键
        return await self.navigator._press_back()
    
    def get_scene_info(self, scene_id: str) -> Optional[dict]:
        # 获取场景信息
        scene = registry.get(scene_id)
        if scene:
            return {
                "id": scene.id,
                "name": scene.name,
                "fingerprint": scene.fingerprint,
                "transitions": list(scene.transitions.keys()),
                "back_to": scene.back_to,
            }
        return None
    
    def get_all_scenes(self) -> list[str]:
        # 获取所有已注册的场景ID
        return list(registry.get_all().keys())
