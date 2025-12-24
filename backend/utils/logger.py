"""
日志工具
支持 WebSocket 广播
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import Set
from fastapi import WebSocket


class LogBroadcaster:
    """日志广播器"""
    
    def __init__(self):
        self.clients: Set[WebSocket] = set()
    
    async def register(self, websocket: WebSocket):
        """注册客户端"""
        self.clients.add(websocket)
    
    async def unregister(self, websocket: WebSocket):
        """注销客户端"""
        self.clients.discard(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息到所有客户端"""
        if not self.clients:
            return
        
        # 移除断开的连接
        dead_clients = set()
        
        for client in self.clients:
            try:
                await client.send_json(message)
            except Exception:
                dead_clients.add(client)
        
        # 清理断开的连接
        for client in dead_clients:
            self.clients.discard(client)


class WebSocketHandler(logging.Handler):
    """WebSocket 日志处理器"""
    
    def __init__(self, broadcaster: LogBroadcaster):
        super().__init__()
        self.broadcaster = broadcaster
    
    def emit(self, record: logging.LogRecord):
        """发送日志记录"""
        try:
            message = {
                "type": "log",
                "level": record.levelname.lower(),
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "logger": record.name,
                "message": record.getMessage(),
            }
            
            # 使用 asyncio 发送（需要在事件循环中）
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.broadcaster.broadcast(message))
            except RuntimeError:
                # 没有事件循环，忽略
                pass
        except Exception:
            self.handleError(record)


def setup_logger(name: str, broadcaster: LogBroadcaster) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        broadcaster: 日志广播器
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    
    # WebSocket 处理器
    ws_handler = WebSocketHandler(broadcaster)
    ws_handler.setLevel(logging.INFO)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(ws_handler)
    
    return logger
