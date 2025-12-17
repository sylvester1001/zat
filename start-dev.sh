#!/bin/bash
# ZAT 开发环境启动脚本

echo "================================"
echo "  ZAT 开发环境启动"
echo "================================"
echo ""

# 检查 Python 虚拟环境
if [ ! -d "python-backend/venv" ]; then
    echo "❌ Python 虚拟环境不存在"
    echo ""
    echo "请先运行以下命令创建虚拟环境："
    echo "  cd python-backend"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 检查 ADB
if ! command -v adb &> /dev/null; then
    echo "⚠️  警告: 未找到 ADB"
    echo "请安装 ADB: brew install android-platform-tools"
    echo ""
fi

# 检查模拟器连接
echo "检查 ADB 设备..."
adb devices | grep -q "device$"
if [ $? -eq 0 ]; then
    echo "✓ 已连接 ADB 设备"
else
    echo "⚠️  警告: 未找到 ADB 设备"
    echo "请启动模拟器并运行: adb connect 127.0.0.1:16384"
fi

echo ""
echo "================================"
echo "  启动后端和前端"
echo "================================"
echo ""
echo "终端 1: Python 后端 (http://127.0.0.1:8000)"
echo "终端 2: Tauri 前端 (http://localhost:1420)"
echo ""
echo "请在两个终端分别运行："
echo ""
echo "终端 1:"
echo "  cd python-backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "终端 2:"
echo "  pnpm tauri dev"
echo ""
