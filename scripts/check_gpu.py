#!/usr/bin/env python3
"""检查显卡类型和推荐配置"""

import subprocess
import sys

def get_gpu_info():
    """获取显卡信息"""
    try:
        # 使用 PowerShell 获取显卡信息
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            gpus = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return gpus
        else:
            print(f"错误: {result.stderr}")
            return []
    except Exception as e:
        print(f"获取显卡信息失败: {e}")
        return []

def analyze_gpu(gpus):
    """分析显卡并给出推荐"""
    if not gpus:
        print("\n未检测到显卡信息")
        print("推荐: 使用 CPU 模式")
        print("预计速度: 2-5 帧/秒")
        return
    
    print("\n检测到的显卡:")
    for i, gpu in enumerate(gpus, 1):
        print(f"  {i}. {gpu}")
    
    print("\n推荐配置:")
    
    # 检查 NVIDIA
    nvidia_gpus = [gpu for gpu in gpus if 'nvidia' in gpu.lower()]
    if nvidia_gpus:
        print("\n  ✓ 检测到 NVIDIA 显卡")
        print("  推荐: 运行 scripts/安装CUDA支持.bat")
        print("  预计速度: 20-40 帧/秒 (最快)")
        return
    
    # 检查 AMD
    amd_gpus = [gpu for gpu in gpus if 'amd' in gpu.lower() or 'radeon' in gpu.lower()]
    if amd_gpus:
        print("\n  ✓ 检测到 AMD 显卡")
        print("  推荐: 运行 正确安装GPU.bat")
        print("  预计速度: 10-20 帧/秒")
        return
    
    # 检查 Intel
    intel_gpus = [gpu for gpu in gpus if 'intel' in gpu.lower()]
    if intel_gpus:
        print("\n  ✓ 检测到 Intel 显卡")
        print("  推荐: 运行 正确安装GPU.bat")
        print("  预计速度: 5-15 帧/秒")
        return
    
    print("\n  未识别的显卡类型")
    print("  推荐: 使用 CPU 模式")

def check_current_runtime():
    """检查当前安装的 ONNX Runtime"""
    print("\n" + "="*60)
    print("当前 ONNX Runtime 状态:")
    print("="*60)
    
    try:
        import onnxruntime as ort
        print(f"\n版本: {ort.__version__}")
        
        if hasattr(ort, 'get_available_providers'):
            providers = ort.get_available_providers()
            print(f"可用提供商: {providers}")
            
            if 'CUDAExecutionProvider' in providers:
                print("\n✓ CUDA 已安装 (NVIDIA GPU 加速)")
            elif 'DmlExecutionProvider' in providers:
                print("\n✓ DirectML 已安装 (AMD/Intel GPU 加速)")
            else:
                print("\n⚠ 仅 CPU 模式")
        else:
            print("\n⚠ 无法检测提供商 (可能版本不兼容)")
            
    except ImportError:
        print("\n✗ ONNX Runtime 未安装")
    except Exception as e:
        print(f"\n✗ 检查失败: {e}")

if __name__ == '__main__':
    print("="*60)
    print("FaceFusion GPU 检测工具")
    print("="*60)
    
    gpus = get_gpu_info()
    analyze_gpu(gpus)
    check_current_runtime()
    
    print("\n" + "="*60)
    print("\n按任意键退出...")
    input()
