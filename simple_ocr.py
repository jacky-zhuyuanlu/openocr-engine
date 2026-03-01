import os
from hybrid_ocr_engine import HybridOCREngine, save_results


def recognize_single_image(image_path: str, doc_type: str = 'general'):
    engine = HybridOCREngine()
    
    print(f"Recognizing {doc_type} document: {image_path}")
    result = engine.recognize_document(image_path, doc_type)
    
    if result.get('success'):
        print(f"\n✓ Recognition successful using {result.get('engine', 'unknown')} engine")
        print(f"\n--- Extracted Text ---\n")
        print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])
        print(f"\n--- End of Text ---\n")
        
        output_dir = './output_results/single'
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        print(f"Result saved to: {output_path}")
    else:
        print(f"✗ Recognition failed: {result.get('error', 'Unknown error')}")
    
    return result


def recognize_contract(image_path: str):
    return recognize_single_image(image_path, 'contract')


def recognize_bid(image_path: str):
    return recognize_single_image(image_path, 'bid')


def batch_process_contracts(input_dir: str):
    engine = HybridOCREngine()
    print(f"Batch processing contracts from: {input_dir}")
    
    if not os.path.exists(input_dir):
        print(f"Directory not found: {input_dir}")
        return []
    
    results = engine.batch_recognize(input_dir, 'contract')
    save_results(results, './output_results/contracts')
    
    return results


def batch_process_bids(input_dir: str):
    engine = HybridOCREngine()
    print(f"Batch processing bids from: {input_dir}")
    
    if not os.path.exists(input_dir):
        print(f"Directory not found: {input_dir}")
        return []
    
    results = engine.batch_recognize(input_dir, 'bid')
    save_results(results, './output_results/bids')
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python simple_ocr.py <image_path> [doc_type]")
        print("  python simple_ocr.py contract <image_path>")
        print("  python simple_ocr.py bid <image_path>")
        print("  python simple_ocr.py batch-contracts <input_dir>")
        print("  python simple_ocr.py batch-bids <input_dir>")
        print("\nDoc types: contract, bid, general (default)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'contract' and len(sys.argv) >= 3:
        recognize_contract(sys.argv[2])
    elif command == 'bid' and len(sys.argv) >= 3:
        recognize_bid(sys.argv[2])
    elif command == 'batch-contracts' and len(sys.argv) >= 3:
        batch_process_contracts(sys.argv[2])
    elif command == 'batch-bids' and len(sys.argv) >= 3:
        batch_process_bids(sys.argv[2])
    elif os.path.exists(command):
        doc_type = sys.argv[2] if len(sys.argv) >= 3 else 'general'
        recognize_single_image(command, doc_type)
    else:
        print(f"Unknown command or file not found: {command}")
