#!/bin/bash
# ZAT Python Backend 启动脚本

cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "错误: 虚拟环境不存在，请先运行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 启动服务
echo "启动 ZAT Backend..."
python main.py
