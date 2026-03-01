#!/bin/bash

echo "=========================================="
echo "DeepSeek-OCR 简化版 Web 应用"
echo "=========================================="
echo ""

echo "检查Python环境..."
python3 --version

echo ""
echo "安装必要依赖..."
pip3 install flask pillow transformers torch --quiet

echo ""
echo "创建必要的目录..."
mkdir -p uploads
mkdir -p output_results/simple
mkdir -p templates

echo ""
echo "=========================================="
echo "启动Web服务器..."
echo "=========================================="
echo ""
echo "服务器地址: http://localhost:5001"
echo "按 Ctrl+C 停止服务器"
echo ""
echo "注意: 首次运行会自动下载DeepSeek-OCR模型(约3GB)"
echo "      请确保网络连接稳定"
echo ""

python3 app_simple.py
