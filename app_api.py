#!/usr/bin/env python3
"""
简化版OCR Web应用 - 使用DeepSeek API
无需本地模型，直接调用API
"""
import os
import base64
import io
import json
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('./output_results/api', exist_ok=True)

# DeepSeek API配置
DEEPSEEK_API_KEY = 'sk-8e51dda022ff4cb5a2fa20e3a6443839'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'

# 文档类型配置
DOC_TYPES = {
    'general': {
        'name': '通用文档',
        'prompt': '请识别这张图片中的文字内容，并以Markdown格式输出。保留原有的段落和格式。'
    },
    'contract': {
        'name': '合同文档',
        'prompt': '请识别这张合同文档的内容，并以Markdown格式输出。保留条款编号、金额、日期等关键信息，以及签名和盖章的位置标记。'
    },
    'bid': {
        'name': '投标书',
        'prompt': '请识别这张投标书的内容，并以Markdown格式输出。保留表格结构、价格信息、技术规格等内容。'
    }
}

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

def image_to_base64(image_path):
    """将图片转为base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def recognize_with_deepseek_api(image_path, doc_type='general'):
    """使用DeepSeek API识别"""
    try:
        config = DOC_TYPES.get(doc_type, DOC_TYPES['general'])
        
        # 将图片转为base64
        image_base64 = image_to_base64(image_path)
        
        # 构建请求
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-vl-7b',
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': config['prompt']
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{image_base64}'
                            }
                        }
                    ]
                }
            ],
            'temperature': 0.0,
            'max_tokens': 4096
        }
        
        # 调用多模态API
        response = requests.post(
            f'{DEEPSEEK_BASE_URL}/v1/multimodal/chat/completions',
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result['choices'][0]['message']['content']
            return {
                'success': True,
                'text': text,
                'doc_type': doc_type,
                'doc_type_name': config['name'],
                'model': 'deepseek-chat'
            }
        else:
            return {
                'success': False,
                'error': f'API调用失败: {response.status_code} - {response.text}'
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    # 测试API是否可用
    try:
        headers = {'Authorization': f'Bearer {DEEPSEEK_API_KEY}'}
        response = requests.get(f'{DEEPSEEK_BASE_URL}/models', headers=headers, timeout=10)
        api_available = response.status_code == 200
    except:
        api_available = False
    
    return jsonify({
        'status': 'ok',
        'api_available': api_available,
        'mode': 'DeepSeek API',
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
        
        # 使用API识别
        result = recognize_with_deepseek_api(filepath, doc_type)
        
        result['filename'] = saved_filename
        result['timestamp'] = timestamp
        
        if result.get('success'):
            # 保存结果
            output_dir = './output_results/api'
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
        output_dir = './output_results/api'
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
    print("简化版OCR Web应用 (DeepSeek API)")
    print("=" * 60)
    print(f"\n服务器地址: http://localhost:5002")
    print(f"上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"输出目录: ./output_results/api")
    print(f"\n使用DeepSeek API进行识别")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5002, debug=False)
