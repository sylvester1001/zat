# 场景观察者
# 负责截图并识别当前场景，是"眼睛"的角色

import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.adb_controller import ADBController
    from core.image_matcher import ImageMatcher

from core.scene_registry import registry

logger = logging.getLogger("zat.scene_observer")


class SceneObserver:
    # 场景观察者：每次操作前截图识别当前场景
    
    def __init__(self, adb: "ADBController", matcher: "ImageMatcher"):
        self.adb = adb
        self.matcher = matcher
        self._last_screen = None  # 缓存最近一次截图
    
    async def observe(self) -> str:
        # 截图并识别当前场景
        # Returns: 场景ID，无法识别时返回 "unknown"
        
        screen = await self.adb.screencap_array()
        self._last_screen = screen
        
        fingerprints = registry.get_all_fingerprints()
        
        best_match: Optional[str] = None
        best_confidence: float = 0.0
        
        for scene_id, fingerprint_path in fingerprints.items():
            # 指纹图片统一放在 fingerprint/ 目录下
            template_path = f"fingerprint/{fingerprint_path}"
            result = self.matcher.match_template(screen, template_path, threshold=0.7)
            if result:
                _, _, confidence = result
                logger.debug(f"匹配 {scene_id}: {confidence:.2f}")
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = scene_id
        
        if best_match:
            scene = registry.get(best_match)
            logger.info(f"识别到场景: {scene.name} (confidence: {best_confidence:.2f})")
            return best_match
        
        logger.warning("无法识别当前场景")
        return "unknown"
    
    def get_last_screen(self):
        # 获取最近一次截图（避免重复截图）
        return self._last_screen
    
    async def capture(self):
        # 仅截图，不识别
        self._last_screen = await self.adb.screencap_array()
        return self._last_screen
