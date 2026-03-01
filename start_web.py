#!/usr/bin/env python3
import os
import sys


def check_flask():
    try:
        import flask
        print("✓ Flask 已安装")
        return True
    except ImportError:
        print("✗ Flask 未安装")
        print("请运行: pip install flask")
        return False


def check_dependencies():
    print("检查依赖...")
    
    deps_ok = True
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
    except ImportError:
        print("✗ PyTorch 未安装")
        deps_ok = False
    
    try:
        import transformers
        print(f"✓ Transformers {transformers.__version__}")
    except ImportError:
        print("✗ Transformers 未安装")
        deps_ok = False
    
    try:
        from PIL import Image
        print("✓ Pillow 已安装")
    except ImportError:
        print("✗ Pillow 未安装")
        deps_ok = False
    
    try:
        from aip import AipOcr
        print("✓ 百度OCR SDK 已安装")
    except ImportError:
        print("⚠ 百度OCR SDK 未安装 (可选)")
    
    try:
        import flask
        print("✓ Flask 已安装")
    except ImportError:
        print("✗ Flask 未安装")
        deps_ok = False
    
    return deps_ok


def create_directories():
    print("\n创建必要的目录...")
    
    dirs = [
        './uploads',
        './output_results/web',
        './templates'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✓ {dir_path}")


def check_config():
    print("\n检查配置文件...")
    
    try:
        from config_ocr import BAIDU_OCR_CONFIG, DEEPSEEK_API_CONFIG
        
        if BAIDU_OCR_CONFIG.get('use_baidu_ocr'):
            if 'YOUR_BAIDU' in str(BAIDU_OCR_CONFIG.get('API_KEY', '')):
                print("  ⚠ 百度OCR配置未更新")
            else:
                print("  ✓ 百度OCR配置已设置")
        
        print("  ✓ 配置文件检查通过")
        return True
    except Exception as e:
        print(f"  ✗ 配置文件读取失败: {e}")
        return False


def main():
    print("=" * 60)
    print("OCR Web 应用启动脚本")
    print("=" * 60)
    print()
    
    if not check_dependencies():
        print("\n请先安装缺失的依赖:")
        print("  pip install -r requirements_web.txt")
        sys.exit(1)
    
    if not check_config():
        print("\n请检查 config_ocr.py 配置文件")
        sys.exit(1)
    
    create_directories()
    
    print("\n" + "=" * 60)
    print("所有检查通过！")
    print("=" * 60)
    print("\n启动 Web 服务器...")
    print()
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"\n启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
