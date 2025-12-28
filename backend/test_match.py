# 模板匹配调试脚本

import asyncio
import cv2
from core.adb_controller import ADBController
from core.image_matcher import image_matcher


async def main():
    print("=== 模板匹配调试 ===\n")
    
    adb = ADBController()
    device = await adb.auto_discover()
    if not device:
        print("❌ 未找到设备")
        return
    
    print(f"✅ 已连接: {device}")
    
    # 启动屏幕捕获
    await adb.start_capture()
    await asyncio.sleep(1.5)  # 等待稳定
    
    # 获取帧
    frame = await adb.screencap_array()
    print(f"帧尺寸: {frame.shape[1]}x{frame.shape[0]}")
    
    # 保存当前帧用于调试
    cv2.imwrite("debug_frame.png", frame)
    print("已保存 debug_frame.png")
    
    # 测试模板匹配
    templates_to_test = [
        "daily_dungeon/daily_dungeon",
        "daily_dungeon/goto_daily_dungeon", 
        "note",
        "note_selected",
        "home",
        "home_selected",
    ]
    
    print("\n--- 模板匹配测试 ---")
    for template_name in templates_to_test:
        result = image_matcher.match_template(frame, template_name, threshold=0.7)
        if result:
            x, y, conf = result
            print(f"✅ {template_name}: 位置({x}, {y}), 置信度: {conf:.3f}")
        else:
            print(f"❌ {template_name}: 未匹配")
            # 检查模板是否存在
            if template_name in image_matcher.templates:
                t = image_matcher.templates[template_name]
                print(f"   模板尺寸: {t.shape[1]}x{t.shape[0]}")
            else:
                print(f"   模板不存在!")
    
    await adb.stop_capture()
    print("\n✅ 完成")


if __name__ == "__main__":
    asyncio.run(main())
