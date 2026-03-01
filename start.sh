#!/bin/bash

echo "=========================================="
echo "OCR Web 应用启动脚本"
echo "=========================================="
echo ""

echo "检查Python环境..."
python3 --version

echo ""
echo "安装依赖..."
pip install -r requirements_web.txt

echo ""
echo "创建必要的目录..."
mkdir -p uploads
mkdir -p output_results/web
mkdir -p templates

echo ""
echo "=========================================="
echo "启动Web服务器..."
echo "=========================================="
echo ""
echo "服务器地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo ""

python3 start_web.py
