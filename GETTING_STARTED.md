# ZAT 快速开始指南

## 项目已搭建完成 ✅

恭喜！ZAT 项目的基础架构已经搭建完成。

## 项目结构

```
zat/
├─ src/                          # Svelte 前端
│  ├─ routes/+page.svelte       # 主页面
│  ├─ lib/api.ts                # API 客户端
│  └─ lib/components/           # UI 组件
│     ├─ TaskControl.svelte     # 任务控制
│     ├─ LogViewer.svelte       # 日志查看
│     ├─ StatusBar.svelte       # 状态栏
│     └─ DebugPanel.svelte      # 调试面板
│
├─ src-tauri/                    # Tauri 桌面壳
│  └─ tauri.conf.json           # 配置文件
│
├─ python-backend/               # Python 后端
│  ├─ main.py                   # FastAPI 入口
│  ├─ core/
│  │  ├─ adb_controller.py      # ADB 控制器 ✅
│  │  └─ task_engine.py         # 任务引擎（基础）
│  ├─ utils/
│  │  └─ logger.py              # 日志工具 ✅
│  ├─ requirements.txt          # Python 依赖
│  ├─ start.sh                  # 启动脚本
│  └─ test_backend.py           # 测试脚本
│
├─ README.md                     # 项目说明
├─ DEVELOPMENT.md                # 开发指南
└─ GETTING_STARTED.md            # 本文件
```

## 已实现功能

### ✅ 后端（Python）

1. **ADB 控制器** (`adb_controller.py`)
   - 自动发现设备（支持 MuMu、BlueStacks 等）
   - 截图（使用 `exec-out`，最快方式）
   - 点击、滑动
   - 启动应用
   - 支持灰度图（体积减半）

2. **任务引擎** (`task_engine.py`)
   - 基础框架
   - 启动/停止任务
   - 状态管理

3. **日志系统** (`logger.py`)
   - WebSocket 实时广播
   - 多客户端支持
   - 自动清理断开连接

4. **FastAPI 服务** (`main.py`)
   - HTTP 端点：连接、状态、启动、停止、截图
   - WebSocket 端点：日志流、状态流
   - CORS 配置
   - 生命周期管理

### ✅ 前端（Svelte）

1. **API 客户端** (`api.ts`)
   - HTTP 请求封装
   - WebSocket 管理器
   - 自动重连

2. **UI 组件**
   - `TaskControl`: 连接设备、启动/停止任务
   - `LogViewer`: 实时日志显示
   - `StatusBar`: 状态监控
   - `DebugPanel`: 截图调试

3. **Tauri 配置**
   - 窗口大小：1200x800
   - 允许访问本地 API

## 下一步：启动项目

### 步骤 1: 安装 Python 依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 步骤 2: 测试 ADB 连接

```bash
# 确保模拟器已启动（MuMu）

# 连接 ADB
adb connect 127.0.0.1:16384

# 验证连接
adb devices

# 运行测试脚本
python test_backend.py
```

如果测试通过，你会看到：
```
==================================================
测试 ADB 控制器
==================================================

1. 初始化 ADB 控制器...
✓ ADB 控制器初始化成功

2. 自动发现设备...
✓ 已连接设备: 127.0.0.1:16384

3. 获取设备列表...
✓ 发现 1 个设备: ['127.0.0.1:16384']

4. 测试截图...
✓ 截图成功，大小: 123456 bytes (120.6 KB)
✓ 截图已保存到: test_screenshot.jpg

5. 测试灰度截图...
✓ 灰度截图成功，大小: 67890 bytes (66.3 KB)
  压缩率: 55.0%

==================================================
✓ 所有测试通过！
==================================================
```

### 步骤 3: 启动后端（终端 1）

```bash
cd backend
source venv/bin/activate
python main.py
```

你会看到：
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 步骤 4: 启动前端（终端 2）

```bash
# 在项目根目录
pnpm tauri dev
```

等待编译完成，Tauri 窗口会自动打开。

### 步骤 5: 使用 ZAT

1. 点击 **"连接设备"** 按钮
2. 等待连接成功，会显示设备地址
3. 点击 **"启动任务"** 按钮（目前是测试循环）
4. 查看日志流和状态更新
5. 在调试面板点击 **"刷新截图"** 查看模拟器画面
6. 点击 **"停止任务"** 停止

## 验证功能

### 1. 测试 HTTP API

打开浏览器访问：`http://127.0.0.1:8000/docs`

你会看到 FastAPI 自动生成的 API 文档，可以直接测试所有端点。

### 2. 测试截图

浏览器访问：`http://127.0.0.1:8000/debug/screenshot`

应该会下载一张 JPEG 截图。

### 3. 测试 WebSocket

打开浏览器 Console（F12），运行：

```javascript
// 测试日志流
const ws = new WebSocket('ws://127.0.0.1:8000/ws/log');
ws.onmessage = (e) => console.log(JSON.parse(e.data));

// 测试状态流
const ws2 = new WebSocket('ws://127.0.0.1:8000/ws/state');
ws2.onmessage = (e) => console.log(JSON.parse(e.data));
```

## 常见问题

### Q: 找不到 ADB？

```bash
# macOS
brew install android-platform-tools

# 验证
adb version
```

### Q: 连接不上模拟器？

```bash
# 1. 确认模拟器已启动
# 2. 手动连接
adb connect 127.0.0.1:16384

# 3. 如果还是不行，重启 ADB
adb kill-server
adb start-server
adb connect 127.0.0.1:16384
```

### Q: Python 依赖安装失败？

```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 前端连接不上后端？

1. 确认后端已启动（终端 1 有日志输出）
2. 浏览器访问 `http://127.0.0.1:8000` 应该返回 JSON
3. 检查防火墙设置

## 下一步开发

现在基础架构已经完成，接下来可以开发：

1. **图像识别引擎** - 模板匹配、OCR
2. **任务配置系统** - JSON 配置加载
3. **状态机** - 完整的任务流程
4. **游戏特定逻辑** - 杖剑传说的具体任务

详细开发指南请查看 `DEVELOPMENT.md`。

## 技术亮点

✅ **截图优化**
- 使用 `adb exec-out screencap -p`（最快方式）
- JPEG 压缩（质量 65）
- 可选灰度图（体积减半）
- HTTP 拉取式（按需获取）

✅ **实时通信**
- WebSocket 日志流（实时显示）
- WebSocket 状态流（1 秒更新）
- 自动重连机制

✅ **开发体验**
- FastAPI 自动生成 API 文档
- Svelte 热重载
- TypeScript 类型安全
- 详细的日志输出

## 项目状态

- ✅ 基础架构：100%
- ✅ ADB 控制：100%
- ✅ 前端 UI：100%
- ✅ 日志系统：100%
- 🚧 图像识别：0%
- 🚧 任务系统：20%
- 🚧 状态机：0%

预计完成时间：1-2 周（取决于游戏复杂度）

---

**祝开发顺利！** 🚀

如有问题，请查看 `DEVELOPMENT.md` 或提交 Issue。
