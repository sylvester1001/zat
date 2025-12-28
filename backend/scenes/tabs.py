# L0: 底部 Tab 场景定义
# home, note, character, guild, world

from core.scene_registry import registry, Scene, Transition, ActionType


# 主界面
registry.register(Scene(
    id="home",
    name="主界面",
    fingerprint="home",
    transitions={
        "note": Transition(
            target="note",
            action=ActionType.CLICK,
            template="note",
            wait_after=0.5
        ),
        "character": Transition(
            target="character",
            action=ActionType.CLICK,
            template="character",
            wait_after=0.5
        ),
        "guild": Transition(
            target="guild",
            action=ActionType.CLICK,
            template="guild",
            wait_after=0.5
        ),
        "world": Transition(
            target="world",
            action=ActionType.CLICK,
            template="world",
            wait_after=0.5
        ),
    },
    back_to=None,
))

# 笔记
registry.register(Scene(
    id="note",
    name="笔记",
    fingerprint="note",
    transitions={
        "home": Transition(
            target="home",
            action=ActionType.CLICK,
            template="home",
            wait_after=0.5
        ),
        "character": Transition(
            target="character",
            action=ActionType.CLICK,
            template="character",
            wait_after=0.5
        ),
        "guild": Transition(
            target="guild",
            action=ActionType.CLICK,
            template="guild",
            wait_after=0.5
        ),
        "world": Transition(
            target="world",
            action=ActionType.CLICK,
            template="world",
            wait_after=0.5
        ),
        "dungeon_list": Transition(
            target="dungeon_list",
            action=ActionType.CLICK,
            template="daily_dungeon/daily_dungeon",
            wait_after=0.5
        ),
        "daily_activity_list": Transition(
            target="daily_activity_list",
            action=ActionType.CLICK,
            template="daily_activity",
            wait_after=0.5
        ),
    },
    back_to=None,
))

# 角色
registry.register(Scene(
    id="character",
    name="角色",
    fingerprint="character",
    transitions={
        "home": Transition(
            target="home",
            action=ActionType.CLICK,
            template="home",
            wait_after=0.5
        ),
        "note": Transition(
            target="note",
            action=ActionType.CLICK,
            template="note",
            wait_after=0.5
        ),
        "guild": Transition(
            target="guild",
            action=ActionType.CLICK,
            template="guild",
            wait_after=0.5
        ),
        "world": Transition(
            target="world",
            action=ActionType.CLICK,
            template="world",
            wait_after=0.5
        ),
    },
    back_to=None,
))

# 公会
registry.register(Scene(
    id="guild",
    name="公会",
    fingerprint="guild",
    transitions={
        "home": Transition(
            target="home",
            action=ActionType.CLICK,
            template="home",
            wait_after=0.5
        ),
        "note": Transition(
            target="note",
            action=ActionType.CLICK,
            template="note",
            wait_after=0.5
        ),
        "character": Transition(
            target="character",
            action=ActionType.CLICK,
            template="character",
            wait_after=0.5
        ),
        "world": Transition(
            target="world",
            action=ActionType.CLICK,
            template="world",
            wait_after=0.5
        ),
    },
    back_to=None,
))

# 世界
registry.register(Scene(
    id="world",
    name="世界",
    fingerprint="world",
    transitions={
        "home": Transition(
            target="home",
            action=ActionType.CLICK,
            template="home",
            wait_after=0.5
        ),
        "note": Transition(
            target="note",
            action=ActionType.CLICK,
            template="note",
            wait_after=0.5
        ),
        "character": Transition(
            target="character",
            action=ActionType.CLICK,
            template="character",
            wait_after=0.5
        ),
        "guild": Transition(
            target="guild",
            action=ActionType.CLICK,
            template="guild",
            wait_after=0.5
        ),
    },
    back_to=None,
))
