# 场景图导航系统
# 使用图结构管理游戏场景，支持自动寻路

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable, Any
from enum import Enum

logger = logging.getLogger("zat.scene")


# ==================== 全局配置 ====================

# 操作后默认等待时间（秒）
# 流式捕获下通常不需要等待，设为 0
# 如果遇到点击太快的问题，可以适当增加
DEFAULT_WAIT_AFTER = 0.0

# 模板匹配检测间隔（秒）
MATCH_INTERVAL = 0.05


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
    wait_after: Optional[float] = None   # 操作后等待时间，None 使用全局默认值


@dataclass
class Scene:
    # 场景定义
    id: str                              # 场景ID
    name: str                            # 场景名称（用于日志）
    detect_templates: list[str] = field(default_factory=list)  # 用于识别该场景的模板
    detect_texts: list[str] = field(default_factory=list)      # 用于识别该场景的文字
    transitions: dict[str, Transition] = field(default_factory=dict)  # 可转移到的场景
    back_to: Optional[str] = None        # 返回操作会到达的场景
    back_template: Optional[str] = None  # 返回按钮模板


# ==================== 场景定义 ====================

SCENES: dict[str, Scene] = {}


def register_scene(scene: Scene):
    # 注册场景
    SCENES[scene.id] = scene
    logger.debug(f"注册场景: {scene.id} ({scene.name})")


def define_scenes():
    # 定义所有场景
    
    # 主界面
    register_scene(Scene(
        id="home",
        name="主界面",
        detect_templates=["home_selected"],
        transitions={
            "note": Transition(target="note", action=ActionType.CLICK, template="note"),
            "character": Transition(target="character", action=ActionType.CLICK, template="character"),
            "guild": Transition(target="guild", action=ActionType.CLICK, template="guild"),
            "world": Transition(target="world", action=ActionType.CLICK, template="world"),
        },
        back_to=None,
    ))
    
    # 笔记页面
    register_scene(Scene(
        id="note",
        name="笔记",
        detect_templates=["note_selected"],
        transitions={
            "dungeon_list": Transition(target="dungeon_list", action=ActionType.CLICK, template="daily_dungeon/daily_dungeon"),
            "home": Transition(target="home", action=ActionType.CLICK, template="home"),
        },
        back_to="home",
        back_template="home",
    ))
    
    # 角色页面
    register_scene(Scene(
        id="character",
        name="角色",
        detect_templates=["character_selected"],
        transitions={
            "home": Transition(target="home", action=ActionType.CLICK, template="home"),
        },
        back_to="home",
        back_template="home",
    ))
    
    # 公会页面
    register_scene(Scene(
        id="guild",
        name="公会",
        detect_templates=["guild_selected"],
        transitions={
            "home": Transition(target="home", action=ActionType.CLICK, template="home"),
        },
        back_to="home",
        back_template="home",
    ))
    
    # 世界页面
    register_scene(Scene(
        id="world",
        name="世界",
        detect_templates=["world_selected"],
        transitions={
            "home": Transition(target="home", action=ActionType.CLICK, template="home"),
        },
        back_to="home",
        back_template="home",
    ))
    
    # 日常副本列表
    register_scene(Scene(
        id="dungeon_list",
        name="日常副本列表",
        detect_templates=[
            "daily_dungeon/sea_palace",
            "daily_dungeon/mizumoto_shrine",
        ],
        detect_texts=["日常副本"],
        transitions={
            "dungeon:world_tree": Transition(
                target="dungeon:world_tree",
                action=ActionType.CLICK,
                template="daily_dungeon/world_tree",
                scroll="down",
                scroll_distance=500,
            ),
            "dungeon:mount_mechagod": Transition(
                target="dungeon:mount_mechagod",
                action=ActionType.CLICK,
                template="daily_dungeon/mount_mechagod",
                scroll="down",
                scroll_distance=500,
            ),
            "dungeon:sea_palace": Transition(
                target="dungeon:sea_palace",
                action=ActionType.CLICK,
                template="daily_dungeon/sea_palace",
            ),
            "dungeon:mizumoto_shrine": Transition(
                target="dungeon:mizumoto_shrine",
                action=ActionType.CLICK,
                template="daily_dungeon/mizumoto_shrine",
            ),
            "note": Transition(target="note", action=ActionType.CLICK, template="back"),
        },
        back_to="note",
        back_template="back",
    ))
    
    # 各个副本详情页
    for dungeon_id, dungeon_name in [
        ("world_tree", "世界之树"),
        ("mount_mechagod", "机神山"),
        ("sea_palace", "海之宫遗迹"),
        ("mizumoto_shrine", "源水大社"),
    ]:
        register_scene(Scene(
            id=f"dungeon:{dungeon_id}",
            name=dungeon_name,
            detect_templates=[f"daily_dungeon/{dungeon_id}"],
            transitions={
                "dungeon_list": Transition(target="dungeon_list", action=ActionType.CLICK, template="back"),
            },
            back_to="dungeon_list",
            back_template="back",
        ))


# 初始化场景
define_scenes()


# ==================== 场景图导航器 ====================

class SceneNavigator:
    # 场景图导航器
    
    def __init__(self):
        self.current_scene: Optional[str] = None
        self._action_handler: Optional[Callable] = None
    
    def set_action_handler(self, handler: Callable[[Transition, Scene], Awaitable[bool]]):
        # 设置操作处理器
        # handler 签名: async def handler(transition: Transition, from_scene: Scene) -> bool
        # 返回 True 表示操作成功
        self._action_handler = handler
    
    def find_path(self, from_scene: str, to_scene: str) -> Optional[list[str]]:
        # 使用 BFS 寻找从 from_scene 到 to_scene 的最短路径
        # 
        # Returns:
        #     场景ID列表（包含起点和终点），如果无法到达返回 None
        if from_scene == to_scene:
            return [from_scene]
        
        if from_scene not in SCENES or to_scene not in SCENES:
            return None
        
        # BFS
        queue = deque([(from_scene, [from_scene])])
        visited = {from_scene}
        
        while queue:
            current, path = queue.popleft()
            scene = SCENES.get(current)
            
            if not scene:
                continue
            
            # 检查所有可转移的场景
            for target_id in scene.transitions.keys():
                if target_id == to_scene:
                    return path + [target_id]
                
                if target_id not in visited and target_id in SCENES:
                    visited.add(target_id)
                    queue.append((target_id, path + [target_id]))
            
            # 也考虑返回操作
            if scene.back_to and scene.back_to not in visited:
                if scene.back_to == to_scene:
                    return path + [scene.back_to]
                visited.add(scene.back_to)
                queue.append((scene.back_to, path + [scene.back_to]))
        
        return None
    
    async def navigate_to(self, target_scene: str) -> bool:
        # 导航到目标场景
        # 
        # Args:
        #     target_scene: 目标场景ID
        # 
        # Returns:
        #     成功返回 True
        if not self._action_handler:
            logger.error("未设置操作处理器")
            return False
        
        if self.current_scene is None:
            logger.error("当前场景未知，请先调用 detect_current_scene()")
            return False
        
        if self.current_scene == target_scene:
            logger.info(f"已在目标场景: {target_scene}")
            return True
        
        # 寻找路径
        path = self.find_path(self.current_scene, target_scene)
        if not path:
            logger.error(f"无法找到从 {self.current_scene} 到 {target_scene} 的路径")
            return False
        
        logger.info(f"导航路径: {' -> '.join(path)}")
        
        # 执行路径上的每一步
        for i in range(len(path) - 1):
            from_id = path[i]
            to_id = path[i + 1]
            
            from_scene = SCENES.get(from_id)
            if not from_scene:
                logger.error(f"场景不存在: {from_id}")
                return False
            
            # 查找转移
            transition = from_scene.transitions.get(to_id)
            
            # 如果没有直接转移，检查是否是返回操作
            if not transition and from_scene.back_to == to_id:
                transition = Transition(
                    target=to_id,
                    action=ActionType.BACK,
                    template=from_scene.back_template,
                )
            
            if not transition:
                logger.error(f"无法从 {from_id} 转移到 {to_id}")
                return False
            
            # 执行操作
            logger.info(f"执行: {from_scene.name} -> {SCENES[to_id].name}")
            success = await self._action_handler(transition, from_scene)
            
            if not success:
                logger.error(f"操作失败: {from_id} -> {to_id}")
                self.current_scene = None  # 标记为未知状态
                return False
            
            # 更新当前场景
            self.current_scene = to_id
        
        logger.info(f"成功导航到: {SCENES[target_scene].name}")
        return True
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        # 获取场景定义
        return SCENES.get(scene_id)
    
    def get_all_scenes(self) -> dict[str, Scene]:
        # 获取所有场景
        return SCENES.copy()


# 全局导航器实例
scene_navigator = SceneNavigator()
