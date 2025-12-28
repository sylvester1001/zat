# ADB 控制器
# 负责与 Android 设备通信

import asyncio
import logging
import shutil
from typing import Optional
import numpy as np
import cv2

from .scrcpy_capture import ScrcpyCapture, AsyncScrcpyCapture, ScrcpyError

logger = logging.getLogger("zat.adb")


class ADBError(Exception):
    # ADB 错误
    pass


class ADBController:
    # ADB 控制器
    # 支持 scrcpy 高速屏幕捕获和传统 adb screencap
    
    # 常见模拟器端口
    COMMON_PORTS = [
        5555,   # MuMu (默认端口), BlueStacks, 雷电
        16384,  # MuMu 12
        62001,  # 夜神
        21503,  # 逍遥
    ]
    
    # 推荐的分辨率（用于图像识别）
    # 仗剑传说是竖屏游戏，推荐 720x1280
    RECOMMENDED_RESOLUTION = (720, 1280)
    
    def __init__(
        self,
        adb_path: str = "adb",
        use_scrcpy: bool = True,
        scrcpy_path: Optional[str] = None,
        scrcpy_max_size: int = 1080,
        scrcpy_bit_rate: str = '8M',
        scrcpy_max_fps: int = 30,
    ):
        # 初始化 ADB 控制器
        # 
        # Args:
        #     adb_path: ADB 可执行文件路径
        #     use_scrcpy: 是否使用 scrcpy 进行屏幕捕获（推荐）
        #     scrcpy_path: scrcpy 可执行文件路径
        #     scrcpy_max_size: scrcpy 最大分辨率
        #     scrcpy_bit_rate: scrcpy 视频码率
        #     scrcpy_max_fps: scrcpy 最大帧率
        
        self.adb_path = adb_path
        self.device: Optional[str] = None
        self.screen_resolution: Optional[tuple[int, int]] = None
        
        # scrcpy 配置
        self.use_scrcpy = use_scrcpy
        self.scrcpy_path = scrcpy_path
        self.scrcpy_max_size = scrcpy_max_size
        self.scrcpy_bit_rate = scrcpy_bit_rate
        self.scrcpy_max_fps = scrcpy_max_fps
        
        # scrcpy 捕获器实例
        self._scrcpy_capture: Optional[ScrcpyCapture] = None
        self._async_scrcpy: Optional[AsyncScrcpyCapture] = None
        
        # 检查 ADB 是否可用
        if not shutil.which(self.adb_path):
            raise ADBError(f"未找到 ADB: {self.adb_path}")
        
        logger.info(f"ADB 控制器已初始化: {self.adb_path}, scrcpy模式: {use_scrcpy}")
    
    def is_connected(self) -> bool:
        # 检查是否已连接设备（仅检查本地状态）
        return self.device is not None
    
    # ==================== scrcpy 相关方法 ====================
    
    async def start_scrcpy(self):
        # 启动 scrcpy 屏幕捕获
        # 需要先连接设备
        if not self.is_connected():
            raise ADBError("设备未连接，无法启动 scrcpy")
        
        if not self.use_scrcpy:
            logger.warning("scrcpy 模式未启用")
            return
        
        if self._scrcpy_capture and self._scrcpy_capture.is_running:
            logger.warning("scrcpy 已在运行")
            return
        
        try:
            self._scrcpy_capture = ScrcpyCapture(
                device=self.device,
                max_size=self.scrcpy_max_size,
                bit_rate=self.scrcpy_bit_rate,
                max_fps=self.scrcpy_max_fps,
                scrcpy_path=self.scrcpy_path,
                adb_path=self.adb_path,
            )
            self._async_scrcpy = AsyncScrcpyCapture(self._scrcpy_capture)
            await self._async_scrcpy.start()
            logger.info("scrcpy 屏幕捕获已启动")
        except ScrcpyError as e:
            logger.error(f"启动 scrcpy 失败: {e}")
            self._scrcpy_capture = None
            self._async_scrcpy = None
            raise ADBError(f"启动 scrcpy 失败: {e}")
    
    async def stop_scrcpy(self):
        # 停止 scrcpy 屏幕捕获
        if self._async_scrcpy:
            await self._async_scrcpy.stop()
            self._scrcpy_capture = None
            self._async_scrcpy = None
            logger.info("scrcpy 屏幕捕获已停止")
    
    @property
    def scrcpy_running(self) -> bool:
        # 检查 scrcpy 是否正在运行
        return self._scrcpy_capture is not None and self._scrcpy_capture.is_running
    
    @property
    def scrcpy_fps(self) -> float:
        # 获取 scrcpy 当前帧率
        if self._scrcpy_capture:
            return self._scrcpy_capture.fps
        return 0.0
    
    # ==================== 屏幕捕获方法 ====================
    
    async def check_device_online(self) -> bool:
        # 实时检查设备是否在线
        # 
        # Returns:
        #     True 如果设备在线且可用，否则 False
        if not self.device:
            return False
        
        try:
            devices = await self.get_devices()
            if self.device in devices:
                return True
            else:
                # 设备离线，清除状态
                logger.warning(f"设备已离线: {self.device}")
                await self.stop_scrcpy()  # 停止 scrcpy
                self.device = None
                self.screen_resolution = None
                return False
        except Exception as e:
            logger.error(f"检查设备状态失败: {e}")
            return False
    
    async def _run_command(self, cmd: str) -> tuple[str, str, int]:
        # 执行 ADB 命令
        # 
        # Returns:
        #     (stdout, stderr, returncode)
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return (
            stdout.decode("utf-8", errors="ignore"),
            stderr.decode("utf-8", errors="ignore"),
            proc.returncode
        )
    
    async def get_devices(self) -> list[str]:
        # 获取已连接的设备列表
        cmd = f'"{self.adb_path}" devices'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"获取设备列表失败: {stderr}")
        
        devices = []
        for line in stdout.strip().split("\n")[1:]:  # 跳过第一行 "List of devices attached"
            if line.strip() and "\tdevice" in line:
                device = line.split("\t")[0]
                devices.append(device)
        
        return devices
    
    async def connect(self, device: str) -> bool:
        # 连接到指定设备
        # 
        # Args:
        #     device: 设备地址，如 "127.0.0.1:16384"
        
        # 如果是 IP:PORT 格式，先尝试 connect
        if ":" in device:
            cmd = f'"{self.adb_path}" connect {device}'
            stdout, stderr, code = await self._run_command(cmd)
            
            if code != 0:
                logger.error(f"连接失败: {stderr}")
                return False
            
            # 等待连接稳定
            await asyncio.sleep(1)
        
        # 验证设备是否可用
        devices = await self.get_devices()
        if device in devices:
            self.device = device
            logger.info(f"已连接设备: {device}")
            return True
        else:
            logger.error(f"设备不可用: {device}")
            return False
    
    async def auto_discover(self) -> Optional[str]:
        # 自动发现并连接设备
        # 
        # Returns:
        #     设备地址，如果未找到则返回 None
        logger.info("开始自动发现设备...")
        
        # 1. 先检查已连接的设备
        devices = await self.get_devices()
        if devices:
            device = devices[0]
            self.device = device
            logger.info(f"发现已连接设备: {device}")
            return device
        
        # 2. 尝试常见端口
        for port in self.COMMON_PORTS:
            device = f"127.0.0.1:{port}"
            logger.info(f"尝试连接: {device}")
            
            if await self.connect(device):
                return device
        
        logger.warning("未找到可用设备")
        return None
    
    async def screencap(self, gray: bool = False, quality: int = 65) -> bytes:
        # 截图并返回 JPEG 字节
        # 优先使用 scrcpy，fallback 到 adb screencap
        # 
        # Args:
        #     gray: 是否转换为灰度图
        #     quality: JPEG 质量 (1-100)
        # 
        # Returns:
        #     JPEG 图像字节
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        # 优先使用 scrcpy
        if self.use_scrcpy and self._async_scrcpy and self._scrcpy_capture.is_running:
            img = self._async_scrcpy.get_latest_frame()
            if img is not None:
                if gray:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
                _, buffer = cv2.imencode(".jpg", img, encode_param)
                return buffer.tobytes()
        
        # fallback 到 adb screencap
        return await self._screencap_adb(gray, quality)
    
    async def _screencap_adb(self, gray: bool = False, quality: int = 65) -> bytes:
        # 使用 adb screencap 截图（传统方式）
        cmd = f'"{self.adb_path}" -s {self.device} exec-out screencap -p'
        
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise ADBError(f"截图失败: {stderr.decode()}")
        
        # 解码 PNG
        nparr = np.frombuffer(stdout, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ADBError("解码截图失败")
        
        # 可选：转换为灰度图
        if gray:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 编码为 JPEG
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
        _, buffer = cv2.imencode(".jpg", img, encode_param)
        
        return buffer.tobytes()
    
    async def screencap_array(self) -> np.ndarray:
        # 截图并返回 numpy 数组（用于图像识别）
        # 优先使用 scrcpy，fallback 到 adb screencap
        # 
        # Returns:
        #     BGR 格式的 numpy 数组
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        # 优先使用 scrcpy
        if self.use_scrcpy and self._async_scrcpy and self._scrcpy_capture.is_running:
            img = self._async_scrcpy.get_latest_frame()
            if img is not None:
                return img
        
        # fallback 到 adb screencap
        return await self._screencap_array_adb()
    
    async def _screencap_array_adb(self) -> np.ndarray:
        # 使用 adb screencap 截图并返回数组（传统方式）
        cmd = f'"{self.adb_path}" -s {self.device} exec-out screencap -p'
        
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise ADBError(f"截图失败: {stderr.decode()}")
        
        nparr = np.frombuffer(stdout, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ADBError("解码截图失败")
        
        return img
    
    async def tap(self, x: int, y: int):
        # 点击屏幕
        # 
        # Args:
        #     x: X 坐标
        #     y: Y 坐标
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        cmd = f'"{self.adb_path}" -s {self.device} shell input tap {x} {y}'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"点击失败: {stderr}")
        
        logger.debug(f"点击: ({x}, {y})")
    
    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        # 滑动屏幕
        # 
        # Args:
        #     x1, y1: 起始坐标
        #     x2, y2: 结束坐标
        #     duration: 持续时间（毫秒）
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        cmd = f'"{self.adb_path}" -s {self.device} shell input swipe {x1} {y1} {x2} {y2} {duration}'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"滑动失败: {stderr}")
        
        logger.debug(f"滑动: ({x1}, {y1}) -> ({x2}, {y2})")
    
    async def get_screen_resolution(self) -> tuple[int, int]:
        # 获取屏幕分辨率
        # 
        # Returns:
        #     (width, height)
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        cmd = f'"{self.adb_path}" -s {self.device} shell wm size'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"获取分辨率失败: {stderr}")
        
        # 解析输出: "Physical size: 1280x720"
        for line in stdout.strip().split("\n"):
            if ":" in line:
                size_str = line.split(":")[-1].strip()
                if "x" in size_str:
                    width, height = map(int, size_str.split("x"))
                    self.screen_resolution = (width, height)
                    logger.info(f"屏幕分辨率: {width}x{height}")
                    
                    # 检查是否为推荐分辨率
                    if (width, height) != self.RECOMMENDED_RESOLUTION:
                        logger.warning(
                            f"当前分辨率 {width}x{height} 与推荐分辨率 "
                            f"{self.RECOMMENDED_RESOLUTION[0]}x{self.RECOMMENDED_RESOLUTION[1]} 不匹配，"
                            f"可能影响图像识别准确性"
                        )
                    
                    return (width, height)
        
        raise ADBError("无法解析分辨率")
    
    async def start_app(self, package: str, activity: str = None):
        # 启动应用
        # 
        # Args:
        #     package: 包名
        #     activity: Activity 名称（可选）
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        if activity:
            target = f"{package}/{activity}"
        else:
            # 使用 monkey 启动（不需要知道 activity）
            cmd = f'"{self.adb_path}" -s {self.device} shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
            stdout, stderr, code = await self._run_command(cmd)
            
            if code != 0:
                raise ADBError(f"启动应用失败: {stderr}")
            
            logger.info(f"已启动应用: {package}")
            return
        
        cmd = f'"{self.adb_path}" -s {self.device} shell am start -n {target}'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"启动应用失败: {stderr}")
        
        logger.info(f"已启动应用: {target}")
    
    async def stop_app(self, package: str):
        # 停止应用
        # 
        # Args:
        #     package: 包名
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        cmd = f'"{self.adb_path}" -s {self.device} shell am force-stop {package}'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"停止应用失败: {stderr}")
        
        logger.info(f"已停止应用: {package}")
    
    async def is_app_running(self, package: str) -> bool:
        # 检查应用是否正在运行
        # 
        # Args:
        #     package: 包名
        # 
        # Returns:
        #     True 如果应用正在运行
        if not self.is_connected():
            return False
        
        cmd = f'"{self.adb_path}" -s {self.device} shell pidof {package}'
        stdout, stderr, code = await self._run_command(cmd)
        
        # pidof 返回 PID 表示运行中，空表示未运行
        return bool(stdout.strip())
    
    async def disconnect(self):
        # 断开设备连接并清理资源
        await self.stop_scrcpy()
        self.device = None
        self.screen_resolution = None
        logger.info("已断开设备连接")
