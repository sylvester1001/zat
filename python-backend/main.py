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
from core.dungeon_navigator import GameNavigator
from core.scene_graph import SCENES
from utils.logger import setup_logger, LogBroadcaster

# 全局实例
adb_controller: ADBController = None
task_engine: TaskEngine = None
game_navigator: GameNavigator = None
log_broadcaster = LogBroadcaster()
logger = setup_logger("zat", log_broadcaster)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global adb_controller, task_engine, game_navigator
    
    logger.info("ZAT Backend 启动中...")
    
    # 初始化 ADB 控制器
    adb_controller = ADBController()
    
    # 初始化任务引擎
    task_engine = TaskEngine(adb_controller, log_broadcaster)
    
    # 初始化游戏导航器
    game_navigator = GameNavigator(adb_controller)
    
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
    
    # 检查游戏是否运行
    game_running = False
    if is_online and adb_controller:
        game_running = await adb_controller.is_app_running("com.leiting.zjcs")
    
    return {
        "connected": is_online,
        "device": adb_controller.device if adb_controller else None,
        "task_running": task_engine.is_running() if task_engine else False,
        "current_state": task_engine.current_state if task_engine else None,
        "game_running": game_running,
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


# 用于中断 wait_for_game_ready 的标志
_game_starting = False

@app.post("/start-game")
async def start_game(wait_ready: bool = False, timeout: int = 60):
    """
    启动游戏（杖剑传说）
    
    Args:
        wait_ready: 是否等待游戏加载完成并自动点击进入
        timeout: 等待超时时间（秒）
    """
    global _game_starting
    
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        # 杖剑传说包名和Activity
        package = "com.leiting.zjcs"
        activity = "com.leiting.unity.AppActivity"
        
        await adb_controller.start_app(package, activity)
        logger.info(f"游戏已启动: {package}")
        
        # 如果需要等待游戏加载完成
        if wait_ready:
            _game_starting = True
            task_engine._running = True
            try:
                success = await task_engine.wait_for_game_ready(timeout=timeout)
                if not _game_starting:
                    # 被中断了
                    return {"success": True, "package": package, "entered": False, "message": "已取消"}
                if not success:
                    return {"success": True, "package": package, "entered": False, "message": "游戏已启动但等待进入超时"}
                return {"success": True, "package": package, "entered": True}
            finally:
                _game_starting = False
                task_engine._running = False
                task_engine.current_state = None
        
        return {"success": True, "package": package}
    except Exception as e:
        logger.error(f"启动游戏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop-game")
async def stop_game():
    """停止游戏（杖剑传说）"""
    global _game_starting
    
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    # 中断 wait_for_game_ready
    _game_starting = False
    task_engine._running = False
    
    try:
        package = "com.leiting.zjcs"
        await adb_controller.stop_app(package)
        logger.info(f"游戏已停止: {package}")
        return {"success": True}
    except Exception as e:
        logger.error(f"停止游戏失败: {e}")
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


@app.get("/dungeons")
async def get_dungeons():
    """获取可用副本列表"""
    # 从场景图中获取副本场景
    dungeons = []
    dungeon_names = {
        "world-tree": "世界之树",
        "mount-mechagod": "机神山",
        "sea-palace": "海之宫遗迹",
        "mizumoto-shrine": "源水大社",
    }
    dungeon_difficulties = {
        "world-tree": ["normal", "hard"],
        "mount-mechagod": ["normal", "hard"],
        "sea-palace": ["normal", "hard"],
        "mizumoto-shrine": ["normal", "hard", "nightmare"],
    }
    
    for dungeon_id, name in dungeon_names.items():
        dungeons.append({
            "id": dungeon_id,
            "name": name,
            "difficulties": dungeon_difficulties.get(dungeon_id, ["normal"]),
        })
    return {"dungeons": dungeons}


@app.post("/navigate-to-dungeon")
async def navigate_to_dungeon(dungeon_id: str, difficulty: str = "normal"):
    """
    导航到指定副本
    
    Args:
        dungeon_id: 副本ID (world-tree, mount-mechagod, sea-palace, mizumoto-shrine)
        difficulty: 难度 (normal, hard, nightmare)
    """
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        success = await game_navigator.navigate_to_dungeon(dungeon_id)
        if success:
            return {"success": True, "dungeon": dungeon_id, "difficulty": difficulty}
        else:
            return {"success": False, "message": "导航失败"}
    except Exception as e:
        logger.error(f"导航到副本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenes")
async def get_scenes():
    """获取所有场景"""
    scenes = []
    for scene_id, scene in SCENES.items():
        scenes.append({
            "id": scene_id,
            "name": scene.name,
            "transitions": list(scene.transitions.keys()),
            "back_to": scene.back_to,
        })
    return {"scenes": scenes}


@app.get("/current-scene")
async def get_current_scene():
    """获取当前场景"""
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    current = game_navigator.get_current_scene()
    if current:
        scene = SCENES.get(current)
        return {
            "scene_id": current,
            "scene_name": scene.name if scene else None,
            "detected": False
        }
    
    # 如果当前场景未知，尝试检测
    detected = await game_navigator.detect_current_scene()
    if detected:
        scene = SCENES.get(detected)
        return {
            "scene_id": detected,
            "scene_name": scene.name if scene else None,
            "detected": True
        }
    
    return {"scene_id": None, "scene_name": None, "detected": True}


@app.post("/navigate-to")
async def navigate_to_scene(scene_id: str):
    """
    导航到指定场景
    
    Args:
        scene_id: 场景ID
    """
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    if scene_id not in SCENES:
        raise HTTPException(status_code=400, detail=f"未知场景: {scene_id}")
    
    try:
        success = await game_navigator.navigate_to(scene_id)
        if success:
            return {"success": True, "scene": scene_id}
        else:
            return {"success": False, "message": "导航失败"}
    except Exception as e:
        logger.error(f"导航失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/ocr")
async def debug_ocr(target: str = None):
    """
    OCR 调试端点
    
    Args:
        target: 要查找的目标文字（可选），如果不指定则返回所有识别到的文字
    """
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        from core.image_matcher import image_matcher
        
        screen = await adb_controller.screencap_array()
        
        if target:
            # 查找特定文字
            result = image_matcher.ocr_find_text(screen, target)
            if result:
                x, y, confidence = result
                return {
                    "found": True,
                    "target": target,
                    "position": {"x": x, "y": y},
                    "confidence": confidence
                }
            else:
                return {"found": False, "target": target}
        else:
            # 返回所有识别到的文字
            texts = image_matcher.ocr_get_all_text(screen)
            return {
                "texts": [
                    {"text": t, "confidence": c, "position": {"x": pos[0], "y": pos[1]}}
                    for t, c, pos in texts
                ]
            }
    except Exception as e:
        logger.error(f"OCR 失败: {e}")
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
