#!/usr/bin/env python3
"""
DeepSeek-OCR 使用示例
演示如何使用混合OCR引擎识别合同和投标书
"""

import os
from hybrid_ocr_engine import HybridOCREngine, save_results


def example_1_single_contract():
    """示例1：识别单个合同文档"""
    print("\n" + "="*60)
    print("示例1：识别单个合同文档")
    print("="*60)
    
    engine = HybridOCREngine()
    
    # 假设有一个合同图片
    contract_path = "./input_images/contracts/sample_contract.jpg"
    
    if os.path.exists(contract_path):
        result = engine.recognize_document(contract_path, doc_type='contract')
        
        if result['success']:
            print(f"\n✓ 识别成功！使用引擎: {result['engine']}")
            print(f"\n识别结果预览 (前200字符):")
            print(result['text'][:200] + "...")
            
            # 保存结果
            output_dir = './output_results/examples'
            os.makedirs(output_dir, exist_ok=True)
            
            with open(f'{output_dir}/example1_contract.txt', 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            print(f"\n完整结果已保存到: {output_dir}/example1_contract.txt")
        else:
            print(f"\n✗ 识别失败: {result.get('error')}")
    else:
        print(f"\n⚠ 示例文件不存在: {contract_path}")
        print("请将合同图片放到 ./input_images/contracts/ 目录下")


def example_2_single_bid():
    """示例2：识别单个投标书文档"""
    print("\n" + "="*60)
    print("示例2：识别单个投标书文档")
    print("="*60)
    
    engine = HybridOCREngine()
    
    # 假设有一个投标书图片
    bid_path = "./input_images/bids/sample_bid.jpg"
    
    if os.path.exists(bid_path):
        result = engine.recognize_document(bid_path, doc_type='bid')
        
        if result['success']:
            print(f"\n✓ 识别成功！使用引擎: {result['engine']}")
            print(f"\n识别结果预览 (前200字符):")
            print(result['text'][:200] + "...")
            
            # 保存结果
            output_dir = './output_results/examples'
            os.makedirs(output_dir, exist_ok=True)
            
            with open(f'{output_dir}/example2_bid.txt', 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            print(f"\n完整结果已保存到: {output_dir}/example2_bid.txt")
        else:
            print(f"\n✗ 识别失败: {result.get('error')}")
    else:
        print(f"\n⚠ 示例文件不存在: {bid_path}")
        print("请将投标书图片放到 ./input_images/bids/ 目录下")


def example_3_batch_contracts():
    """示例3：批量处理合同文档"""
    print("\n" + "="*60)
    print("示例3：批量处理合同文档")
    print("="*60)
    
    engine = HybridOCREngine()
    
    contracts_dir = "./input_images/contracts"
    
    if os.path.exists(contracts_dir):
        import glob
        
        # 查找所有合同图片
        contract_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            contract_files.extend(glob.glob(os.path.join(contracts_dir, ext)))
        
        if contract_files:
            print(f"\n找到 {len(contract_files)} 个合同文件")
            
            results = []
            for i, contract_file in enumerate(contract_files, 1):
                print(f"\n处理 {i}/{len(contract_files)}: {os.path.basename(contract_file)}")
                
                result = engine.recognize_document(contract_file, doc_type='contract')
                result['image_path'] = contract_file
                result['filename'] = os.path.basename(contract_file)
                results.append(result)
                
                if result['success']:
                    print(f"  ✓ 识别成功 (引擎: {result['engine']})")
                else:
                    print(f"  ✗ 识别失败: {result.get('error')}")
            
            # 保存批量结果
            save_results(results, './output_results/examples/batch_contracts')
            
            # 统计
            success_count = sum(1 for r in results if r.get('success'))
            print(f"\n批量处理完成: {success_count}/{len(results)} 成功")
        else:
            print(f"\n⚠ 在 {contracts_dir} 目录下没有找到图片文件")
    else:
        print(f"\n⚠ 目录不存在: {contracts_dir}")


def example_4_batch_bids():
    """示例4：批量处理投标书文档"""
    print("\n" + "="*60)
    print("示例4：批量处理投标书文档")
    print("="*60)
    
    engine = HybridOCREngine()
    
    bids_dir = "./input_images/bids"
    
    if os.path.exists(bids_dir):
        import glob
        
        # 查找所有投标书图片
        bid_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            bid_files.extend(glob.glob(os.path.join(bids_dir, ext)))
        
        if bid_files:
            print(f"\n找到 {len(bid_files)} 个投标书文件")
            
            results = []
            for i, bid_file in enumerate(bid_files, 1):
                print(f"\n处理 {i}/{len(bid_files)}: {os.path.basename(bid_file)}")
                
                result = engine.recognize_document(bid_file, doc_type='bid')
                result['image_path'] = bid_file
                result['filename'] = os.path.basename(bid_file)
                results.append(result)
                
                if result['success']:
                    print(f"  ✓ 识别成功 (引擎: {result['engine']})")
                else:
                    print(f"  ✗ 识别失败: {result.get('error')}")
            
            # 保存批量结果
            save_results(results, './output_results/examples/batch_bids')
            
            # 统计
            success_count = sum(1 for r in results if r.get('success'))
            print(f"\n批量处理完成: {success_count}/{len(results)} 成功")
        else:
            print(f"\n⚠ 在 {bids_dir} 目录下没有找到图片文件")
    else:
        print(f"\n⚠ 目录不存在: {bids_dir}")


def example_5_compare_engines():
    """示例5：对比不同引擎的识别效果"""
    print("\n" + "="*60)
    print("示例5：对比不同引擎的识别效果")
    print("="*60)
    
    # 这个示例需要同时配置百度OCR和DeepSeek-OCR
    from config_ocr import BAIDU_OCR_CONFIG
    
    if not BAIDU_OCR_CONFIG.get('use_baidu_ocr'):
        print("\n⚠ 此示例需要配置百度OCR")
        print("请在 config_ocr.py 中设置百度OCR的API密钥")
        return
    
    engine = HybridOCREngine()
    
    if not engine.baidu_client or not engine.deepseek_model:
        print("\n⚠ 此示例需要同时启用百度OCR和DeepSeek-OCR")
        return
    
    test_image = "./input_images/contracts/sample_contract.jpg"
    
    if os.path.exists(test_image):
        from PIL import Image, ImageOps
        
        image = Image.open(test_image)
        image = ImageOps.exif_transpose(image).convert('RGB')
        image = engine.enhance_image_quality(image)
        
        print("\n使用百度OCR识别...")
        baidu_result = engine.recognize_with_baidu(image)
        
        print("\n使用DeepSeek-OCR识别...")
        deepseek_result = engine.recognize_with_deepseek(image, 'contract')
        
        print("\n" + "-"*60)
        print("对比结果:")
        print("-"*60)
        
        if baidu_result.get('success'):
            print(f"\n百度OCR:")
            print(f"  状态: ✓ 成功")
            print(f"  文本长度: {len(baidu_result.get('text', ''))} 字符")
            print(f"  预览: {baidu_result.get('text', '')[:100]}...")
        else:
            print(f"\n百度OCR:")
            print(f"  状态: ✗ 失败")
            print(f"  错误: {baidu_result.get('error')}")
        
        if deepseek_result.get('success'):
            print(f"\nDeepSeek-OCR:")
            print(f"  状态: ✓ 成功")
            print(f"  文本长度: {len(deepseek_result.get('text', ''))} 字符")
            print(f"  预览: {deepseek_result.get('text', '')[:100]}...")
        else:
            print(f"\nDeepSeek-OCR:")
            print(f"  状态: ✗ 失败")
            print(f"  错误: {deepseek_result.get('error')}")
        
        print("\n" + "-"*60)
    else:
        print(f"\n⚠ 测试文件不存在: {test_image}")


def example_6_custom_prompt():
    """示例6：使用自定义Prompt进行识别"""
    print("\n" + "="*60)
    print("示例6：使用自定义Prompt进行识别")
    print("="*60)
    
    engine = HybridOCREngine()
    
    if not engine.deepseek_model:
        print("\n⚠ 此示例需要DeepSeek-OCR")
        return
    
    from config_ocr import OPTIONS
    
    # 修改合同识别的Prompt
    original_prompt = OPTIONS['contract']['prompt']
    print(f"\n原始合同Prompt:")
    print(f"  {original_prompt}")
    
    # 自定义Prompt示例
    custom_prompt = '<image>\n<|grounding|>Extract all key information from this contract including parties, dates, amounts, and important clauses. Format as structured markdown.'
    
    print(f"\n自定义Prompt:")
    print(f"  {custom_prompt}")
    
    # 临时修改配置
    OPTIONS['contract']['prompt'] = custom_prompt
    
    test_image = "./input_images/contracts/sample_contract.jpg"
    
    if os.path.exists(test_image):
        print(f"\n使用自定义Prompt识别...")
        result = engine.recognize_document(test_image, doc_type='contract')
        
        if result['success']:
            print(f"\n✓ 识别成功")
            print(f"\n识别结果预览:")
            print(result['text'][:300] + "...")
            
            # 恢复原始Prompt
            OPTIONS['contract']['prompt'] = original_prompt
        else:
            print(f"\n✗ 识别失败: {result.get('error')}")
    else:
        print(f"\n⚠ 测试文件不存在: {test_image}")


def main():
    print("\n" + "="*60)
    print("DeepSeek-OCR 使用示例")
    print("="*60)
    
    examples = {
        '1': ('识别单个合同', example_1_single_contract),
        '2': ('识别单个投标书', example_2_single_bid),
        '3': ('批量处理合同', example_3_batch_contracts),
        '4': ('批量处理投标书', example_4_batch_bids),
        '5': ('对比不同引擎', example_5_compare_engines),
        '6': ('使用自定义Prompt', example_6_custom_prompt),
        'all': ('运行所有示例', None),
        '0': ('退出', None)
    }
    
    print("\n可用示例:")
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")
    
    choice = input("\n请选择要运行的示例 (输入数字): ").strip()
    
    if choice == '0':
        print("\n退出")
        return
    elif choice == 'all':
        for key, (desc, func) in examples.items():
            if key not in ['all', '0'] and func:
                try:
                    func()
                except Exception as e:
                    print(f"\n✗ 示例执行出错: {e}")
    elif choice in examples and examples[choice][1]:
        try:
            examples[choice][1]()
        except Exception as e:
            print(f"\n✗ 示例执行出错: {e}")
    else:
        print(f"\n✗ 无效的选择: {choice}")
    
    print("\n" + "="*60)
    print("示例执行完成")
    print("="*60)


if __name__ == "__main__":
    main()
