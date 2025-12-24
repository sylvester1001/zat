<p align="center">
  <img src="static/favicon.png" width="80" height="80" alt="ZAT Logo">
</p>

<h1 align="center">ZAT</h1>

<p align="center">
  <b>杖剑传说自动化工具</b><br>
  <sub>Zhangjianchuanshuo Automation Tool</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-macOS%20|%20Windows-blue?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/Tauri-2.0-orange?style=flat-square" alt="Tauri">
  <img src="https://img.shields.io/badge/Svelte-5-red?style=flat-square" alt="Svelte">
  <img src="https://img.shields.io/badge/Python-3.10+-green?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square" alt="License">
</p>

<p align="center">
  <a href="#install">安装</a> •
  <a href="#usage">使用</a> •
  <a href="#features">特性</a> •
  <a href="#contributing">贡献</a> •
  <a href="./docs/">文档</a>
</p>

---

## What

一个桌面端游戏辅助工具，通过 ADB 连接 Android 模拟器，实现副本自动化、场景导航、状态监控等功能。

## Why

手动刷副本太累了。

## Install

### 方式一：下载即用 

前往 [Releases](https://github.com/your-repo/zat/releases) 下载对应平台的安装包：

| 平台 | 文件 |
|------|------|
| macOS | `ZAT_x.x.x_aarch64.dmg` / `ZAT_x.x.x_x64.dmg` |
| Windows | `ZAT_x.x.x_x64-setup.exe` |

### 方式二：从源码构建

```bash
# 1. 安装前端依赖
pnpm install

# 2. 安装后端依赖
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# 3. 启动后端
cd backend
source venv/bin/activate
python main.py

# 4. 启动前端
pnpm tauri dev
或
pnpm tauri build
```

## Usage

1. 启动 ZAT 应用
2. 启动 Android 模拟器（如 MuMu）
3. 在 GUI 中点击「连接设备」
4. 选择副本，设置次数，开刷

## Features

| 功能 | 描述 |
|------|------|
| 🎮 设备管理 | 自动发现并连接 Android 模拟器 |
| 🗺️ 场景导航 | 基于场景图的智能路径规划 |
| ⚔️ 副本自动化 | 支持单次 / 循环 / 无限刷本 |
| 📊 实时监控 | WebSocket 推送日志与状态 |
| 🖼️ 图像识别 | 模板匹配 + OCR 文字识别 |

## Tech Stack

```
┌─────────────────────────────────────┐
│           ZAT Desktop App           │
├─────────────────────────────────────┤
│  UI        │ Svelte 5 + TypeScript  │
│  Shell     │ Tauri 2 (Rust)         │
│  Backend   │ FastAPI + WebSocket    │
│  Vision    │ OpenCV + OCR           │
│  Control   │ ADB                    │
└─────────────────────────────────────┘
```

## Contributing

欢迎贡献代码！请先阅读以下文档：

| 文档 | 说明 |
|------|------|
| [开发指南](./docs/development.md) | 环境配置、项目结构、开发流程 |
| [API 文档](./docs/api.md) | HTTP / WebSocket 接口说明 |
| [架构设计](./docs/architecture.md) | 系统架构、模块设计、状态机 |

```bash
# Fork & Clone
git clone https://github.com/your-username/zat.git
cd zat

# 创建分支
git checkout -b feature/your-feature

# 提交 PR
```

## Roadmap

- [x] 基础框架搭建
- [x] ADB 控制器
- [x] WebSocket 日志流
- [x] 前端 UI
- [x] 图像识别引擎
- [x] 场景导航系统
- [x] 副本自动化
- [ ] 任务调度系统
- [ ] 自定义脚本

## License

[MIT](./LICENSE) © 2024

---

<p align="center">
  <sub>一起来冒险吧！ 🗡️</sub>
</p>
