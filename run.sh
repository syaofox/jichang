#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

echo "启动 Web UI..."
echo "打开 http://localhost:8000"
.venv/bin/python api/main.py
