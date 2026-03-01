#!/usr/bin/env python3
"""
测试OCR Web应用
"""
import requests
import base64
import json
import os


BASE_URL = 'http://localhost:5000'


def test_health():
    print("=" * 60)
    print("测试1: 健康检查")
    print("=" * 60)
    
    try:
        response = requests.get(f'{BASE_URL}/api/health')
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✓ 健康检查通过")
            return True
        else:
            print("✗ 健康检查失败")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_config():
    print("\n" + "=" * 60)
    print("测试2: 获取配置")
    print("=" * 60)
    
    try:
        response = requests.get(f'{BASE_URL}/api/config')
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✓ 配置获取成功")
            return True
        else:
            print("✗ 配置获取失败")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_history():
    print("\n" + "=" * 60)
    print("测试3: 获取历史记录")
    print("=" * 60)
    
    try:
        response = requests.get(f'{BASE_URL}/api/history')
        data = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"历史记录数量: {len(data.get('history', []))}")
        
        if response.status_code == 200:
            print("✓ 历史记录获取成功")
            return True
        else:
            print("✗ 历史记录获取失败")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_recognize_file(image_path):
    print("\n" + "=" * 60)
    print("测试4: 文件上传识别")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"✗ 测试图片不存在: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'doc_type': 'general',
                'engine': 'auto'
            }
            
            print(f"上传文件: {image_path}")
            print(f"文档类型: general")
            print(f"识别引擎: auto")
            
            response = requests.post(f'{BASE_URL}/api/recognize', files=files, data=data)
            result = response.json()
        
        print(f"\n状态码: {response.status_code}")
        
        if result.get('success'):
            print(f"✓ 识别成功")
            print(f"引擎: {result.get('engine')}")
            print(f"时间戳: {result.get('timestamp')}")
            print(f"文本长度: {len(result.get('text', ''))}")
            print(f"\n识别结果预览:")
            print(result.get('text', '')[:200] + "...")
            return True
        else:
            print(f"✗ 识别失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_recognize_base64(image_path):
    print("\n" + "=" * 60)
    print("测试5: Base64识别")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"✗ 测试图片不存在: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            'image': f'data:image/jpeg;base64,{image_data}',
            'doc_type': 'general'
        }
        
        print(f"上传文件: {image_path}")
        print(f"文档类型: general")
        
        response = requests.post(
            f'{BASE_URL}/api/recognize_base64',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        result = response.json()
        
        print(f"\n状态码: {response.status_code}")
        
        if result.get('success'):
            print(f"✓ 识别成功")
            print(f"引擎: {result.get('engine')}")
            print(f"时间戳: {result.get('timestamp')}")
            print(f"文本长度: {len(result.get('text', ''))}")
            return True
        else:
            print(f"✗ 识别失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("OCR Web 应用测试")
    print("=" * 60)
    print(f"服务器地址: {BASE_URL}")
    print()
    
    results = []
    
    results.append(('健康检查', test_health()))
    results.append(('获取配置', test_config()))
    results.append(('历史记录', test_history()))
    
    test_image = './input_images/contracts/sample_contract.jpg'
    if os.path.exists(test_image):
        results.append(('文件上传识别', test_recognize_file(test_image)))
        results.append(('Base64识别', test_recognize_base64(test_image)))
    else:
        print("\n⚠ 跳过识别测试（测试图片不存在）")
        print(f"  请将测试图片放到: {test_image}")
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠ {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
