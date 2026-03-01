# OCR Web 应用使用指南

基于 DeepSeek-OCR 和百度OCR 的轻量级Web应用，支持图片上传和文档识别。

## 功能特点

- 🖼️ 支持拖拽或点击上传图片
- 📄 支持合同、投标书、通用文档三种识别模式
- 🔄 智能选择识别引擎（百度OCR / DeepSeek-OCR）
- 📝 实时显示识别结果
- 📚 历史记录查看
- 📋 一键复制识别结果

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_web.txt
```

### 2. 配置API密钥

已配置好以下API密钥：

**百度OCR：**
- API_KEY: `0ooCxqxczLd5WrQWOB4oN3ar`
- SECRET_KEY: `Bh7JBNDIdwQ26Y6aothlQyM4WaGb9sgh`

**DeepSeek API：**
- API_KEY: `sk-8e51dda022ff4cb5a2fa20e3a6443839`
- BASE_URL: `https://api.deepseek.com`

配置文件：[config_ocr.py](config_ocr.py)

### 3. 启动Web服务

```bash
python start_web.py
```

或直接运行：

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：`http://localhost:5000`

## 使用说明

### 上传图片

1. 点击上传区域或拖拽图片到上传框
2. 支持的格式：JPG、PNG、GIF、BMP、WEBP
3. 最大文件大小：16MB

### 选择识别模式

- **通用文档**：适用于普通文档识别
- **合同文档**：针对合同文档优化，保留法律格式
- **投标书**：针对投标书优化，强化表格识别

### 选择识别引擎

- **自动选择**：根据文档类型和内容自动选择最佳引擎
- **百度OCR**：快速识别，适合简单文档
- **DeepSeek-OCR**：高质量识别，适合复杂文档

### 查看结果

识别完成后，结果会显示在右侧文本框中，可以：
- 查看识别的文本内容
- 查看使用的引擎和识别时间
- 一键复制识别结果

### 历史记录

页面底部显示最近的识别历史记录，包括：
- 文件名
- 文档类型
- 识别状态
- 使用引擎
- 文本预览

## API接口

### 1. 健康检查

```bash
GET /api/health
```

返回：
```json
{
  "status": "ok",
  "baidu_ocr": true,
  "deepseek_ocr": true,
  "deepseek_api": false
}
```

### 2. 识别文档（文件上传）

```bash
POST /api/recognize
Content-Type: multipart/form-data

参数：
- file: 图片文件
- doc_type: 文档类型（contract/bid/general）
- engine: 识别引擎（auto/baidu/deepseek）
```

返回：
```json
{
  "success": true,
  "text": "识别的文本内容",
  "engine": "Hybrid",
  "doc_type": "contract",
  "timestamp": "20240227_143025",
  "filename": "20240227_143025_abc123_contract.jpg",
  "text_file": "./output_results/web/20240227_143025_abc123_contract.txt",
  "json_file": "./output_results/web/20240227_143025_abc123_contract.json",
  "image_preview": "base64编码的图片"
}
```

### 3. 识别文档（Base64）

```bash
POST /api/recognize_base64
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,...",
  "doc_type": "contract"
}
```

### 4. 获取历史记录

```bash
GET /api/history
```

返回：
```json
{
  "success": true,
  "history": [
    {
      "filename": "20240227_143025_abc123_contract.jpg",
      "doc_type": "contract",
      "timestamp": "20240227_143025",
      "engine": "Hybrid",
      "success": true,
      "text_preview": "识别文本预览..."
    }
  ]
}
```

### 5. 获取配置信息

```bash
GET /api/config
```

返回：
```json
{
  "allowed_extensions": ["png", "jpg", "jpeg", "gif", "bmp", "webp"],
  "max_file_size": 16777216,
  "doc_types": {
    "contract": "合同文档",
    "bid": "投标书",
    "general": "通用文档"
  },
  "engines": ["auto", "baidu", "deepseek"]
}
```

## 目录结构

```
deepseekorc_eg/
├── app.py                    # Flask Web服务器
├── start_web.py              # 启动脚本
├── config_ocr.py             # 配置文件
├── hybrid_ocr_engine.py      # OCR引擎
├── requirements_web.txt       # Web应用依赖
├── templates/
│   └── index.html           # 前端页面
├── uploads/                  # 上传的图片
└── output_results/
    └── web/                  # Web识别结果
        ├── *.txt            # 文本结果
        └── *.json           # JSON结果
```

## 技术栈

### 后端
- Flask：Web框架
- PyTorch：深度学习框架
- Transformers：HuggingFace模型库
- 百度OCR SDK：百度OCR接口

### 前端
- HTML5 + CSS3
- 原生JavaScript
- Fetch API：异步请求

### OCR引擎
- 百度OCR：快速识别
- DeepSeek-OCR-2：高质量识别

## 常见问题

### 1. 启动失败

**问题**：提示缺少依赖
**解决**：运行 `pip install -r requirements_web.txt`

**问题**：端口被占用
**解决**：修改 [app.py](app.py) 最后一行的端口号

### 2. 识别失败

**问题**：百度OCR认证失败
**解决**：检查 [config_ocr.py](config_ocr.py) 中的API密钥是否正确

**问题**：DeepSeek-OCR模型加载失败
**解决**：确保网络连接正常，模型会自动从HuggingFace下载

### 3. 性能问题

**问题**：识别速度慢
**解决**：
- 选择"百度OCR"引擎
- 降低图片分辨率
- 使用GPU加速

**问题**：内存不足
**解决**：
- 减少并发数
- 降低图片质量
- 使用CPU模式

## 开发说明

### 添加新的文档类型

在 [config_ocr.py](config_ocr.py) 的 `OPTIONS` 中添加：

```python
OPTIONS['invoice'] = {
    'prompt': '<image>\n<|grounding|>Convert this invoice to markdown.',
    'crop_mode': True,
    'min_crops': 2,
    'max_crops': 4
}
```

### 自定义前端样式

编辑 [templates/index.html](templates/index.html) 中的CSS样式。

### 添加新的API端点

在 [app.py](app.py) 中添加新的路由函数。

## 部署

### 本地部署

直接运行 `python start_web.py` 即可。

### 生产环境部署

建议使用 Gunicorn 或 uWSGI：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements_web.txt .
RUN pip install -r requirements_web.txt

COPY . .

EXPOSE 5000

CMD ["python", "start_web.py"]
```

构建和运行：

```bash
docker build -t ocr-web .
docker run -p 5000:5000 ocr-web
```

## 安全建议

1. 不要将API密钥提交到版本控制
2. 使用环境变量存储敏感信息
3. 启用HTTPS（生产环境）
4. 添加用户认证
5. 限制文件上传大小和类型
6. 定期更新依赖包

## 许可证

本项目基于 DeepSeek-OCR-2 的 Apache 2.0 许可证。

## 相关链接

- DeepSeek-OCR-2 GitHub: https://github.com/deepseek-ai/DeepSeek-OCR-2
- 官方文档: https://deepseekocr.com/zh-CN
- 百度OCR文档: https://cloud.baidu.com/product/ocr
- Flask文档: https://flask.palletsprojects.com/
