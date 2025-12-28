# scrcpy 屏幕捕获模块
# 使用 scrcpy 的 H.264 视频流实现低延迟屏幕捕获

import asyncio
import logging
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Callable
from queue import Queue, Empty

import numpy as np

logger = logging.getLogger("zat.scrcpy")


class ScrcpyError(Exception):
    # scrcpy 相关错误
    pass


class ScrcpyCapture:
    # scrcpy 屏幕捕获器
    # 通过 scrcpy 的 H.264 流实现低延迟屏幕捕获
    
    def __init__(
        self,
        device: str,
        max_size: int = 1080,
        bit_rate: str = '8M',
        max_fps: int = 30,
        scrcpy_path: Optional[str] = None,
        adb_path: Optional[str] = None,
    ):
        # 初始化 scrcpy 捕获器
        # 
        # Args:
        #     device: ADB 设备地址
        #     max_size: 最大分辨率（短边）
        #     bit_rate: 视频码率
        #     max_fps: 最大帧率
        #     scrcpy_path: scrcpy 可执行文件路径
        #     adb_path: adb 可执行文件路径
        
        self.device = device
        self.max_size = max_size
        self.bit_rate = bit_rate
        self.max_fps = max_fps
        self.scrcpy_path = scrcpy_path or self._find_scrcpy()
        self.adb_path = adb_path or 'adb'
        
        self._proc: Optional[subprocess.Popen] = None
        self._decoder_thread: Optional[threading.Thread] = None
        self._running = False
        self._frame_queue: Queue = Queue(maxsize=2)  # 只保留最新帧
        self._latest_frame: Optional[np.ndarray] = None
        self._frame_lock = threading.Lock()
        self._on_frame_callback: Optional[Callable[[np.ndarray], None]] = None
        
        # 统计信息
        self._frame_count = 0
        self._start_time = 0.0
        self._last_frame_time = 0.0
    
    def _find_scrcpy(self) -> str:
        # 查找 scrcpy 可执行文件
        
        # 1. 检查打包后的路径
        if getattr(sys, 'frozen', False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent.parent
        
        vendor_path = base / 'vendor' / 'scrcpy'
        if sys.platform == 'win32':
            scrcpy_exe = vendor_path / 'scrcpy.exe'
        else:
            scrcpy_exe = vendor_path / 'scrcpy'
        
        if scrcpy_exe.exists():
            return str(scrcpy_exe)
        
        # 2. 检查系统 PATH
        import shutil
        system_scrcpy = shutil.which('scrcpy')
        if system_scrcpy:
            return system_scrcpy
        
        raise ScrcpyError(
            "未找到 scrcpy，请安装 scrcpy 或将其放置在 vendor/scrcpy/ 目录下"
        )
    
    def _build_command(self) -> list[str]:
        # 构建 scrcpy 命令
        cmd = [
            self.scrcpy_path,
            '--serial', self.device,
            '--no-window',           # 不显示窗口
            '--no-audio',            # 不捕获音频
            '--no-control',          # 不发送控制事件（控制用 adb）
            '--video-codec=h264',    # 使用 H.264 编码
            f'--max-size={self.max_size}',
            f'--video-bit-rate={self.bit_rate}',
            f'--max-fps={self.max_fps}',
            '--video-source=display',
            '--record=-',            # 输出到 stdout
            '--record-format=h264',  # H.264 格式
        ]
        return cmd
    
    def _decoder_loop(self):
        # 解码线程主循环
        try:
            import av
        except ImportError:
            logger.error("请安装 PyAV: pip install av")
            return
        
        logger.info("解码线程启动")
        
        try:
            container = av.open(
                self._proc.stdout,
                format='h264',
                options={'flags': 'low_delay'}
            )
            
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
                
                # 放入队列（非阻塞，丢弃旧帧）
                try:
                    # 清空队列中的旧帧
                    while not self._frame_queue.empty():
                        try:
                            self._frame_queue.get_nowait()
                        except Empty:
                            break
                    self._frame_queue.put_nowait(img)
                except:
                    pass
                    
        except Exception as e:
            if self._running:
                logger.error(f"解码错误: {e}")
        finally:
            logger.info("解码线程退出")
    
    def start(self):
        # 启动 scrcpy 捕获
        if self._running:
            logger.warning("scrcpy 已在运行")
            return
        
        logger.info(f"启动 scrcpy 捕获: {self.device}")
        
        cmd = self._build_command()
        logger.debug(f"scrcpy 命令: {' '.join(cmd)}")
        
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            raise ScrcpyError(f"scrcpy 不存在: {self.scrcpy_path}")
        except Exception as e:
            raise ScrcpyError(f"启动 scrcpy 失败: {e}")
        
        self._running = True
        self._start_time = time.time()
        self._frame_count = 0
        
        # 启动解码线程
        self._decoder_thread = threading.Thread(
            target=self._decoder_loop,
            daemon=True
        )
        self._decoder_thread.start()
        
        logger.info("scrcpy 捕获已启动")
    
    def stop(self):
        # 停止 scrcpy 捕获
        if not self._running:
            return
        
        logger.info("停止 scrcpy 捕获")
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
        
        # 清空队列
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except Empty:
                break
        
        logger.info("scrcpy 捕获已停止")
    
    def get_frame(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        # 获取最新一帧
        # 
        # Args:
        #     timeout: 超时时间（秒）
        # 
        # Returns:
        #     BGR 格式的 numpy 数组，如果超时返回 None
        
        if not self._running:
            return None
        
        try:
            return self._frame_queue.get(timeout=timeout)
        except Empty:
            # 如果队列为空，返回缓存的最新帧
            with self._frame_lock:
                return self._latest_frame
    
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


class AsyncScrcpyCapture:
    # 异步 scrcpy 捕获器封装
    # 提供异步接口，方便在 asyncio 环境中使用
    
    def __init__(self, capture: ScrcpyCapture):
        self._capture = capture
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    async def start(self):
        # 异步启动
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._capture.start)
    
    async def stop(self):
        # 异步停止
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._capture.stop)
    
    async def get_frame(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        # 异步获取帧
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self._capture.get_frame(timeout)
        )
    
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
