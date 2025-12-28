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
from core.navigator import Navigator
from core.dungeon_runner import DungeonRunner
from core.game_launcher import GameLauncher
from core.scene_graph import SCENES
from core.image_matcher import image_matcher
from utils.logger import setup_logger, LogBroadcaster

# 全局实例
adb_controller: ADBController = None
task_engine: TaskEngine = None
navigator: Navigator = None
dungeon_runner: DungeonRunner = None
game_launcher: GameLauncher = None
log_broadcaster = LogBroadcaster()
logger = setup_logger("zat", log_broadcaster)

# 事件广播器（用于推送导航失败等事件）
event_clients: set[WebSocket] = set()


async def broadcast_event(event_type: str, data: dict):
    # 广播事件到所有连接的客户端
    message = {"type": event_type, **data}
    dead_clients = set()
    
    for client in event_clients:
        try:
            await client.send_json(message)
        except Exception:
            dead_clients.add(client)
    
    for client in dead_clients:
        event_clients.discard(client)


async def on_navigation_failure(target: str, reason: str):
    # 导航失败回调
    logger.warning(f"导航失败事件: target={target}, reason={reason}")
    
    # 根据原因生成不同的提示信息
    if reason == "not_in_game":
        message = "无法识别游戏界面，请确保已进入游戏后再试"
    elif reason == "scene_unrecognized":
        message = "连续多次无法识别场景，请确保游戏在正常界面"
    else:
        message = f"无法导航到目标场景，已回退到主界面"
    
    await broadcast_event("navigation_failure", {
        "target": target,
        "reason": reason,
        "message": message
    })


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global adb_controller, task_engine, navigator, dungeon_runner, game_launcher
    
    logger.info("ZAT Backend 启动中...")
    
    # 初始化 ADB 控制器
    adb_controller = ADBController()
    
    # 初始化任务引擎
    task_engine = TaskEngine(adb_controller, log_broadcaster)
    
    # 初始化游戏导航器
    navigator = Navigator(adb_controller, image_matcher)
    navigator.set_failure_callback(on_navigation_failure)
    
    # 初始化副本执行器
    dungeon_runner = DungeonRunner(adb_controller, navigator)
    
    # 初始化游戏启动器
    game_launcher = GameLauncher(adb_controller)
    
    logger.info("ZAT Backend 启动完成")
    
    yield
    
    # 清理资源
    logger.info("ZAT Backend 关闭中...")
    if dungeon_runner:
        dungeon_runner.stop()
    if task_engine:
        await task_engine.stop()
    # 注意：不关闭游戏，让用户自己决定
    if adb_controller:
        await adb_controller.stop_capture()
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
    # 连接 ADB 设备并启动屏幕捕获
    try:
        device = await adb_controller.auto_discover()
        if device:
            logger.info(f"已连接设备: {device}")
            
            # 启动屏幕捕获
            try:
                await adb_controller.start_capture()
                logger.info("屏幕捕获已启动")
            except Exception as e:
                logger.warning(f"启动屏幕捕获失败: {e}")
            
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
    # 获取当前状态（实时检测设备连接）
    # 实时检查设备是否在线
    is_online = await adb_controller.check_device_online() if adb_controller else False
    
    # 检查游戏是否运行
    game_running = False
    if is_online and game_launcher:
        game_running = await game_launcher.is_running()
    
    return {
        "connected": is_online,
        "device": adb_controller.device if adb_controller else None,
        "capture_running": adb_controller.capture_running if adb_controller else False,
        "capture_fps": adb_controller.capture_fps if adb_controller else 0,
        "task_running": task_engine.is_running() if task_engine else False,
        "current_state": task_engine.current_state if task_engine else None,
        "game_running": game_running,
        "dungeon_state": dungeon_runner.state.value if dungeon_runner else "idle",
        "dungeon_running": dungeon_runner.is_running if dungeon_runner else False,
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
async def start_game(wait_ready: bool = False, timeout: int = 60):
    """
    启动游戏（杖剑传说）
    
    Args:
        wait_ready: 是否等待游戏加载完成并自动点击进入
        timeout: 等待超时时间（秒）
    """
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    result = await game_launcher.start(wait_ready=wait_ready, timeout=timeout)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message", "启动失败"))
    return result


@app.post("/stop-game")
async def stop_game():
    """停止游戏（杖剑传说）"""
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    result = await game_launcher.stop()
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("message", "停止失败"))
    return result


@app.get("/debug/screenshot")
async def get_screenshot(gray: bool = False):
    # 获取当前截图
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    if not adb_controller.capture_running:
        raise HTTPException(status_code=400, detail="屏幕捕获未启动，请先连接设备")
    
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
        "world_tree": "世界之树",
        "mount_mechagod": "机神山",
        "sea_palace": "海之宫遗迹",
        "mizumoto_shirine": "源水大社",
    }
    dungeon_difficulties = {
        "world_tree": ["normal", "hard"],
        "mount_mechagod": ["normal", "hard"],
        "sea_palace": ["normal", "hard"],
        "mizumoto_shirine": ["normal", "hard", "nightmare"],
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
    导航到指定副本（仅导航，不开始战斗）
    
    Args:
        dungeon_id: 副本ID (world_tree, mount_mechagod, sea_palace, mizumoto_shrine)
        difficulty: 难度 (normal, hard, nightmare)
    """
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        target_scene = f"dungeon:{dungeon_id}"
        success = await navigator.navigate_to(target_scene)
        if success:
            return {"success": True, "dungeon": dungeon_id, "difficulty": difficulty}
        else:
            return {"success": False, "message": "导航失败"}
    except Exception as e:
        logger.error(f"导航到副本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-dungeon")
async def run_dungeon(dungeon_id: str, difficulty: str = "normal", count: int = 1):
    # 执行副本
    # 
    # Args:
    #     dungeon_id: 副本ID (world_tree, mount_mechagod, sea_palace, mizumoto_shrine)
    #     difficulty: 难度 (normal, hard, nightmare)
    #     count: 执行次数，1 为单次，>1 为循环，-1 为无限循环
    # 
    # Returns:
    #     单次: {"success": bool, "rank": str | None, "message": str}
    #     多次: {"total": int, "completed": int, "failed": int, "ranks": list}
    if not adb_controller.is_connected():
        raise HTTPException(status_code=400, detail="设备未连接")
    
    try:
        if count == 1:
            result = await dungeon_runner.run_once(dungeon_id, difficulty)
            return {
                "success": result.success,
                "rank": result.rank,
                "message": result.message
            }
        else:
            # count > 1 或 count == -1（无限循环）
            result = await dungeon_runner.run_loop(dungeon_id, difficulty, count)
            return {
                "total": result.total,
                "completed": result.completed,
                "failed": result.failed,
                "ranks": result.ranks,
                "success_rate": result.success_rate
            }
    except Exception as e:
        logger.error(f"执行副本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop-dungeon")
async def stop_dungeon():
    """停止副本运行"""
    if dungeon_runner:
        dungeon_runner.stop()
        return {"success": True, "message": "已停止"}
    return {"success": False, "message": "副本执行器未初始化"}


@app.get("/dungeon-history")
async def get_dungeon_history():
    """获取副本运行历史"""
    if not dungeon_runner:
        return {"records": []}
    
    # 获取历史记录（最新的在前面），然后反转使最早的在前面
    history = dungeon_runner.history
    records = []
    for record in history:
        records.append({
            "id": record.id,
            "name": record.dungeon_name,
            "difficulty": record.difficulty_name,
            "rank": record.rank,
            "time": record.time,
            "status": record.status,
        })
    # 反转顺序，最早的在前面（时间线从左到右）
    records.reverse()
    return {"records": records}


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
    
    current = navigator.get_current_scene()
    if current:
        scene = SCENES.get(current)
        return {
            "scene_id": current,
            "scene_name": scene.name if scene else None,
            "detected": False
        }
    
    # 如果当前场景未知，尝试检测
    detected = await navigator.detect_current_scene()
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
        success = await navigator.navigate_to(scene_id)
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
    """状态流 - 推送副本和任务状态"""
    await websocket.accept()
    logger.info("状态 WebSocket 已连接")
    
    # 注册到事件广播
    event_clients.add(websocket)
    
    last_dungeon_state = None
    
    try:
        while True:
            # 获取当前副本状态
            current_dungeon_state = dungeon_runner.state.value if dungeon_runner else "idle"
            dungeon_running = dungeon_runner.is_running if dungeon_runner else False
            
            # 状态变化时立即推送，否则每秒推送一次
            state = {
                "type": "state",
                "dungeon_state": current_dungeon_state,
                "dungeon_running": dungeon_running,
                "task_running": task_engine.is_running() if task_engine else False,
                "current_state": task_engine.current_state if task_engine else None,
            }
            await websocket.send_json(state)
            
            last_dungeon_state = current_dungeon_state
            
            # 如果副本正在运行，检测频率更高
            interval = 0.3 if dungeon_running else 1.0
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        logger.info("状态 WebSocket 已断开")
    finally:
        event_clients.discard(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
