BASE_SIZE = 1024
IMAGE_SIZE = 768
CROP_MODE = True
MIN_CROPS = 2
MAX_CROPS = 6
MAX_CONCURRENCY = 100
NUM_WORKERS = 64
PRINT_NUM_VIS_TOKENS = False
SKIP_REPEAT = True
MODEL_PATH = 'deepseek-ai/DeepSeek-OCR-2'

INPUT_PATH = './input_images/'
OUTPUT_PATH = './output_results/'

PROMPT = '<image>\n<|grounding|>Convert the document to markdown.'

from transformers import AutoTokenizer

TOKENIZER = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

BAIDU_OCR_CONFIG = {
    'APP_ID': '',
    'API_KEY': '0ooCxqxczLd5WrQWOB4oN3ar',
    'SECRET_KEY': 'Bh7JBNDIdwQ26Y6aothlQyM4WaGb9sgh',
    'use_baidu_ocr': True,
    'baidu_priority': 'fast'
}

DEEPSEEK_API_CONFIG = {
    'API_KEY': 'sk-8e51dda022ff4cb5a2fa20e3a6443839',
    'BASE_URL': 'https://api.deepseek.com',
    'use_deepseek_api': False
}

RECOGNITION_MODE = 'hybrid'
OPTIONS = {
    'contract': {
        'prompt': '<image>\n<|grounding|>Convert this contract document to markdown with proper formatting for legal text, clauses, and signatures.',
        'crop_mode': True,
        'min_crops': 3,
        'max_crops': 6
    },
    'bid': {
        'prompt': '<image>\n<|grounding|>Convert this bid document to markdown with proper formatting for tables, pricing, and technical specifications.',
        'crop_mode': True,
        'min_crops': 3,
        'max_crops': 6
    },
    'general': {
        'prompt': '<image>\n<|grounding|>Convert the document to markdown.',
        'crop_mode': True,
        'min_crops': 2,
        'max_crops': 6
    }
}
