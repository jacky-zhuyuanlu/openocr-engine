# OCR Web 应用 - 快速启动指南

## 🚀 快速启动（3步）

### 1. 安装依赖

```bash
pip install -r requirements_web.txt
```

### 2. 启动服务

**方式一：使用启动脚本（推荐）**
```bash
./start.sh
```

**方式二：使用Python**
```bash
python start_web.py
```

**方式三：直接运行Flask**
```bash
python app.py
```

### 3. 访问应用

打开浏览器访问：**http://localhost:5000**

## 📋 已配置的API密钥

### 百度OCR
- API_KEY: `0ooCxqxczLd5WrQWOB4oN3ar`
- SECRET_KEY: `Bh7JBNDIdwQ26Y6aothlQyM4WaGb9sgh`

### DeepSeek API
- API_KEY: `sk-8e51dda022ff4cb5a2fa20e3a6443839`
- BASE_URL: `https://api.deepseek.com`

配置文件：[config_ocr.py](config_ocr.py)

## 🎯 功能演示

### 上传图片
1. 点击上传区域或拖拽图片
2. 选择文档类型（合同/投标书/通用）
3. 选择识别引擎（自动/百度/DeepSeek）
4. 点击"开始识别"

### 查看结果
- 识别结果实时显示
- 支持一键复制
- 查看识别引擎和时间
- 历史记录查看

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| [app.py](app.py) | Flask Web服务器主程序 |
| [start_web.py](start_web.py) | 启动脚本（带环境检查） |
| [start.sh](start.sh) | Shell启动脚本 |
| [config_ocr.py](config_ocr.py) | 配置文件（API密钥） |
| [hybrid_ocr_engine.py](hybrid_ocr_engine.py) | OCR识别引擎 |
| [templates/index.html](templates/index.html) | 前端页面 |
| [test_web.py](test_web.py) | API测试脚本 |
| [requirements_web.txt](requirements_web.txt) | Python依赖 |

## 🔧 测试API

启动服务后，运行测试脚本：

```bash
python test_web.py
```

测试内容包括：
- 健康检查
- 获取配置
- 历史记录
- 文件上传识别
- Base64识别

## 📖 完整文档

详细使用说明请查看：[README_WEB.md](README_WEB.md)

## ⚠️ 注意事项

1. **首次运行**：DeepSeek-OCR模型会自动下载（约3GB），需要稳定的网络连接
2. **GPU加速**：如有CUDA GPU，识别速度会显著提升
3. **文件大小**：最大支持16MB的图片
4. **端口占用**：如5000端口被占用，请修改 [app.py](app.py) 中的端口号

## 🐛 常见问题

### 问题1：启动失败
```bash
# 检查Python版本（需要3.8+）
python --version

# 重新安装依赖
pip install -r requirements_web.txt
```

### 问题2：模型下载失败
```bash
# 设置镜像源（国内用户）
export HF_ENDPOINT=https://hf-mirror.com

# 然后重新启动
python start_web.py
```

### 问题3：识别失败
- 检查API密钥是否正确
- 查看控制台错误信息
- 尝试切换识别引擎

## 📞 技术支持

- DeepSeek-OCR文档: https://deepseekocr.com/zh-CN
- 百度OCR文档: https://cloud.baidu.com/product/ocr
- Flask文档: https://flask.palletsprojects.com/

## 🎉 开始使用

现在就启动服务，体验智能OCR识别吧！

```bash
./start.sh
```

然后访问：http://localhost:5000
