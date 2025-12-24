# API 文档

后端服务运行在 `http://127.0.0.1:8000`

## HTTP 端点

### 基础

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 健康检查 |
| GET | `/status` | 获取当前状态 |
| POST | `/connect` | 连接 ADB 设备 |

### 游戏控制

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/start-game` | 启动游戏 |
| POST | `/stop-game` | 停止游戏 |

### 副本系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dungeons` | 获取副本列表 |
| POST | `/run-dungeon` | 执行副本 |
| POST | `/stop-dungeon` | 停止副本 |
| GET | `/dungeon-history` | 获取运行历史 |

### 导航系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/scenes` | 获取所有场景 |
| GET | `/current-scene` | 获取当前场景 |
| POST | `/navigate-to` | 导航到指定场景 |
| POST | `/navigate-to-dungeon` | 导航到副本 |

### 任务引擎

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/task-engine/start` | 启动任务引擎 |
| POST | `/task-engine/stop` | 停止任务引擎 |

### 调试

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/debug/screenshot` | 获取截图 |
| GET | `/debug/ocr` | OCR 调试 |

---

## WebSocket 端点

### `/ws/log` - 日志流

实时推送后端日志

```json
{
  "level": "INFO",
  "message": "任务引擎已启动",
  "timestamp": "2024-01-01T12:00:00"
}
```

### `/ws/state` - 状态流

实时推送运行状态

```json
{
  "type": "state",
  "dungeon_state": "fighting",
  "dungeon_running": true,
  "task_running": false,
  "current_state": null
}
```

---

## 示例

### 连接设备
```bash
curl -X POST http://127.0.0.1:8000/connect
```

### 执行副本（单次）
```bash
curl -X POST "http://127.0.0.1:8000/run-dungeon?dungeon_id=world_tree&difficulty=normal&count=1"
```

### 执行副本（循环 10 次）
```bash
curl -X POST "http://127.0.0.1:8000/run-dungeon?dungeon_id=world_tree&difficulty=hard&count=10"
```

### 执行副本（无限循环）
```bash
curl -X POST "http://127.0.0.1:8000/run-dungeon?dungeon_id=world_tree&count=-1"
```
