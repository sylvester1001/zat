# 开发指南

## 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | 18+ | 前端构建 |
| Rust | 1.70+ | Tauri 编译 |
| Python | 3.10+ | 后端运行 |
| ADB | latest | 设备控制 |

## macOS 环境安装

```bash
# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 依赖
brew install android-platform-tools python@3.10 node
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## 项目结构

```
zat/
├── src/                    # Svelte 前端
│   ├── routes/            # 页面路由
│   └── lib/               # 组件 & API
│
├── src-tauri/             # Tauri 壳 (Rust)
│   └── src/main.rs
│
├── backend/               # Python 后端
│   ├── main.py           # FastAPI 入口
│   ├── core/             # 核心模块
│   │   ├── adb_controller.py    # ADB 控制
│   │   ├── task_engine.py       # 任务引擎
│   │   ├── game_navigator.py    # 场景导航
│   │   ├── dungeon_runner.py    # 副本执行
│   │   ├── image_matcher.py     # 图像识别
│   │   └── scene_graph.py       # 场景图
│   └── utils/            # 工具函数
│
└── static/               # 静态资源
```

## 开发流程

### 1. 安装依赖

```bash
# 前端
pnpm install

# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动开发服务

**终端 1 - Python 后端**
```bash
cd backend
source venv/bin/activate
python main.py
```

**终端 2 - Tauri 前端**
```bash
pnpm tauri dev
```

### 3. 连接模拟器

```bash
# 启动 MuMu 模拟器后
adb connect 127.0.0.1:16384
adb devices  # 验证连接
```

## 构建发布

```bash
pnpm tauri build
```

产物位于 `src-tauri/target/release/bundle/`

## 调试技巧

### 截图调试
```bash
curl http://127.0.0.1:8000/debug/screenshot --output screen.jpg
```

### OCR 调试
```bash
# 查看所有识别文字
curl http://127.0.0.1:8000/debug/ocr

# 查找特定文字
curl "http://127.0.0.1:8000/debug/ocr?target=开始"
```

### 日志监控
WebSocket 连接 `ws://127.0.0.1:8000/ws/log` 获取实时日志流
