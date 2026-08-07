@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title 安装 CUDA 支持（仅限 NVIDIA 显卡）

echo.
echo ============================================================
echo          安装 CUDA 支持（仅限 NVIDIA 显卡）
echo ============================================================
echo.
echo 此脚本仅适用于 NVIDIA 显卡（GTX/RTX 系列）
echo.
echo 如果你不确定是否有 NVIDIA 显卡，请：
echo 1. 打开任务管理器（Ctrl + Shift + Esc）
echo 2. 点击"性能"标签
echo 3. 查看"GPU"部分
echo 4. 如果显示 NVIDIA GeForce，继续安装
echo.
pause

echo.
echo [步骤 1/4] 检查 NVIDIA 显卡...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo.
    echo 错误：未检测到 NVIDIA 显卡或驱动未安装
    echo.
    echo 请确认：
    echo 1. 你的电脑有 NVIDIA 显卡
    echo 2. 已安装 NVIDIA 驱动程序
    echo.
    echo 如果没有 NVIDIA 显卡，请使用 CPU 模式
    echo.
    pause
    exit /b 1
)

echo NVIDIA 显卡检测成功！
nvidia-smi --query-gpu=name --format=csv,noheader
echo.

echo [步骤 2/4] 卸载现有版本...
pip uninstall onnxruntime onnxruntime-directml onnxruntime-gpu -y
echo.

echo [步骤 3/4] 安装 CUDA 版本...
pip install onnxruntime-gpu==1.24.4
echo.

echo [步骤 4/4] 验证安装...
python -c "import onnxruntime as ort; print('Version:', ort.__version__); providers = ort.get_available_providers(); print('Providers:', providers); print('CUDA OK!' if 'CUDAExecutionProvider' in providers else 'CUDA not found')"
echo.

echo ============================================================
echo 安装完成！
echo.
echo 接下来：
echo 1. 关闭所有 FaceFusion 窗口
echo 2. 重新运行 启动FaceFusion.bat
echo 3. 在"执行提供商"部分应该会看到"CUDA"选项
echo 4. 勾选"CUDA"并开始处理
echo.
echo 注意：
echo - 如果没有看到 CUDA 选项，可能需要安装 CUDA Toolkit
echo - 下载地址：https://developer.nvidia.com/cuda-downloads
echo ============================================================
pause
