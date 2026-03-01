#!/usr/bin/env python3
"""
DeepSeek-OCR-2 模型包装器
修复CUDA硬编码问题，支持MPS和CPU
"""
import torch
import os

# 保存原始的cuda方法
_original_cuda = torch.Tensor.cuda

def patched_cuda(self, device=None, non_blocking=False, memory_format=torch.preserve_format):
    """
    修补后的cuda方法
    如果CUDA不可用，则返回tensor本身（已在正确的设备上）
    """
    if not torch.cuda.is_available():
        # 如果tensor已经在当前设备上，直接返回
        return self
    return _original_cuda(self, device, non_blocking, memory_format)

# 应用补丁
torch.Tensor.cuda = patched_cuda

# 同时修补torch.autocast
_original_autocast = torch.autocast

def patched_autocast(device_type, dtype=None, enabled=True, cache_enabled=None):
    """
    修补后的autocast
    如果请求的是cuda但不可用，则使用cpu
    """
    if device_type == "cuda" and not torch.cuda.is_available():
        # 检测可用的设备
        if torch.backends.mps.is_available():
            device_type = "cpu"  # MPS不支持autocast，使用cpu
        else:
            device_type = "cpu"
    return _original_autocast(device_type, dtype, enabled, cache_enabled)

torch.autocast = patched_autocast

print("✓ 模型包装器已加载，CUDA兼容性补丁已应用")
