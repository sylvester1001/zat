"""
ADB 控制器
负责与 Android 设备通信
"""
import asyncio
import logging
import shutil
from typing import Optional
import numpy as np
import cv2

logger = logging.getLogger("zat.adb")


class ADBError(Exception):
    """ADB 错误"""
    pass


class ADBController:
    """ADB 控制器"""
    
    # 常见模拟器端口
    COMMON_PORTS = [
        16384,  # MuMu 12
        5555,   # BlueStacks, 雷电
        62001,  # 夜神
        21503,  # 逍遥
    ]
    
    def __init__(self, adb_path: str = "adb"):
        """
        初始化 ADB 控制器
        
        Args:
            adb_path: ADB 可执行文件路径，默认 "adb"（从 PATH 查找）
        """
        self.adb_path = adb_path
        self.device: Optional[str] = None
        
        # 检查 ADB 是否可用
        if not shutil.which(self.adb_path):
            raise ADBError(f"未找到 ADB: {self.adb_path}")
        
        logger.info(f"ADB 控制器已初始化: {self.adb_path}")
    
    def is_connected(self) -> bool:
        """检查是否已连接设备"""
        return self.device is not None
    
    async def _run_command(self, cmd: str) -> tuple[str, str, int]:
        """
        执行 ADB 命令
        
        Returns:
            (stdout, stderr, returncode)
        """
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
        """获取已连接的设备列表"""
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
        """
        连接到指定设备
        
        Args:
            device: 设备地址，如 "127.0.0.1:16384"
        """
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
        """
        自动发现并连接设备
        
        Returns:
            设备地址，如果未找到则返回 None
        """
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
        """
        截图（使用 exec-out，最快）
        
        Args:
            gray: 是否转换为灰度图
            quality: JPEG 质量 (1-100)
        
        Returns:
            JPEG 图像字节
        """
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        # 使用 exec-out 直接输出到 stdout
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
        """
        截图并返回 numpy 数组（用于图像识别）
        
        Returns:
            BGR 格式的 numpy 数组
        """
        if not self.is_connected():
            raise ADBError("设备未连接")
        
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
        """
        点击屏幕
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        cmd = f'"{self.adb_path}" -s {self.device} shell input tap {x} {y}'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"点击失败: {stderr}")
        
        logger.debug(f"点击: ({x}, {y})")
    
    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        """
        滑动屏幕
        
        Args:
            x1, y1: 起始坐标
            x2, y2: 结束坐标
            duration: 持续时间（毫秒）
        """
        if not self.is_connected():
            raise ADBError("设备未连接")
        
        cmd = f'"{self.adb_path}" -s {self.device} shell input swipe {x1} {y1} {x2} {y2} {duration}'
        stdout, stderr, code = await self._run_command(cmd)
        
        if code != 0:
            raise ADBError(f"滑动失败: {stderr}")
        
        logger.debug(f"滑动: ({x1}, {y1}) -> ({x2}, {y2})")
    
    async def start_app(self, package: str, activity: str = None):
        """
        启动应用
        
        Args:
            package: 包名
            activity: Activity 名称（可选）
        """
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
