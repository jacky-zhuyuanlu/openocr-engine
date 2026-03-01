#!/usr/bin/env python3
"""
简化版OCR Web应用 - 仅使用DeepSeek-OCR
"""
import os
import base64
import io
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import uuid

# 设置HuggingFace镜像源（国内加速）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 导入模型包装器（修复CUDA硬编码问题）
import model_wrapper

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    print("Warning: Transformers not available. Install with: pip install transformers torch")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('./output_results/simple', exist_ok=True)

# DeepSeek-OCR配置
MODEL_PATH = 'deepseek-ai/DeepSeek-OCR-2'
BASE_SIZE = 1024
IMAGE_SIZE = 768

# 文档类型配置
DOC_TYPES = {
    'general': {
        'name': '通用文档',
        'prompt': '<image>\n<|grounding|>Convert the document to markdown.'
    },
    'contract': {
        'name': '合同文档',
        'prompt': '<image>\n<|grounding|>Convert this contract document to markdown with proper formatting for legal text, clauses, and signatures.'
    },
    'bid': {
        'name': '投标书',
        'prompt': '<image>\n<|grounding|>Convert this bid document to markdown with proper formatting for tables, pricing, and technical specifications.'
    }
}

# 全局模型实例
ocr_model = None
ocr_tokenizer = None

def init_model():
    """初始化DeepSeek-OCR模型"""
    global ocr_model, ocr_tokenizer
    
    if not DEEPSEEK_AVAILABLE:
        return False
    
    if ocr_model is None:
        try:
            print("正在加载DeepSeek-OCR模型...")
            
            # 强制使用CPU（MPS有兼容性问题）
            device = 'cpu'
            torch_dtype = torch.float32
            
            print(f"使用设备: {device}")
            
            ocr_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
            ocr_model = AutoModel.from_pretrained(
                MODEL_PATH,
                trust_remote_code=True,
                use_safetensors=True,
                torch_dtype=torch_dtype
            )
            ocr_model = ocr_model.eval().to(device)
            print(f"模型加载完成！使用设备: {device}")
            return True
        except Exception as e:
            print(f"模型加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image_path):
    """预处理图片"""
    try:
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
        
        # 增强图像质量
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        return image.convert('RGB')
    except Exception as e:
        print(f"图片预处理失败: {e}")
        return None

def recognize_with_deepseek(image_path, doc_type='general'):
    """使用DeepSeek-OCR识别"""
    if not ocr_model:
        return {'success': False, 'error': '模型未加载'}
    
    try:
        config = DOC_TYPES.get(doc_type, DOC_TYPES['general'])
        prompt = config['prompt']
        
        print(f"开始识别图片: {image_path}")
        print(f"文档类型: {config['name']}")
        
        # 调用模型推理（模型已在正确的设备上）
        # 使用eval_mode=True获取返回结果
        result = ocr_model.infer(
            ocr_tokenizer,
            prompt=prompt,
            image_file=image_path,
            output_path='./output_results/simple',
            base_size=BASE_SIZE,
            image_size=IMAGE_SIZE,
            crop_mode=True,
            save_results=False,
            eval_mode=True
        )
        
        print(f"识别结果: {result}")
        
        # 检查结果
        if result is None:
            return {'success': False, 'error': '模型返回空结果'}
        
        if isinstance(result, str):
            text = result
        else:
            text = str(result)
        
        return {
            'success': True,
            'text': text,
            'doc_type': doc_type,
            'doc_type_name': config['name']
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'model_loaded': ocr_model is not None,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu' if DEEPSEEK_AVAILABLE else 'none',
        'available_doc_types': list(DOC_TYPES.keys())
    })

@app.route('/api/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
    
    doc_type = request.form.get('doc_type', 'general')
    
    if doc_type not in DOC_TYPES:
        return jsonify({'success': False, 'error': '不支持的文档类型'}), 400
    
    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        # 预处理图片
        image = preprocess_image(filepath)
        if image is None:
            return jsonify({'success': False, 'error': '图片预处理失败'}), 500
        
        # 保存预处理后的图片
        image.save(filepath, 'JPEG', quality=95)
        
        # 识别
        result = recognize_with_deepseek(filepath, doc_type)
        
        result['filename'] = saved_filename
        result['timestamp'] = timestamp
        
        if result.get('success'):
            # 保存结果
            output_dir = './output_results/simple'
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = os.path.splitext(saved_filename)[0]
            
            # 保存文本
            text_path = os.path.join(output_dir, f"{base_name}.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            # 保存JSON
            json_path = os.path.join(output_dir, f"{base_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            result['text_file'] = text_path
            result['json_file'] = json_path
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        output_dir = './output_results/simple'
        if not os.path.exists(output_dir):
            return jsonify({'success': True, 'history': []})
        
        history = []
        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        
        for json_file in sorted(json_files, reverse=True)[:20]:
            json_path = os.path.join(output_dir, json_file)
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                history.append({
                    'filename': data.get('filename', ''),
                    'doc_type': data.get('doc_type', 'general'),
                    'doc_type_name': data.get('doc_type_name', '通用文档'),
                    'timestamp': data.get('timestamp', ''),
                    'success': data.get('success', False),
                    'text_preview': data.get('text', '')[:200] + '...' if len(data.get('text', '')) > 200 else data.get('text', '')
                })
            except:
                continue
        
        return jsonify({'success': True, 'history': history})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/doc_types', methods=['GET'])
def get_doc_types():
    return jsonify({
        'success': True,
        'doc_types': {k: v['name'] for k, v in DOC_TYPES.items()}
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("=" * 60)
    print("简化版OCR Web应用 (仅DeepSeek-OCR)")
    print("=" * 60)
    
    # 初始化模型
    if init_model():
        print("✓ 模型加载成功")
    else:
        print("✗ 模型加载失败，请检查依赖")
        print("  运行: pip install transformers torch pillow")
    
    print(f"\n服务器地址: http://localhost:5001")
    print(f"上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"输出目录: ./output_results/simple")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5003, debug=False)
