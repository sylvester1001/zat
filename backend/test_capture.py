# 屏幕捕获测试脚本

import asyncio
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')

from core.adb_controller import ADBController


async def main():
    print("=== 屏幕捕获测试 ===\n")
    
    # 初始化
    adb = ADBController()
    
    # 连接设备
    device = await adb.auto_discover()
    if not device:
        print("❌ 未找到设备，请确保模拟器已启动")
        return
    
    print(f"✅ 已连接: {device}\n")
    
    # 启动屏幕捕获
    print("启动屏幕捕获...")
    try:
        await adb.start_capture()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return
    
    # 等待视频流稳定
    print("等待视频流...")
    for i in range(30):
        await asyncio.sleep(0.1)
        if adb._capture.get_latest_frame() is not None:
            print(f"✅ 第 {(i+1)*100}ms 获取到帧")
            break
    
    await asyncio.sleep(0.5)
    
    if adb._capture.get_latest_frame() is None:
        print("❌ 未能获取到帧")
        await adb.stop_capture()
        return
    
    print(f"✅ 已就绪，当前帧率: {adb.capture_fps:.1f} fps\n")
    
    # 测试获取帧速度
    print("--- 帧读取测试 ---")
    times = []
    for i in range(10):
        start = time.perf_counter()
        frame = await adb.screencap_array()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"帧 {i+1}: {frame.shape[1]}x{frame.shape[0]}, 耗时: {elapsed:.3f}ms")
        await asyncio.sleep(0.033)
    
    avg = sum(times) / len(times)
    print(f"\n平均延迟: {avg:.3f}ms")
    print(f"解码帧率: {adb.capture_fps:.1f} fps")
    
    await adb.stop_capture()
    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(main())
