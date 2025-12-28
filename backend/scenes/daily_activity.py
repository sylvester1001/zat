# L1-L2: 每日活动场景定义
# daily_activity_list + 圣兽试炼等

from core.scene_registry import registry, Scene, Transition, ActionType


# 每日活动列表
registry.register(Scene(
    id="daily_activity_list",
    name="每日活动列表",
    fingerprint="daily_activity_list",
    transitions={
        "sacred_trial": Transition(
            target="sacred_trial",
            action=ActionType.CLICK,
            template="sacred_trial",
            wait_after=1.0
        ),
        # 未来可以在这里添加更多活动入口
    },
    back_to="note",
    back_template="back",
))


# 圣兽试炼
registry.register(Scene(
    id="sacred_trial",
    name="圣兽试炼",
    fingerprint="sacred_trial",
    transitions={
        # 圣兽试炼内部的跳转（后续添加）
    },
    back_to="daily_activity_list",
    back_template="back",
))
