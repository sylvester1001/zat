# 导航系统测试脚本
# 用于测试场景识别和导航功能

import asyncio
import logging
import sys

# 配置日志 - 显示 DEBUG 级别以查看详细信息
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)

# 导入模块
from core.adb_controller import ADBController
from core.image_matcher import image_matcher
from core.navigator import Navigator
from core.scene_registry import registry

# 导入场景定义（触发注册）
import scenes


async def test_observe():
    # 测试场景识别
    print("\n" + "=" * 50)
    print("测试场景识别")
    print("=" * 50)
    
    adb = ADBController()
    device = await adb.auto_discover()
    if not device:
        print("未找到设备")
        return
    
    print(f"已连接: {device}")
    await adb.start_capture()
    await asyncio.sleep(1)
    
    navigator = Navigator(adb, image_matcher)
    
    # 识别当前场景
    current = await navigator.observer.observe()
    print(f"\n当前场景: {current}")
    
    if current != "unknown":
        scene = registry.get(current)
        print(f"场景名称: {scene.name}")
        print(f"可跳转到: {list(scene.transitions.keys())}")
        if scene.back_to:
            print(f"返回到: {scene.back_to}")
    
    await adb.stop_capture()


async def test_navigate(target: str):
    # 测试导航到指定场景
    print("\n" + "=" * 50)
    print(f"测试导航到: {target}")
    print("=" * 50)
    
    adb = ADBController()
    device = await adb.auto_discover()
    if not device:
        print("未找到设备")
        return
    
    print(f"已连接: {device}")
    await adb.start_capture()
    await asyncio.sleep(1)
    
    navigator = Navigator(adb, image_matcher)
    
    # 先识别当前位置
    current = await navigator.observer.observe()
    print(f"当前位置: {current}")
    
    # 计算路径
    path = navigator.find_path(current, target)
    if path:
        print(f"规划路径: {' -> '.join(path)}")
    else:
        print("无法找到路径")
        await adb.stop_capture()
        return
    
    # 执行导航
    print("\n开始导航...")
    success = await navigator.navigate_to(target)
    
    if success:
        print(f"\n✓ 成功到达: {target}")
    else:
        print(f"\n✗ 导航失败")
    
    await adb.stop_capture()


async def list_scenes():
    # 列出所有已注册的场景
    print("\n" + "=" * 50)
    print("已注册的场景")
    print("=" * 50)
    
    for scene_id, scene in registry.get_all().items():
        print(f"\n[{scene_id}] {scene.name}")
        print(f"  指纹: {scene.fingerprint}")
        if scene.transitions:
            print(f"  跳转: {list(scene.transitions.keys())}")
        if scene.back_to:
            print(f"  返回: {scene.back_to}")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python test_navigation.py list          # 列出所有场景")
        print("  python test_navigation.py observe       # 识别当前场景")
        print("  python test_navigation.py navigate <场景ID>  # 导航到指定场景")
        print("")
        print("场景ID示例: home, note, dungeon_list, dungeon:sea_palace, daily_activity_list, sacred_trial")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        asyncio.run(list_scenes())
    elif cmd == "observe":
        asyncio.run(test_observe())
    elif cmd == "navigate":
        if len(sys.argv) < 3:
            print("请指定目标场景ID")
            return
        target = sys.argv[2]
        asyncio.run(test_navigate(target))
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
