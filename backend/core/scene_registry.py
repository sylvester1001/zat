# 场景注册中心
# 只负责场景数据的存储和查询，不包含导航逻辑

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger("zat.scene_registry")


class ActionType(str, Enum):
    # 操作类型
    CLICK = "click"           # 点击模板
    CLICK_TEXT = "click_text" # 点击文字（OCR）
    BACK = "back"             # 返回操作
    SWIPE = "swipe"           # 滑动


@dataclass
class Transition:
    # 场景转移定义
    target: str                          # 目标场景ID
    action: ActionType                   # 操作类型
    template: Optional[str] = None       # 模板名称（用于 CLICK）
    text: Optional[str] = None           # 文字（用于 CLICK_TEXT）
    scroll: Optional[str] = None         # 滑动方向: "up", "down"
    scroll_distance: int = 500           # 滑动距离
    wait_after: float = 0.5              # 操作后等待时间


@dataclass
class Scene:
    # 场景定义
    id: str                              # 场景ID
    name: str                            # 场景名称（用于日志）
    fingerprint: Optional[str] = None    # 指纹图片路径（用于识别该场景）
    detect_texts: list[str] = field(default_factory=list)  # 备用：用于识别该场景的文字
    transitions: dict[str, Transition] = field(default_factory=dict)  # 可转移到的场景
    back_to: Optional[str] = None        # 返回操作会到达的场景
    back_template: str = "back"          # 返回按钮模板


class SceneRegistry:
    # 场景注册中心（单例）
    
    _instance: Optional["SceneRegistry"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._scenes = {}
        return cls._instance
    
    def register(self, scene: Scene):
        # 注册场景
        self._scenes[scene.id] = scene
        logger.debug(f"注册场景: {scene.id} ({scene.name})")
    
    def get(self, scene_id: str) -> Optional[Scene]:
        # 获取场景
        return self._scenes.get(scene_id)
    
    def get_all(self) -> dict[str, Scene]:
        # 获取所有场景
        return self._scenes.copy()
    
    def get_all_fingerprints(self) -> dict[str, str]:
        # 获取所有场景的指纹映射 {scene_id: fingerprint_path}
        return {
            scene_id: scene.fingerprint
            for scene_id, scene in self._scenes.items()
            if scene.fingerprint
        }
    
    def clear(self):
        # 清空所有场景（用于测试）
        self._scenes.clear()


# 全局注册中心实例
registry = SceneRegistry()
