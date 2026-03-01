#!/usr/bin/env python3
import os
import sys


def check_dependencies():
    print("=" * 60)
    print("DeepSeek-OCR 环境检查")
    print("=" * 60)
    
    issues = []
    
    print("\n1. 检查Python版本...")
    if sys.version_info >= (3, 8):
        print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    else:
        print(f"   ✗ Python版本过低: {sys.version}")
        issues.append("Python版本需要3.8+")
    
    print("\n2. 检查PyTorch...")
    try:
        import torch
        print(f"   ✓ PyTorch {torch.__version__}")
        if torch.cuda.is_available():
            print(f"   ✓ CUDA可用: {torch.cuda.get_device_name(0)}")
        else:
            print("   ⚠ CUDA不可用，将使用CPU (速度较慢)")
    except ImportError:
        print("   ✗ PyTorch未安装")
        issues.append("请安装: pip install torch torchvision")
    
    print("\n3. 检查Transformers...")
    try:
        import transformers
        print(f"   ✓ Transformers {transformers.__version__}")
    except ImportError:
        print("   ✗ Transformers未安装")
        issues.append("请安装: pip install transformers")
    
    print("\n4. 检查PIL/Pillow...")
    try:
        from PIL import Image
        print(f"   ✓ Pillow可用")
    except ImportError:
        print("   ✗ Pillow未安装")
        issues.append("请安装: pip install pillow")
    
    print("\n5. 检查百度OCR SDK...")
    try:
        from aip import AipOcr
        print("   ✓ 百度OCR SDK已安装")
    except ImportError:
        print("   ⚠ 百度OCR SDK未安装 (可选)")
        print("   如需使用百度OCR，请安装: pip install baidu-aip")
    
    print("\n6. 检查Flash Attention...")
    try:
        import flash_attn
        print("   ✓ Flash Attention已安装")
    except ImportError:
        print("   ⚠ Flash Attention未安装 (推荐)")
        print("   安装可提升性能: pip install flash-attn")
    
    print("\n7. 检查配置文件...")
    if os.path.exists('config_ocr.py'):
        print("   ✓ config_ocr.py存在")
        
        try:
            from config_ocr import (
                BAIDU_OCR_CONFIG, RECOGNITION_MODE, 
                INPUT_PATH, OUTPUT_PATH
            )
            print(f"   ✓ 识别模式: {RECOGNITION_MODE}")
            print(f"   ✓ 输入路径: {INPUT_PATH}")
            print(f"   ✓ 输出路径: {OUTPUT_PATH}")
            
            if BAIDU_OCR_CONFIG.get('use_baidu_ocr'):
                if 'YOUR_BAIDU' in str(BAIDU_OCR_CONFIG.get('APP_ID', '')):
                    print("   ⚠ 百度OCR配置未更新，请填入真实的API密钥")
                else:
                    print("   ✓ 百度OCR配置已设置")
        except Exception as e:
            print(f"   ✗ 配置文件读取失败: {e}")
            issues.append("请检查config_ocr.py配置")
    else:
        print("   ✗ config_ocr.py不存在")
        issues.append("配置文件缺失")
    
    print("\n8. 检查目录结构...")
    dirs_to_check = [
        INPUT_PATH,
        OUTPUT_PATH,
        os.path.join(INPUT_PATH, 'contracts'),
        os.path.join(INPUT_PATH, 'bids')
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"   ✓ {dir_path}")
        else:
            print(f"   ⚠ {dir_path} (将自动创建)")
    
    print("\n9. 检查核心文件...")
    files_to_check = [
        'hybrid_ocr_engine.py',
        'simple_ocr.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path}缺失")
            issues.append(f"核心文件缺失: {file_path}")
    
    print("\n" + "=" * 60)
    
    if issues:
        print("发现以下问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n请解决上述问题后再使用OCR功能")
        return False
    else:
        print("✓ 所有检查通过！环境配置正确")
        print("\n可以开始使用OCR功能:")
        print("  python simple_ocr.py contract <image_path>")
        print("  python simple_ocr.py bid <image_path>")
        return True


def create_directories():
    print("\n创建必要的目录结构...")
    
    from config_ocr import INPUT_PATH, OUTPUT_PATH
    
    dirs = [
        INPUT_PATH,
        OUTPUT_PATH,
        os.path.join(INPUT_PATH, 'contracts'),
        os.path.join(INPUT_PATH, 'bids'),
        os.path.join(OUTPUT_PATH, 'contracts'),
        os.path.join(OUTPUT_PATH, 'bids'),
        os.path.join(OUTPUT_PATH, 'single')
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✓ {dir_path}")


def test_ocr_engine():
    print("\n" + "=" * 60)
    print("测试OCR引擎")
    print("=" * 60)
    
    try:
        from hybrid_ocr_engine import HybridOCREngine
        
        print("\n初始化OCR引擎...")
        engine = HybridOCREngine()
        
        if engine.baidu_client:
            print("  ✓ 百度OCR引擎已加载")
        else:
            print("  ⚠ 百度OCR引擎未加载")
        
        if engine.deepseek_model:
            print(f"  ✓ DeepSeek-OCR引擎已加载 (设备: {engine.device})")
        else:
            print("  ⚠ DeepSeek-OCR引擎未加载")
        
        if not engine.baidu_client and not engine.deepseek_model:
            print("\n  ✗ 没有可用的OCR引擎")
            print("  请至少配置百度OCR或确保DeepSeek-OCR模型可下载")
            return False
        
        print("\n  ✓ OCR引擎测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ OCR引擎测试失败: {e}")
        return False


def main():
    print("\nDeepSeek-OCR 环境检查和测试工具\n")
    
    env_ok = check_dependencies()
    
    if env_ok:
        create_directories()
        test_ocr_engine()
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
