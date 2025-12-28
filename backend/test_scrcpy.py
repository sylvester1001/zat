# scrcpy 捕获测试脚本

import asyncio
import time
import logging

# 开启调试日志
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(message)s')

from core.adb_controller import ADBController


async def main():
    print("=== scrcpy 捕获测试 ===\n")
    
    # 初始化
    adb = ADBController(use_scrcpy=True)
    
    # 连接设备
    device = await adb.auto_discover()
    if not device:
        print("❌ 未找到设备，请确保模拟器已启动")
        return
    
    print(f"✅ 已连接: {device}\n")
    
    # 启动 scrcpy
    print("启动 scrcpy...")
    try:
        await adb.start_scrcpy()
    except Exception as e:
        print(f"❌ 启动 scrcpy 失败: {e}")
        return
    
    # 检查 scrcpy 进程状态
    if adb._scrcpy_capture._proc:
        poll = adb._scrcpy_capture._proc.poll()
        print(f"scrcpy 进程状态: {'运行中' if poll is None else f'已退出({poll})'}")
        
        if poll is not None:
            # 进程已退出，读取错误信息
            stderr = adb._scrcpy_capture._proc.stderr.read()
            if stderr:
                print(f"scrcpy 错误输出:\n{stderr.decode()}")
    
    # 等待视频流稳定
    print("等待视频流...")
    for i in range(50):  # 最多等 5 秒
        await asyncio.sleep(0.1)
        frame = adb._scrcpy_capture.get_latest_frame()
        if frame is not None:
            print(f"✅ 第 {i*100}ms 获取到帧")
            break
        if i % 10 == 0:
            print(f"  等待中... {i*100}ms, 帧数: {adb._scrcpy_capture.frame_count}")
    
    if adb._scrcpy_capture.get_latest_frame() is None:
        print("❌ scrcpy 未能获取到帧")
        
        # 再次检查进程
        if adb._scrcpy_capture._proc:
            poll = adb._scrcpy_capture._proc.poll()
            if poll is not None:
                stderr = adb._scrcpy_capture._proc.stderr.read()
                print(f"scrcpy 已退出，错误:\n{stderr.decode() if stderr else '无'}")
        
        await adb.stop_scrcpy()
        return
    
    print(f"✅ scrcpy 已就绪，当前帧率: {adb.scrcpy_fps:.1f} fps\n")
    
    # 测试 scrcpy 获取帧速度
    print("--- scrcpy 缓存帧读取测试 ---")
    times_cache = []
    for i in range(10):
        start = time.perf_counter()
        frame = adb._scrcpy_capture.get_latest_frame()
        elapsed = (time.perf_counter() - start) * 1000
        times_cache.append(elapsed)
        if frame is not None:
            print(f"帧 {i+1}: {frame.shape[1]}x{frame.shape[0]}, 耗时: {elapsed:.3f}ms")
        await asyncio.sleep(0.033)
    
    avg_cache = sum(times_cache) / len(times_cache)
    print(f"\nscrcpy 缓存读取平均延迟: {avg_cache:.3f}ms")
    print(f"scrcpy 解码帧率: {adb.scrcpy_fps:.1f} fps")
    
    # 对比 adb screencap
    print("\n--- 对比 adb screencap ---")
    times_adb = []
    for i in range(5):
        start = time.perf_counter()
        frame = await adb._screencap_array_adb()
        elapsed = (time.perf_counter() - start) * 1000
        times_adb.append(elapsed)
        print(f"adb 截图 {i+1}: 耗时: {elapsed:.1f}ms")
    
    avg_adb = sum(times_adb) / len(times_adb)
    print(f"\nadb screencap 平均延迟: {avg_adb:.1f}ms")
    
    if avg_cache > 0:
        print(f"scrcpy 缓存读取快了: {avg_adb / avg_cache:.0f}x")
    
    await adb.stop_scrcpy()
    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(main())
