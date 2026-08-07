@echo off
chcp 65001 >nul
title 验证 GPU 库安装

echo.
echo ============================================================
echo              验证 GPU 库安装
echo ============================================================
echo.

set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6

echo [1] 检查 CUDA Toolkit...
if exist "%CUDA_PATH%" (
    echo [OK] CUDA Toolkit 已安装: %CUDA_PATH%
) else (
    echo [FAIL] CUDA Toolkit 未找到
)
echo.

echo [2] 检查 cuDNN...
if exist "%CUDA_PATH%\bin\cudnn64_9.dll" (
    echo [OK] cuDNN 9.x 已安装
) else (
    echo [?] 在 CUDA 目录未找到 cudnn64_9.dll
    echo     检查其他可能位置...
    
    if exist "C:\Program Files\NVIDIA\CUDNN\v9.5\bin\cudnn64_9.dll" (
        echo [OK] cuDNN 安装在: C:\Program Files\NVIDIA\CUDNN\v9.5\
    ) else if exist "C:\Program Files\NVIDIA\CUDNN\v9.0\bin\cudnn64_9.dll" (
        echo [OK] cuDNN 安装在: C:\Program Files\NVIDIA\CUDNN\v9.0\
    ) else (
        echo [FAIL] cuDNN 未找到
    )
)
echo.

echo [3] 检查 TensorRT...
if exist "%CUDA_PATH%\bin\nvinfer_10.dll" (
    echo [OK] TensorRT 10.x 已安装在 CUDA 目录
) else if exist "%CUDA_PATH%\bin\nvinfer.dll" (
    echo [OK] TensorRT 已安装在 CUDA 目录
) else (
    echo [?] 在 CUDA 目录未找到 TensorRT DLL
    echo     检查其他可能位置...
    
    if exist "C:\TensorRT\lib\nvinfer_10.dll" (
        echo [OK] TensorRT 安装在: C:\TensorRT\
    ) else if exist "C:\TensorRT\lib\nvinfer.dll" (
        echo [OK] TensorRT 安装在: C:\TensorRT\
    )
    
    for /d %%i in (C:\TensorRT-*) do (
        if exist "%%i\lib\nvinfer_10.dll" (
            echo [OK] TensorRT 安装在: %%i
        ) else if exist "%%i\lib\nvinfer.dll" (
            echo [OK] TensorRT 安装在: %%i
        )
    )
    
    if exist "C:\Program Files\NVIDIA\TensorRT\lib\nvinfer_10.dll" (
        echo [OK] TensorRT 安装在: C:\Program Files\NVIDIA\TensorRT\
    ) else if exist "C:\Program Files\NVIDIA\TensorRT\lib\nvinfer.dll" (
        echo [OK] TensorRT 安装在: C:\Program Files\NVIDIA\TensorRT\
    )
)
echo.

echo [4] 检查环境变量...
echo %PATH% | findstr /i "CUDA" >nul
if %errorlevel%==0 (
    echo [OK] CUDA 在 PATH 中
) else (
    echo [WARN] CUDA 不在 PATH 中
)

echo %PATH% | findstr /i "TensorRT" >nul
if %errorlevel%==0 (
    echo [OK] TensorRT 在 PATH 中
) else (
    echo [WARN] TensorRT 不在 PATH 中
    echo       需要添加 C:\TensorRT\lib 到 PATH
)
echo.

echo [5] 测试 Python ONNX Runtime...
python -c "try: import onnxruntime as ort; print('[OK] ONNX Runtime version:', ort.__version__); providers = ort.get_available_providers(); print('[OK] Available providers:', providers); print(''); print('Summary:'); print('  CUDA:', 'YES' if 'CUDAExecutionProvider' in providers else 'NO'); print('  TensorRT:', 'YES' if 'TensorrtExecutionProvider' in providers else 'NO'); except Exception as e: print('[FAIL] Error:', e)"
echo.

echo ============================================================
echo 诊断完成
echo ============================================================
echo.
echo 如果看到：
echo - cuDNN: [OK] 
echo - CUDA: YES
echo   → 可以使用 GPU 加速了！
echo.
echo 如果看到：
echo - cuDNN: [FAIL] 或 [?]
echo   → 需要配置环境变量或重新安装
echo.
echo 解决方案：
echo 1. 如果 cuDNN 安装在其他位置，需要添加到 PATH
echo 2. 或者运行: 修复CUDA缺少库文件.bat
echo.
echo ============================================================
pause
