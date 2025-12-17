"""
ZAT Python Backend
FastAPI + WebSocket + ADB Controller
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from core.adb_controller import ADBController
from core.task_engine import TaskEngine
from utils.logger import setup_logger, LogBroadcaster

# 全局实例
adb_controller: ADBController = None
task_engine: TaskEngine = None
log_broadcaster = LogBroadcaster()
logger = setup_logger("zat", log_broadcaster)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global adb_controller, task_engine
    
    logger.info("ZAT Backend 启动中...")
    
    # 初始化 ADB 控制器
    adb_controller = ADBController()
    
    # 初始化任务引擎
    task_engine = TaskEngine(adb_controller, log_broadcaster)
    
    logger.info("ZAT Backend 启动完成")
    
    yield
    
    # 清理资源
    logger.info("ZAT Backend 关闭中...")
    if task_engine:
        await task_engine.stop()
    logger.info("ZAT Backend 已关闭")


app = FastAPI(title="ZAT Backend", version="0.1.0", lifespan=lifespan)

# CORS 配置（仅本地）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://127.0.0.1:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HTTP 端点 ====================

@app.get("/")
async def root():
    return {"name": "ZAT Backend", "version": "0.1.0", "status": "running"}


@app.post("/connect")
async def connect_device():
    """连接 ADB 设备"""
    try:
        device = await adb_controller.auto_discover()
        if device:
            logger.info(f"已连接设备: {device}")
            
            # 获取屏幕分辨率
            try:
                resolution = await adb_controller.get_screen_resolution()
                return {
                    "success": True,
                    "device": device,
                    "resolution": {"width": resolution[0], "height": resolution[1]}
                }
            except Exception as e:
                logger.warning(f"获取分辨率失败: {e}")
                return {"success": True, "device": device}
        else:
            logger.error("未找到设备")
            raise HTTPException(status_code=404, detail="未找到设备")
    except Exception as e:
        logger.error(f"连接失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """获取当前状态（实时检测设备连接）"""
    # 实时检查设备是否在线
    is_online = await adb_controller.check_device_online() if adb_controller else False
    
    return {
        "connected": is_online,
        "device": adb_controller.device if adb_controller else None,
        "task_running": task_engine.is_running() if task_engine else False,
        "current_state": task_engine.current_state if task_engine else None,
    }


@app.post("/task-engine/start")
async def start_task_engine(task_name: str = "farming"):
    """启动任务引擎（自动化）"""
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        await task_engine.start(task_name)
        logger.info(f"任务引擎已启动: {task_name}")
        return {"success": True, "task": task_name}
    except Exception as e:
        logger.error(f"启动任务引擎失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/task-engine/stop")
async def stop_task_engine():
    """停止任务引擎（自动化）"""
    try:
        await task_engine.stop()
        logger.info("任务引擎已停止")
        return {"success": True}
    except Exception as e:
        logger.error(f"停止任务引擎失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/start-game")
async def start_game():
    """启动游戏（杖剑传说）"""
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        # 杖剑传说包名和Activity
        package = "com.leiting.zjcs"
        activity = "com.leiting.unity.AppActivity"
        
        await adb_controller.start_app(package, activity)
        logger.info(f"游戏已启动: {package}")
        return {"success": True, "package": package}
    except Exception as e:
        logger.error(f"启动游戏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/screenshot")
async def get_screenshot(gray: bool = False):
    """获取当前截图（仅 Debug 模式）"""
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        screenshot = await adb_controller.screencap(gray=gray)
        return Response(content=screenshot, media_type="image/jpeg")
    except Exception as e:
        logger.error(f"截图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket 端点 ====================

@app.websocket("/ws/log")
async def websocket_log(websocket: WebSocket):
    """日志流"""
    await websocket.accept()
    logger.info("日志 WebSocket 已连接")
    
    try:
        # 注册客户端
        await log_broadcaster.register(websocket)
        
        # 保持连接
        while True:
            # 接收心跳（可选）
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                # 发送 ping
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        logger.info("日志 WebSocket 已断开")
    finally:
        await log_broadcaster.unregister(websocket)


@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket):
    """状态流"""
    await websocket.accept()
    logger.info("状态 WebSocket 已连接")
    
    try:
        while True:
            # 每秒推送一次状态
            state = {
                "type": "state",
                "current_state": task_engine.current_state if task_engine else None,
                "is_running": task_engine.is_running() if task_engine else False,
                "loop_count": task_engine.loop_count if task_engine else 0,
            }
            await websocket.send_json(state)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("状态 WebSocket 已断开")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
