#!/usr/bin/env python3
"""
GPU版本PyTorch安装脚本
自动检测CUDA版本并安装对应的PyTorch
"""

import subprocess
import sys
import re

def get_cuda_version():
    """获取系统CUDA版本"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            # 从nvidia-smi输出中提取CUDA版本
            match = re.search(r'CUDA Version: (\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
        return None
    except FileNotFoundError:
        return None

def install_pytorch_cuda(cuda_version):
    """根据CUDA版本安装PyTorch"""
    
    # 根据CUDA版本选择对应的PyTorch版本
    if cuda_version and float(cuda_version) >= 12.1:
        # CUDA 12.1+ - 使用可用的最新版本
        install_cmd = [
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu121"
        ]
        print(f"🚀 安装CUDA 12.1版本的PyTorch (最新版本)...")
    elif cuda_version and float(cuda_version) >= 11.8:
        # CUDA 11.8
        install_cmd = [
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu118"
        ]
        print(f"🚀 安装CUDA 11.8版本的PyTorch (最新版本)...")
    else:
        # CPU版本
        install_cmd = [
            sys.executable, "-m", "pip", "install",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ]
        print(f"🚀 安装CPU版本的PyTorch (最新版本)...")
    
    try:
        print("执行命令:", " ".join(install_cmd))
        result = subprocess.run(install_cmd, check=True)
        print("✅ PyTorch安装成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyTorch安装失败: {e}")
        return False

def verify_installation():
    """验证PyTorch安装"""
    try:
        import torch
        print(f"\n📦 PyTorch版本: {torch.__version__}")
        print(f"🔧 CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"🎯 CUDA版本: {torch.version.cuda}")
            print(f"🔢 GPU数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        return True
    except ImportError:
        print("❌ PyTorch导入失败")
        return False

def main():
    print("🔍 检测CUDA版本并安装对应的PyTorch\n")
    
    # 检测CUDA版本
    cuda_version = get_cuda_version()
    if cuda_version:
        print(f"✅ 检测到CUDA版本: {cuda_version}")
    else:
        print("⚠️  未检测到CUDA，将安装CPU版本")
    
    # 安装PyTorch
    if install_pytorch_cuda(cuda_version):
        print("\n🔍 验证安装...")
        verify_installation()
    else:
        print("❌ 安装失败，请手动安装")

if __name__ == "__main__":
    main()
