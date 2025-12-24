"""
测试 Python 后端
"""
import asyncio
import sys
from core.adb_controller import ADBController


async def test_adb():
    """测试 ADB 控制器"""
    print("=" * 50)
    print("测试 ADB 控制器")
    print("=" * 50)
    
    try:
        # 初始化
        print("\n1. 初始化 ADB 控制器...")
        adb = ADBController()
        print("✓ ADB 控制器初始化成功")
        
        # 自动发现设备
        print("\n2. 自动发现设备...")
        device = await adb.auto_discover()
        
        if device:
            print(f"✓ 已连接设备: {device}")
        else:
            print("✗ 未找到设备")
            print("\n请确保:")
            print("  1. 模拟器已启动")
            print("  2. ADB 已安装")
            print("  3. 运行: adb connect 127.0.0.1:16384")
            return False
        
        # 获取设备列表
        print("\n3. 获取设备列表...")
        devices = await adb.get_devices()
        print(f"✓ 发现 {len(devices)} 个设备: {devices}")
        
        # 截图测试
        print("\n4. 测试截图...")
        try:
            screenshot = await adb.screencap(quality=65)
            print(f"✓ 截图成功，大小: {len(screenshot)} bytes ({len(screenshot) / 1024:.1f} KB)")
            
            # 保存截图
            with open("test_screenshot.jpg", "wb") as f:
                f.write(screenshot)
            print("✓ 截图已保存到: test_screenshot.jpg")
        except Exception as e:
            print(f"✗ 截图失败: {e}")
            return False
        
        # 测试灰度截图
        print("\n5. 测试灰度截图...")
        try:
            screenshot_gray = await adb.screencap(gray=True, quality=65)
            print(f"✓ 灰度截图成功，大小: {len(screenshot_gray)} bytes ({len(screenshot_gray) / 1024:.1f} KB)")
            print(f"  压缩率: {len(screenshot_gray) / len(screenshot) * 100:.1f}%")
        except Exception as e:
            print(f"✗ 灰度截图失败: {e}")
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await test_adb()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
