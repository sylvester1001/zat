# 任务引擎
# 负责执行自动化任务流程

import asyncio
import logging
from typing import Optional

from core.adb_controller import ADBController
from utils.logger import LogBroadcaster

logger = logging.getLogger("zat.task")


class TaskEngine:
    # 任务引擎 - 负责自动化任务的执行
    
    def __init__(self, adb: ADBController, log_broadcaster: LogBroadcaster):
        self.adb = adb
        self.log_broadcaster = log_broadcaster
        
        self.current_state: Optional[str] = None
        self.loop_count: int = 0
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None
    
    def is_running(self) -> bool:
        # 检查任务是否正在运行
        return self._running
    
    async def start(self, task_name: str):
        # 启动任务
        if self._running:
            raise RuntimeError("任务已在运行")
        
        self._running = True
        self.loop_count = 0
        self.current_state = "STARTING"
        
        # 创建任务
        self._task = asyncio.create_task(self._run_task(task_name))
        
        logger.info(f"任务引擎已启动: {task_name}")
    
    async def stop(self):
        # 停止任务
        if not self._running:
            return
        
        self._running = False
        self.current_state = "STOPPING"
        
        # 取消任务
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        self.current_state = "STOPPED"
        logger.info("任务引擎已停止")
    
    async def _run_task(self, task_name: str):
        # 运行任务（内部方法）
        try:
            logger.info(f"开始执行任务: {task_name}")
            
            # TODO: 加载任务配置
            # TODO: 执行任务流程
            
            # 临时：简单的测试循环
            while self._running:
                self.current_state = "RUNNING"
                self.loop_count += 1
                
                logger.info(f"任务循环 #{self.loop_count}")
                
                # 模拟任务执行
                await asyncio.sleep(5)
            
        except asyncio.CancelledError:
            logger.info("任务已取消")
            raise
        except Exception as e:
            logger.error(f"任务执行失败: {e}", exc_info=True)
            self.current_state = "ERROR"
        finally:
            self._running = False
