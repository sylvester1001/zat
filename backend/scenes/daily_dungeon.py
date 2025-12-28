# L1-L2: 日常副本场景定义
# dungeon_list + 各副本详情页

from core.scene_registry import registry, Scene, Transition, ActionType


# 日常副本列表
registry.register(Scene(
    id="dungeon_list",
    name="日常副本列表",
    fingerprint="dungeon_list",
    transitions={
        "dungeon:sea_palace": Transition(
            target="dungeon:sea_palace",
            action=ActionType.CLICK,
            template="daily_dungeon/sea_palace",
            wait_after=0.8
        ),
        "dungeon:mizumoto_shrine": Transition(
            target="dungeon:mizumoto_shrine",
            action=ActionType.CLICK,
            template="daily_dungeon/mizumoto_shirine",
            wait_after=0.8
        ),
        "dungeon:world_tree": Transition(
            target="dungeon:world_tree",
            action=ActionType.CLICK,
            template="daily_dungeon/world_tree",
            scroll="down",
            scroll_distance=500,
            wait_after=0.8
        ),
        "dungeon:mount_mechagod": Transition(
            target="dungeon:mount_mechagod",
            action=ActionType.CLICK,
            template="daily_dungeon/mount_mechagod",
            scroll="down",
            scroll_distance=500,
            wait_after=0.8
        ),
        "dungeon:huangquan_pavilion": Transition(
            target="dungeon:huangquan_pavilion",
            action=ActionType.CLICK,
            template="daily_dungeon/huangquan_pavilion",
            scroll="down",
            scroll_distance=500,
            wait_after=0.8
        ),
    },
    back_to="note",
    back_template="back",
))


# 副本详情页定义
DUNGEONS = [
    ("sea_palace", "海之宫遗迹"),
    ("mizumoto_shrine", "源水大社"),
    ("world_tree", "世界之树"),
    ("mount_mechagod", "机神山"),
    ("huangquan_pavilion", "黄泉楼"),
]

for dungeon_id, dungeon_name in DUNGEONS:
    # 指纹文件名处理（mizumoto_shrine 的指纹文件拼写是 mizumoto_shirine）
    fingerprint_name = "mizumoto_shirine" if dungeon_id == "mizumoto_shrine" else dungeon_id
    
    registry.register(Scene(
        id=f"dungeon:{dungeon_id}",
        name=dungeon_name,
        fingerprint=fingerprint_name,
        transitions={
            # 副本详情页之间不能直接跳转，只能返回列表
        },
        back_to="dungeon_list",
        back_template="back",
    ))
