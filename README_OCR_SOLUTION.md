# DeepSeek-OCR 合同和投标书识别方案

基于 DeepSeek-OCR-2 源码分析，结合百度OCR和DeepSeek-OCR的混合识别方案，专门针对合同和投标书文档优化。

## 核心技术原理

### 1. DeepSeek-OCR-2 提高识别度的关键技术

#### 1.1 动态拼接视觉编码 (Dynamic Tiling Visual Encoding)
- **自适应分辨率处理**：支持 512px 到 1280px 的动态分辨率
- **智能裁剪策略**：根据文档尺寸自动计算最佳裁剪比例 (2-6个tiles)
- **全局+局部视图**：
  - 全局视图 (1024×1024)：捕获整体布局和结构
  - 局部视图 (768×768)：处理细节文本和表格

#### 1.2 双流视觉编码器架构
- **SAM ViT编码器**：基于Segment Anything Model的视觉编码器
  - 12层Transformer架构
  - 相对位置编码 (Relative Position Encoding)
  - 窗口注意力机制 (Window Attention)
  
- **Qwen2解码器作为编码器**：
  - 24层深度
  - 非因果+因果混合注意力机制
  - 896维隐藏层，14个注意力头

#### 1.3 视觉因果流 (Visual Causal Flow)
- **非因果注意力**：图像区域之间可以互相看到，增强上下文理解
- **因果注意力**：文本生成保持因果性，确保输出连贯
- **查询注入机制**：通过可学习的查询向量提取关键信息

#### 1.4 高级图像处理
- **图像增强**：自动对比度、锐度增强
- **EXIF校正**：自动处理图像方向
- **动态预处理**：根据文档类型调整处理参数

#### 1.5 重复抑制机制
- **N-gram重复抑制**：防止生成重复文本
- **白名单机制**：保护表格标签等特殊token
- **滑动窗口**：在指定窗口内检测重复模式

### 2. 混合识别策略

#### 2.1 百度OCR优势
- **速度快**：适合快速预览和初步识别
- **稳定性高**：对简单文档识别准确
- **成本低**：API调用费用相对较低

#### 2.2 DeepSeek-OCR优势
- **布局理解**：深度理解文档结构和布局
- **表格识别**：优秀的表格和公式识别能力
- **Markdown输出**：直接输出结构化Markdown格式
- **多语言支持**：支持20+种语言

#### 2.3 混合策略
- **快速模式**：优先使用百度OCR，失败时切换到DeepSeek
- **质量优先**：优先使用DeepSeek，确保识别质量
- **智能融合**：根据识别结果长度和质量自动选择最佳输出

## 安装配置

### 1. 环境要求
```bash
# Python 3.12+
conda create -n deepseek_ocr python=3.12 -y
conda activate deepseek_ocr
```

### 2. 安装依赖
```bash
# 基础依赖
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers pillow numpy tqdm

# 百度OCR SDK (可选)
pip install baidu-aip

# Flash Attention (推荐，提升性能)
pip install flash-attn==2.7.3 --no-build-isolation
```

### 3. 配置文件设置

编辑 `config_ocr.py`：

```python
# 百度OCR配置 (如果使用)
BAIDU_OCR_CONFIG = {
    'APP_ID': 'YOUR_BAIDU_APP_ID',
    'API_KEY': 'YOUR_BAIDU_API_KEY',
    'SECRET_KEY': 'YOUR_BAIDU_SECRET_KEY',
    'use_baidu_ocr': True,
    'baidu_priority': 'fast'  # 'fast' 或 'quality'
}

# 识别模式
RECOGNITION_MODE = 'hybrid'  # 'baidu', 'deepseek', 'hybrid'
```

## 使用方法

### 1. 单个文档识别

#### 识别合同
```bash
python simple_ocr.py contract /path/to/contract.jpg
```

#### 识别投标书
```bash
python simple_ocr.py bid /path/to/bid.pdf
```

#### 识别普通文档
```bash
python simple_ocr.py /path/to/document.jpg general
```

### 2. 批量处理

#### 批量处理合同
```bash
python simple_ocr.py batch-contracts /path/to/contracts_folder
```

#### 批量处理投标书
```bash
python simple_ocr.py batch-bids /path/to/bids_folder
```

### 3. 目录结构
```
deepseekorc_eg/
├── input_images/
│   ├── contracts/          # 合同图片
│   └── bids/               # 投标书图片
├── output_results/
│   ├── contracts/          # 合同识别结果
│   ├── bids/               # 投标书识别结果
│   └── single/             # 单个文档识别结果
├── config_ocr.py           # 配置文件
├── hybrid_ocr_engine.py    # 核心引擎
└── simple_ocr.py           # 简单接口
```

### 4. Python API使用

```python
from hybrid_ocr_engine import HybridOCREngine

# 初始化引擎
engine = HybridOCREngine()

# 识别单个合同
result = engine.recognize_document(
    image_path='contract.jpg',
    doc_type='contract'
)

if result['success']:
    print(result['text'])

# 批量处理
results = engine.batch_recognize(
    image_dir='./input_images/contracts',
    doc_type='contract'
)
```

## 针对合同和投标书的优化

### 1. 合同文档优化
- **专用Prompt**：针对法律文本、条款、签名的识别优化
- **增强裁剪**：使用3-6个tiles确保细节不丢失
- **布局保持**：保留合同的法律格式和结构

### 2. 投标书优化
- **表格识别**：强化表格、价格、技术规格的识别
- **结构化输出**：输出Markdown格式，便于后续处理
- **多页处理**：支持多页PDF投标书

### 3. 通用优化
- **图像预处理**：自动增强对比度和锐度
- **方向校正**：自动处理EXIF方向信息
- **质量检测**：自动选择最佳识别引擎

## 输出格式

### 1. 文本输出 (.txt)
纯文本格式，便于阅读和编辑。

### 2. JSON输出 (.json)
包含完整的识别结果和元数据：
```json
{
  "success": true,
  "text": "识别的文本内容",
  "engine": "Hybrid",
  "image_path": "原始图片路径",
  "filename": "文件名",
  "baidu_result": {...},
  "deepseek_result": {...}
}
```

### 3. Markdown输出
DeepSeek-OCR可直接输出Markdown格式，保留文档结构。

## 性能优化建议

### 1. GPU加速
- 推荐使用CUDA 11.8+和PyTorch 2.6.0
- 使用Flash Attention加速推理
- 设置适当的GPU内存利用率

### 2. 批处理优化
- 调整并发数 (MAX_CONCURRENCY)
- 优化工作进程数 (NUM_WORKERS)
- 使用异步处理提高效率

### 3. 内存管理
- 对于大文档，适当降低max_crops
- 使用bfloat16减少内存占用
- 及时清理临时文件

## 故障排除

### 1. 内存不足
```python
# 在config_ocr.py中调整
MAX_CONCURRENCY = 50  # 降低并发数
MAX_CROPS = 4         # 减少裁剪数量
```

### 2. 识别速度慢
```python
# 使用快速模式
RECOGNITION_MODE = 'baidu'
BAIDU_OCR_CONFIG['baidu_priority'] = 'fast'
```

### 3. 准确率不高
```python
# 使用质量优先模式
RECOGNITION_MODE = 'deepseek'
# 或增加裁剪数量
OPTIONS['contract']['max_crops'] = 6
```

## 技术架构图

```
输入图像
    ↓
图像预处理 (增强、校正)
    ↓
┌─────────────┬─────────────┐
│  百度OCR    │ DeepSeek-OCR│
│  (快速)     │  (高质量)   │
└─────────────┴─────────────┘
    ↓              ↓
文本结果      Markdown结果
    ↓              ↓
    └──────┬───────┘
           ↓
    智能融合选择
           ↓
    最终输出结果
```

## 核心代码文件说明

- [config_ocr.py](config_ocr.py)：配置文件，包含所有参数设置
- [hybrid_ocr_engine.py](hybrid_ocr_engine.py)：核心OCR引擎，实现混合识别逻辑
- [simple_ocr.py](simple_ocr.py)：简单易用的命令行接口

## 参考资源

- DeepSeek-OCR-2 GitHub: https://github.com/deepseek-ai/DeepSeek-OCR-2
- 官方文档: https://deepseekocr.com/zh-CN
- 百度OCR文档: https://cloud.baidu.com/product/ocr

## 许可证

本项目基于 DeepSeek-OCR-2 的 Apache 2.0 许可证。
