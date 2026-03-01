import os
import re
import json
import time
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageOps
import numpy as np
import torch
from tqdm import tqdm

try:
    from aip import AipOcr
    BAIDU_AVAILABLE = True
except ImportError:
    BAIDU_AVAILABLE = False
    print("Warning: Baidu OCR SDK not available. Install with: pip install baidu-aip")

try:
    from transformers import AutoTokenizer, AutoModel
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    print("Warning: Transformers not available. Install with: pip install transformers")

from config_ocr import (
    BASE_SIZE, IMAGE_SIZE, CROP_MODE, MIN_CROPS, MAX_CROPS,
    MODEL_PATH, INPUT_PATH, OUTPUT_PATH, BAIDU_OCR_CONFIG,
    RECOGNITION_MODE, OPTIONS
)


class HybridOCREngine:
    def __init__(self):
        self.baidu_client = None
        self.deepseek_model = None
        self.deepseek_tokenizer = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self._init_baidu_ocr()
        self._init_deepseek_ocr()
        
    def _init_baidu_ocr(self):
        if BAIDU_AVAILABLE and BAIDU_OCR_CONFIG.get('use_baidu_ocr', False):
            try:
                self.baidu_client = AipOcr(
                    BAIDU_OCR_CONFIG['APP_ID'],
                    BAIDU_OCR_CONFIG['API_KEY'],
                    BAIDU_OCR_CONFIG['SECRET_KEY']
                )
                print("Baidu OCR initialized successfully")
            except Exception as e:
                print(f"Baidu OCR initialization failed: {e}")
                self.baidu_client = None
    
    def _init_deepseek_ocr(self):
        if DEEPSEEK_AVAILABLE:
            try:
                self.deepseek_tokenizer = AutoTokenizer.from_pretrained(
                    MODEL_PATH, trust_remote_code=True
                )
                self.deepseek_model = AutoModel.from_pretrained(
                    MODEL_PATH,
                    _attn_implementation='flash_attention_2',
                    trust_remote_code=True,
                    use_safetensors=True
                )
                self.deepseek_model = self.deepseek_model.eval().to(self.device).to(torch.bfloat16)
                print(f"DeepSeek OCR initialized on {self.device}")
            except Exception as e:
                print(f"DeepSeek OCR initialization failed: {e}")
                self.deepseek_model = None
    
    def preprocess_image(self, image_path: str) -> Image.Image:
        try:
            image = Image.open(image_path)
            corrected_image = ImageOps.exif_transpose(image)
            return corrected_image.convert('RGB')
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def enhance_image_quality(self, image: Image.Image) -> Image.Image:
        from PIL import ImageEnhance
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def recognize_with_baidu(self, image: Image.Image) -> Dict:
        if not self.baidu_client:
            return {'error': 'Baidu OCR not available'}
        
        try:
            img_byte_arr = np.array(image)
            img_byte_arr = img_byte_arr.tobytes()
            
            result = self.baidu_client.general(img_byte_arr)
            
            if 'words_result' in result:
                return {
                    'success': True,
                    'text': '\n'.join([item['words'] for item in result['words_result']]),
                    'details': result['words_result'],
                    'confidence': result.get('log_id', 0)
                }
            else:
                return {'success': False, 'error': result.get('error_msg', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def recognize_with_deepseek(self, image: Image.Image, doc_type: str = 'general') -> Dict:
        if not self.deepseek_model:
            return {'error': 'DeepSeek OCR not available'}
        
        try:
            option = OPTIONS.get(doc_type, OPTIONS['general'])
            prompt = option['prompt']
            
            temp_image_path = '/tmp/temp_ocr_image.jpg'
            image.save(temp_image_path, 'JPEG')
            
            result = self.deepseek_model.infer(
                self.deepseek_tokenizer,
                prompt=prompt,
                image_file=temp_image_path,
                output_path=OUTPUT_PATH,
                base_size=BASE_SIZE,
                image_size=IMAGE_SIZE,
                crop_mode=option['crop_mode'],
                save_results=False
            )
            
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
            return {
                'success': True,
                'text': result,
                'model': 'DeepSeek-OCR-2'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def merge_results(self, baidu_result: Dict, deepseek_result: Dict) -> str:
        if not baidu_result.get('success') and not deepseek_result.get('success'):
            return "OCR failed for both engines"
        
        if not baidu_result.get('success'):
            return deepseek_result.get('text', '')
        
        if not deepseek_result.get('success'):
            return baidu_result.get('text', '')
        
        baidu_text = baidu_result.get('text', '')
        deepseek_text = deepseek_result.get('text', '')
        
        if len(deepseek_text) > len(baidu_text) * 0.8:
            return deepseek_text
        else:
            return baidu_text
    
    def recognize_document(self, image_path: str, doc_type: str = 'general') -> Dict:
        image = self.preprocess_image(image_path)
        if image is None:
            return {'success': False, 'error': 'Failed to load image'}
        
        image = self.enhance_image_quality(image)
        
        baidu_result = None
        deepseek_result = None
        
        if RECOGNITION_MODE == 'baidu':
            baidu_result = self.recognize_with_baidu(image)
            if baidu_result.get('success'):
                return {
                    'success': True,
                    'text': baidu_result['text'],
                    'engine': 'Baidu',
                    'details': baidu_result
                }
        
        elif RECOGNITION_MODE == 'deepseek':
            deepseek_result = self.recognize_with_deepseek(image, doc_type)
            if deepseek_result.get('success'):
                return {
                    'success': True,
                    'text': deepseek_result['text'],
                    'engine': 'DeepSeek',
                    'details': deepseek_result
                }
        
        elif RECOGNITION_MODE == 'hybrid':
            if BAIDU_OCR_CONFIG.get('baidu_priority') == 'fast':
                baidu_result = self.recognize_with_baidu(image)
                if baidu_result.get('success'):
                    return {
                        'success': True,
                        'text': baidu_result['text'],
                        'engine': 'Baidu (fast)',
                        'details': baidu_result
                    }
            
            deepseek_result = self.recognize_with_deepseek(image, doc_type)
            
            if baidu_result is None:
                baidu_result = self.recognize_with_baidu(image)
            
            merged_text = self.merge_results(baidu_result, deepseek_result)
            
            return {
                'success': True,
                'text': merged_text,
                'engine': 'Hybrid',
                'baidu_result': baidu_result,
                'deepseek_result': deepseek_result
            }
        
        return {'success': False, 'error': 'No OCR engine available'}
    
    def batch_recognize(self, image_dir: str, doc_type: str = 'general') -> List[Dict]:
        if not os.path.exists(image_dir):
            print(f"Directory not found: {image_dir}")
            return []
        
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            image_files.extend(glob.glob(os.path.join(image_dir, ext)))
        
        if not image_files:
            print(f"No images found in {image_dir}")
            return []
        
        results = []
        for image_file in tqdm(image_files, desc=f"Processing {doc_type} documents"):
            result = self.recognize_document(image_file, doc_type)
            result['image_path'] = image_file
            result['filename'] = os.path.basename(image_file)
            results.append(result)
        
        return results


def save_results(results: List[Dict], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    for result in results:
        if result.get('success'):
            filename = result['filename']
            base_name = os.path.splitext(filename)[0]
            
            text_output_path = os.path.join(output_dir, f"{base_name}.txt")
            with open(text_output_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            json_output_path = os.path.join(output_dir, f"{base_name}.json")
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
    
    summary_path = os.path.join(output_dir, 'summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        summary = {
            'total': len(results),
            'successful': sum(1 for r in results if r.get('success')),
            'failed': sum(1 for r in results if not r.get('success')),
            'engines_used': list(set(r.get('engine', 'unknown') for r in results))
        }
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"Results saved to {output_dir}")
    print(f"Summary: {summary['successful']}/{summary['total']} successful")


def main():
    import glob
    
    engine = HybridOCREngine()
    
    contract_dir = os.path.join(INPUT_PATH, 'contracts')
    bid_dir = os.path.join(INPUT_PATH, 'bids')
    
    if os.path.exists(contract_dir):
        print(f"\nProcessing contracts from {contract_dir}...")
        contract_results = engine.batch_recognize(contract_dir, 'contract')
        save_results(contract_results, os.path.join(OUTPUT_PATH, 'contracts'))
    
    if os.path.exists(bid_dir):
        print(f"\nProcessing bids from {bid_dir}...")
        bid_results = engine.batch_recognize(bid_dir, 'bid')
        save_results(bid_results, os.path.join(OUTPUT_PATH, 'bids'))
    
    if not os.path.exists(contract_dir) and not os.path.exists(bid_dir):
        print(f"\nProcessing general documents from {INPUT_PATH}...")
        general_results = engine.batch_recognize(INPUT_PATH, 'general')
        save_results(general_results, OUTPUT_PATH)


if __name__ == "__main__":
    main()
