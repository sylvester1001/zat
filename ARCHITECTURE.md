# ZAT 架构文档

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        ZAT Desktop App                           │
│                     (Tauri + Svelte + TS)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ TaskControl  │  │  LogViewer   │  │  StatusBar   │          │
│  │              │  │              │  │              │          │
│  │ - 连接设备   │  │ - 实时日志   │  │ - 连接状态   │          │
│  │ - 启动任务   │  │ - 自动滚动   │  │ - 任务状态   │          │
│  │ - 停止任务   │  │ - 日志过滤   │  │ - 循环计数   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐                                                │
│  │ DebugPanel   │                                                │
│  │              │                                                │
│  │ - 刷新截图   │                                                │
│  │ - 灰度模式   │                                                │
│  │ - 图像预览   │                                                │
│  └──────────────┘                                                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         │                                    │
         │ HTTP                               │ WebSocket
         │ (控制指令)                         │ (实时数据)
         ↓                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Python Backend (FastAPI)                       │
│                      127.0.0.1:8000                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  HTTP 端点:                    WebSocket 端点:                   │
│  ├─ POST /connect             ├─ /ws/log    (日志流)            │
│  ├─ GET  /status              └─ /ws/state  (状态流)            │
│  ├─ POST /start                                                  │
│  ├─ POST /stop                                                   │
│  └─ GET  /debug/screenshot                                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    核心模块                              │   │
│  │                                                           │   │
│  │  ┌──────────────────┐  ┌──────────────────┐            │   │
│  │  │ ADBController    │  │  TaskEngine      │            │   │
│  │  │                  │  │                  │            │   │
│  │  │ - auto_discover  │  │ - start          │            │   │
│  │  │ - screencap      │  │ - stop           │            │   │
│  │  │ - tap            │  │ - state_machine  │            │   │
│  │  │ - swipe          │  │ - loop_control   │            │   │
│  │  │ - start_app      │  │                  │            │   │
│  │  └──────────────────┘  └──────────────────┘            │   │
│  │                                                           │   │
│  │  ┌──────────────────┐  ┌──────────────────┐            │   │
│  │  │ VisionEngine     │  │ LogBroadcaster   │            │   │
│  │  │ (待实现)         │  │                  │            │   │
│  │  │                  │  │ - register       │            │   │
│  │  │ - load_template  │  │ - unregister     │            │   │
│  │  │ - match_template │  │ - broadcast      │            │   │
│  │  │ - find_all       │  │                  │            │   │
│  │  └──────────────────┘  └──────────────────┘            │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         │
         │ ADB (Android Debug Bridge)
         │ exec-out screencap -p
         │ shell input tap x y
         │ shell input swipe x1 y1 x2 y2
         ↓
┌─────────────────────────────────────────────────────────────────┐
│              Android 模拟器 (MuMu / BlueStacks)                  │
│                    127.0.0.1:16384                               │
│                                                                   │
│                      ┌─────────────┐                             │
│                      │  杖剑传说    │                             │
│                      │             │                             │
│                      │  游戏画面   │                             │
│                      └─────────────┘                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 数据流

### 1. 连接设备流程

```
用户点击"连接设备"
    ↓
前端: api.connect()
    ↓
HTTP POST /connect
    ↓
后端: ADBController.auto_discover()
    ├─ 检查已连接设备 (adb devices)
    └─ 尝试常见端口 (16384, 5555, ...)
    ↓
返回设备地址
    ↓
前端显示: "已连接: 127.0.0.1:16384"
```

### 2. 启动任务流程

```
用户点击"启动任务"
    ↓
前端: api.start('farming')
    ↓
HTTP POST /start?task_name=farming
    ↓
后端: TaskEngine.start('farming')
    ├─ 加载任务配置 (JSON)
    ├─ 初始化状态机
    └─ 启动异步任务
    ↓
任务循环:
    ├─ 截图 (ADB)
    ├─ 图像识别 (Vision)
    ├─ 执行动作 (ADB)
    ├─ 状态转换
    └─ 日志记录
    ↓
WebSocket 推送:
    ├─ /ws/log: 日志消息
    └─ /ws/state: 状态更新
    ↓
前端实时显示
```

### 3. 截图调试流程

```
用户点击"刷新截图"
    ↓
前端: fetch('/debug/screenshot?gray=false')
    ↓
HTTP GET /debug/screenshot
    ↓
后端: ADBController.screencap()
    ├─ adb exec-out screencap -p
    ├─ 解码 PNG
    ├─ 可选: 转灰度图
    └─ JPEG 编码 (质量 65)
    ↓
返回 JPEG bytes
    ↓
前端: Blob URL 显示图片
```

### 4. 日志流

```
后端任务执行
    ↓
logger.info("识别到开始按钮")
    ↓
WebSocketHandler.emit()
    ↓
LogBroadcaster.broadcast()
    ├─ 遍历所有 WebSocket 客户端
    └─ 发送 JSON 消息
    ↓
前端 WebSocket.onmessage
    ↓
LogViewer 显示日志
    └─ 自动滚动到底部
```

## 技术选型理由

### 前端：Svelte + TypeScript

**优势：**
- ✅ 编译时优化，运行时性能好
- ✅ 代码简洁，学习曲线平缓
- ✅ TypeScript 类型安全
- ✅ 响应式更新简单直观

**劣势：**
- ❌ 生态相对较小（但足够用）

### 桌面壳：Tauri

**优势：**
- ✅ 体积小（比 Electron 小 10 倍）
- ✅ 性能好（Rust + 系统 WebView）
- ✅ 安全性高
- ✅ 跨平台（Windows/macOS/Linux）

**劣势：**
- ❌ 需要 Rust 环境（但不需要写 Rust）

### 后端：Python + FastAPI

**优势：**
- ✅ 开发速度快
- ✅ 图像识别生态成熟（OpenCV）
- ✅ FastAPI 性能好，支持异步
- ✅ 自动生成 API 文档
- ✅ WebSocket 支持完善

**劣势：**
- ❌ 打包体积大（200MB+）
- ❌ 性能不如 Rust（但够用）

### 图像识别：OpenCV

**优势：**
- ✅ 功能强大，久经考验
- ✅ 模板匹配简单高效
- ✅ 文档丰富，社区活跃

**劣势：**
- ❌ 依赖体积大

## 性能优化

### 1. 截图优化

```python
# ❌ 慢方式（500ms）
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# ✅ 快方式（100ms）
adb exec-out screencap -p
```

**优化效果：5 倍速度提升**

### 2. 图像传输优化

```python
# ❌ 慢方式（Base64 + JSON）
base64_str = base64.b64encode(image).decode()
json.dumps({"image": base64_str})  # 体积增加 33%

# ✅ 快方式（Binary WebSocket / HTTP）
await websocket.send_bytes(image)  # 直接传输二进制
```

**优化效果：体积减少 33%，速度提升 2 倍**

### 3. 灰度图优化

```python
# 彩色图：1280x720x3 = 2.7 MB (PNG)
# JPEG 压缩后：~120 KB

# 灰度图：1280x720x1 = 0.9 MB (PNG)
# JPEG 压缩后：~60 KB

# 优化效果：体积减半
```

### 4. ROI 优化（待实现）

```python
# ❌ 全屏搜索
result = cv2.matchTemplate(screenshot, template, method)

# ✅ ROI 搜索
roi = screenshot[y:y+h, x:x+w]
result = cv2.matchTemplate(roi, template, method)

# 优化效果：速度提升 5-10 倍
```

## 扩展性设计

### 1. 任务配置化

所有任务逻辑通过 JSON 配置，无需修改代码：

```json
{
  "task_name": "StartBattle",
  "recognition": {
    "method": "template_match",
    "template": "start_button.png",
    "roi": [100, 200, 300, 400],
    "threshold": 0.8
  },
  "action": {
    "type": "click",
    "target": "self"
  },
  "next": ["WaitBattleEnd"]
}
```

### 2. 插件化识别引擎

```python
class VisionEngine:
    def register_method(self, name: str, func: Callable):
        """注册自定义识别方法"""
        self.methods[name] = func

# 支持扩展：
# - template_match (模板匹配)
# - ocr (文字识别)
# - feature_match (特征匹配)
# - color_detect (颜色检测)
```

### 3. 多游戏支持

```
resources/
├─ templates/
│  ├─ zhangjian/      # 杖剑传说
│  ├─ arknights/      # 明日方舟
│  └─ genshin/        # 原神
└─ tasks/
   ├─ zhangjian/
   ├─ arknights/
   └─ genshin/
```

## 安全性

### 1. 本地通信

- ✅ 仅监听 127.0.0.1（不暴露到外网）
- ✅ CORS 限制（仅允许 localhost:1420）
- ✅ 无需认证（本地应用）

### 2. ADB 安全

- ✅ 仅连接本地模拟器
- ✅ 不执行危险命令（rm, su 等）
- ✅ 命令参数验证

### 3. 文件访问

- ✅ 限制在项目目录内
- ✅ 路径验证（防止目录遍历）

## 可维护性

### 1. 代码组织

```
清晰的模块划分：
├─ core/      # 核心逻辑
├─ utils/     # 工具函数
├─ models/    # 数据模型（待添加）
└─ api/       # API 路由（待拆分）
```

### 2. 日志系统

```python
# 统一的日志格式
[2025-01-01 12:00:00] [INFO] zat.adb: 已连接设备: 127.0.0.1:16384
[2025-01-01 12:00:01] [INFO] zat.task: 任务已启动: farming
[2025-01-01 12:00:02] [ERROR] zat.vision: 识别失败: 未找到模板
```

### 3. 类型提示

```python
# Python
async def screencap(self, gray: bool = False) -> bytes:
    ...

# TypeScript
interface LogMessage {
  type: 'log';
  level: 'info' | 'warning' | 'error';
  message: string;
}
```

## 测试策略

### 1. 单元测试（待添加）

```python
# test_adb_controller.py
async def test_auto_discover():
    adb = ADBController()
    device = await adb.auto_discover()
    assert device is not None
```

### 2. 集成测试

```python
# test_backend.py (已实现)
- 测试 ADB 连接
- 测试截图功能
- 测试灰度图
```

### 3. 端到端测试（待添加）

```typescript
// e2e/test_workflow.spec.ts
test('完整任务流程', async () => {
  await page.click('button:has-text("连接设备")');
  await page.click('button:has-text("启动任务")');
  // ...
});
```

## 部署方案

### 开发环境

```bash
# 终端 1: Python 后端
cd python-backend
source venv/bin/activate
python main.py

# 终端 2: Tauri 前端
pnpm tauri dev
```

### 生产环境（待实现）

```bash
# 打包 Python
pyinstaller --onefile main.py

# 打包 Tauri
pnpm tauri build

# 输出：
# - Windows: zat.exe
# - macOS: ZAT.app
# - Linux: zat.AppImage
```

## 未来优化方向

### Phase 1: 功能完善（1-2 周）
- [ ] 图像识别引擎
- [ ] 任务配置系统
- [ ] 状态机实现
- [ ] 错误处理和重试

### Phase 2: 性能优化（可选）
- [ ] Rust 重写核心模块
- [ ] 多线程识别
- [ ] 缓存优化

### Phase 3: 功能扩展（可选）
- [ ] OCR 文字识别
- [ ] 多游戏支持
- [ ] 云端配置同步
- [ ] 统计和报表

---

**架构设计原则：**
1. ✅ 简单优先（KISS）
2. ✅ 模块化（高内聚低耦合）
3. ✅ 可扩展（插件化）
4. ✅ 可维护（清晰的代码组织）
5. ✅ 高性能（关键路径优化）
