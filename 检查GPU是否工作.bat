@echo off
chcp 65001 >nul
title 检查 GPU 是否工作

echo.
echo ============================================================
echo              检查 GPU 是否工作
echo ============================================================
echo.

echo [1] 检查 Python 版本...
python --version
echo.

echo [2] 检查 ONNX Runtime...
python -c "import onnxruntime as ort; print('ONNX Runtime:', ort.__version__); providers = ort.get_available_providers(); print('Providers:', providers); print(''); print('GPU Status:'); print('  CUDA:', 'YES' if 'CUDAExecutionProvider' in providers else 'NO'); print('  TensorRT:', 'YES' if 'TensorrtExecutionProvider' in providers else 'NO')"
echo.

echo [3] 检查 NVIDIA 驱动...
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
echo.

echo [4] 测试 CUDA 是否可用...
python -c "try: import torch; print('PyTorch CUDA:', torch.cuda.is_available()); except: print('PyTorch not installed')"
echo.

echo ============================================================
echo 诊断结果：
echo ============================================================
echo.
echo 如果看到：
echo   CUDA: YES - GPU 加速可用
echo   CUDA: NO - GPU 加速不可用，需要检查配置
echo.
echo 如果 CUDA 显示 NO：
echo 1. 检查 cuDNN 和 TensorRT 是否正确安装
echo 2. 检查环境变量 PATH
echo 3. 可能需要重新安装 onnxruntime-gpu
echo.
echo 如果 CUDA 显示 YES 但 FaceFusion 还是慢：
echo 1. 确保在界面勾选了 CUDA
echo 2. 查看任务管理器 GPU 使用率
echo 3. 检查终端是否有错误信息
echo.
echo ============================================================
pause
