import os
import base64
import io
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

from hybrid_ocr_engine import HybridOCREngine
from config_ocr import BAIDU_OCR_CONFIG, DEEPSEEK_API_CONFIG

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('./output_results/web', exist_ok=True)

ocr_engine = HybridOCREngine()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def image_to_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'baidu_ocr': BAIDU_OCR_CONFIG.get('use_baidu_ocr', False),
        'deepseek_ocr': ocr_engine.deepseek_model is not None,
        'deepseek_api': DEEPSEEK_API_CONFIG.get('use_deepseek_api', False)
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
    engine = request.form.get('engine', 'auto')
    
    try:
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        result = ocr_engine.recognize_document(filepath, doc_type)
        
        result['image_path'] = filepath
        result['filename'] = saved_filename
        result['doc_type'] = doc_type
        result['timestamp'] = timestamp
        
        if result.get('success'):
            output_dir = './output_results/web'
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = os.path.splitext(saved_filename)[0]
            text_output = os.path.join(output_dir, f"{base_name}.txt")
            json_output = os.path.join(output_dir, f"{base_name}.json")
            
            with open(text_output, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            result['text_file'] = text_output
            result['json_file'] = json_output
            
            try:
                result['image_preview'] = image_to_base64(filepath)
            except:
                result['image_preview'] = None
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/recognize_base64', methods=['POST'])
def recognize_base64():
    data = request.get_json()
    
    if not data or 'image' not in data:
        return jsonify({'success': False, 'error': '没有提供图片数据'}), 400
    
    try:
        image_data = data['image']
        doc_type = data.get('doc_type', 'general')
        
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{unique_id}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        result = ocr_engine.recognize_document(filepath, doc_type)
        
        result['image_path'] = filepath
        result['filename'] = filename
        result['doc_type'] = doc_type
        result['timestamp'] = timestamp
        
        if result.get('success'):
            output_dir = './output_results/web'
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = os.path.splitext(filename)[0]
            text_output = os.path.join(output_dir, f"{base_name}.txt")
            json_output = os.path.join(output_dir, f"{base_name}.json")
            
            with open(text_output, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            result['text_file'] = text_output
            result['json_file'] = json_output
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        output_dir = './output_results/web'
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
                    'timestamp': data.get('timestamp', ''),
                    'engine': data.get('engine', 'unknown'),
                    'success': data.get('success', False),
                    'text_preview': data.get('text', '')[:200] + '...' if len(data.get('text', '')) > 200 else data.get('text', '')
                })
            except:
                continue
        
        return jsonify({'success': True, 'history': history})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'allowed_extensions': list(app.config['ALLOWED_EXTENSIONS']),
        'max_file_size': app.config['MAX_CONTENT_LENGTH'],
        'doc_types': {
            'contract': '合同文档',
            'bid': '投标书',
            'general': '通用文档'
        },
        'engines': ['auto', 'baidu', 'deepseek']
    })


if __name__ == '__main__':
    print("=" * 60)
    print("OCR Web Server Starting...")
    print("=" * 60)
    print(f"Server URL: http://localhost:5000")
    print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Output Folder: ./output_results/web")
    print(f"Max File Size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
