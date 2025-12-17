# ZAT - 仗剑传说自动化工具

Zhangjianchuanshuo Automation Tool

## 项目架构

```
ZAT (Desktop App)
├─ UI: Svelte + TypeScript
├─ Shell: Tauri (Rust)
└─ Backend: Python (FastAPI)
    ├─ ADB 控制
    ├─ 图像识别
    └─ 任务引擎
```

## 环境要求

### 开发环境

- Node.js 18+
- Rust 1.70+
- Python 3.10+
- ADB (Android Debug Bridge)

### macOS 安装

```bash
# 安装 Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 ADB
brew install android-platform-tools

# 安装 Python
brew install python@3.10

# 安装 Node.js
brew install node

# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## 快速开始

### 1. 安装依赖

```bash
# 前端依赖
pnpm install

# Python 依赖
cd python-backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cd ..
```

### 2. 启动开发环境

**终端 1：启动 Python 后端**

```bash
cd python-backend
source venv/bin/activate
python main.py
```

**终端 2：启动 Tauri 前端**

```bash
pnpm tauri dev
```

### 3. 连接模拟器

```bash
# 启动 MuMu 模拟器

# 连接 ADB
adb connect 127.0.0.1:16384

# 验证连接
adb devices
```

## 项目结构

```
zat/
├─ src/                      # Svelte 前端
│  ├─ routes/
│  │  └─ +page.svelte       # 主页面
│  └─ lib/
│     ├─ api.ts             # API 客户端
│     └─ components/        # UI 组件
│        ├─ TaskControl.svelte
│        ├─ LogViewer.svelte
│        ├─ StatusBar.svelte
│        └─ DebugPanel.svelte
│
├─ src-tauri/                # Tauri 壳
│  └─ src/
│     └─ main.rs
│
├─ python-backend/           # Python 后端
│  ├─ main.py               # FastAPI 入口
│  ├─ core/
│  │  ├─ adb_controller.py  # ADB 控制
│  │  └─ task_engine.py     # 任务引擎
│  └─ utils/
│     └─ logger.py          # 日志工具
│
└─ resources/                # 资源文件（待创建）
   ├─ templates/            # 图像模板
   └─ tasks/                # 任务配置
```

## API 端点

### HTTP

- `GET /` - 健康检查
- `POST /connect` - 连接设备
- `GET /status` - 获取状态
- `POST /start` - 启动任务
- `POST /stop` - 停止任务
- `GET /debug/screenshot` - 获取截图（Debug）

### WebSocket

- `/ws/log` - 日志流
- `/ws/state` - 状态流

## 开发计划

- [x] 基础框架搭建
- [x] ADB 控制器
- [x] WebSocket 日志流
- [x] 前端 UI
- [ ] 图像识别引擎
- [ ] 任务配置系统
- [ ] 状态机实现
- [ ] 完整任务流程

## 技术栈

- **前端**: Svelte 5 + TypeScript + Vite
- **桌面壳**: Tauri 2
- **后端**: Python 3.10 + FastAPI + Uvicorn
- **图像识别**: OpenCV
- **通信**: WebSocket + HTTP

## License

MIT
