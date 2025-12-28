# 屏幕捕获模块
# 使用 adb screenrecord 的 H.264 视频流实现低延迟屏幕捕获

import asyncio
import logging
import subprocess
import threading
import time
from typing import Optional, Callable

import numpy as np

logger = logging.getLogger("zat.capture")


class ScreenCaptureError(Exception):
    # 屏幕捕获相关错误
    pass


class ScreenCapture:
    # 屏幕捕获器
    # 通过 adb screenrecord 的 H.264 流实现低延迟屏幕捕获
    # 自动处理 screenrecord 的时间限制，流结束后自动重启
    
    def __init__(
        self,
        device: str,
        bit_rate: str = '8M',
        adb_path: Optional[str] = None,
    ):
        # 初始化捕获器
        # 
        # Args:
        #     device: ADB 设备地址
        #     bit_rate: 视频码率
        #     adb_path: adb 可执行文件路径
        
        self.device = device
        self.bit_rate = bit_rate
        self.adb_path = adb_path or 'adb'
        
        self._proc: Optional[subprocess.Popen] = None
        self._decoder_thread: Optional[threading.Thread] = None
        self._running = False
        self._latest_frame: Optional[np.ndarray] = None
        self._frame_lock = threading.Lock()
        self._on_frame_callback: Optional[Callable[[np.ndarray], None]] = None
        
        # 统计信息
        self._frame_count = 0
        self._start_time = 0.0
        self._last_frame_time = 0.0
        self._restart_count = 0
    
    def _build_command(self) -> list[str]:
        # 构建 adb screenrecord 命令
        bit_rate = self.bit_rate.replace('M', '000000').replace('m', '000000')
        cmd = [
            self.adb_path,
            '-s', self.device,
            'exec-out',
            'screenrecord',
            '--output-format=h264',
            f'--bit-rate={bit_rate}',
            '-',  # 输出到 stdout
        ]
        return cmd
    
    def _start_process(self):
        # 启动 screenrecord 进程
        cmd = self._build_command()
        logger.debug(f"命令: {' '.join(cmd)}")
        
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    
    def _decoder_loop(self):
        # 解码线程主循环，支持自动重启
        try:
            import av
        except ImportError:
            logger.error("请安装 PyAV: pip install av")
            return
        
        while self._running:
            logger.info(f"解码线程启动 (重启次数: {self._restart_count})")
            
            try:
                if self._proc is None or self._proc.poll() is not None:
                    # 进程不存在或已退出，重新启动
                    self._start_process()
                
                container = av.open(self._proc.stdout, format='h264')
                logger.info("容器已打开，开始解码")
                
                for frame in container.decode(video=0):
                    if not self._running:
                        break
                    
                    # 转换为 numpy 数组 (BGR)
                    img = frame.to_ndarray(format='bgr24')
                    
                    # 更新最新帧
                    with self._frame_lock:
                        self._latest_frame = img
                        self._frame_count += 1
                        self._last_frame_time = time.time()
                    
                    # 回调
                    if self._on_frame_callback:
                        try:
                            self._on_frame_callback(img)
                        except Exception as e:
                            logger.error(f"帧回调错误: {e}")
                
                # 流结束，准备重启
                if self._running:
                    logger.info("视频流结束，准备重启...")
                    self._restart_count += 1
                    # 清理旧进程
                    if self._proc:
                        self._proc.terminate()
                        try:
                            self._proc.wait(timeout=1)
                        except:
                            self._proc.kill()
                        self._proc = None
                    time.sleep(0.1)  # 短暂等待
                        
            except Exception as e:
                if self._running:
                    logger.error(f"解码错误: {e}, 将在 1 秒后重试...")
                    self._restart_count += 1
                    # 清理
                    if self._proc:
                        try:
                            self._proc.terminate()
                            self._proc.wait(timeout=1)
                        except:
                            pass
                        self._proc = None
                    time.sleep(1)
        
        logger.info("解码线程退出")
    
    def start(self):
        # 启动屏幕捕获
        if self._running:
            logger.warning("捕获已在运行")
            return
        
        logger.info(f"启动屏幕捕获: {self.device}")
        
        try:
            self._start_process()
        except FileNotFoundError:
            raise ScreenCaptureError(f"adb 不存在: {self.adb_path}")
        except Exception as e:
            raise ScreenCaptureError(f"启动捕获失败: {e}")
        
        self._running = True
        self._start_time = time.time()
        self._frame_count = 0
        self._restart_count = 0
        
        # 启动解码线程
        self._decoder_thread = threading.Thread(
            target=self._decoder_loop,
            daemon=True
        )
        self._decoder_thread.start()
        
        logger.info("屏幕捕获已启动")
    
    def stop(self):
        # 停止屏幕捕获
        if not self._running:
            return
        
        logger.info("停止屏幕捕获")
        self._running = False
        
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None
        
        if self._decoder_thread:
            self._decoder_thread.join(timeout=2)
            self._decoder_thread = None
        
        logger.info("屏幕捕获已停止")
    
    def get_frame(self) -> Optional[np.ndarray]:
        # 获取最新一帧
        # 
        # Returns:
        #     BGR 格式的 numpy 数组，如果没有帧返回 None
        return self.get_latest_frame()
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        # 获取缓存的最新帧（非阻塞）
        with self._frame_lock:
            return self._latest_frame
    
    def set_frame_callback(self, callback: Optional[Callable[[np.ndarray], None]]):
        # 设置帧回调函数
        # 每收到一帧就会调用此函数
        self._on_frame_callback = callback
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    @property
    def fps(self) -> float:
        # 当前帧率
        if not self._running or self._start_time == 0:
            return 0.0
        elapsed = time.time() - self._start_time
        if elapsed > 0:
            return self._frame_count / elapsed
        return 0.0
    
    @property
    def frame_count(self) -> int:
        return self._frame_count
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class AsyncScreenCapture:
    # 异步屏幕捕获器封装
    # 提供异步接口，方便在 asyncio 环境中使用
    
    def __init__(self, capture: ScreenCapture):
        self._capture = capture
    
    async def start(self):
        # 异步启动
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._capture.start)
    
    async def stop(self):
        # 异步停止
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._capture.stop)
    
    async def get_frame(self) -> Optional[np.ndarray]:
        # 异步获取帧
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._capture.get_frame)
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        # 获取最新帧（非阻塞）
        return self._capture.get_latest_frame()
    
    @property
    def is_running(self) -> bool:
        return self._capture.is_running
    
    @property
    def fps(self) -> float:
        return self._capture.fps
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
