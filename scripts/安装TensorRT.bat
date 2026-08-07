@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title 配置 TensorRT

echo.
echo ============================================================
echo              配置 TensorRT 10.16
echo ============================================================
echo.

set TENSORRT_PATH=C:\Program Files\TensorRT-10.16.1.11.Windows.amd64.cuda-13.2\TensorRT-10.16.1.11

echo [1/5] 检查 TensorRT 路径...
if not exist "%TENSORRT_PATH%" (
    echo 错误：TensorRT 未找到
    echo 路径：%TENSORRT_PATH%
    pause
    exit /b 1
)

echo [OK] TensorRT 路径: %TENSORRT_PATH%
echo.

echo [2/5] 复制 DLL 文件到 CUDA 目录...
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6

if not exist "%CUDA_PATH%" (
    echo 警告：CUDA 12.6 未找到，尝试其他版本...
    
    if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.2" (
        set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.2
        echo 找到 CUDA 13.2
    ) else (
        echo 将只配置环境变量
        goto skip_copy
    )
)

echo 从: %TENSORRT_PATH%\bin
echo 到: %CUDA_PATH%\bin
xcopy "%TENSORRT_PATH%\bin\*.dll" "%CUDA_PATH%\bin\" /Y /I
echo [OK] DLL 文件已复制
echo.

:skip_copy
echo [3/5] 配置环境变量...

REM 添加 TensorRT bin 到 PATH（DLL 在 bin 目录）
setx PATH "%PATH%;%TENSORRT_PATH%\bin" /M >nul 2>&1
if %errorlevel%==0 (
    echo [OK] PATH 已更新（系统级）
) else (
    echo [WARN] 无法更新系统 PATH（需要管理员权限）
    echo       尝试用户级 PATH...
    setx PATH "%PATH%;%TENSORRT_PATH%\bin" >nul 2>&1
    echo [OK] PATH 已更新（用户级）
)
echo.

echo [4/5] 创建环境变量 TENSORRT_PATH...
setx TENSORRT_PATH "%TENSORRT_PATH%" /M >nul 2>&1
if %errorlevel% neq 0 (
    setx TENSORRT_PATH "%TENSORRT_PATH%" >nul 2>&1
)
echo [OK] TENSORRT_PATH = %TENSORRT_PATH%
echo.

echo [5/5] 验证安装...
echo.
echo 检查文件：
if exist "%TENSORRT_PATH%\bin\nvinfer_10.dll" (
    echo [OK] nvinfer_10.dll
) else if exist "%TENSORRT_PATH%\bin\nvinfer.dll" (
    echo [OK] nvinfer.dll
) else (
    echo [FAIL] TensorRT DLL 未找到
    dir "%TENSORRT_PATH%\bin\nvinfer*.dll"
)

if exist "%TENSORRT_PATH%\bin\nvinfer_plugin_10.dll" (
    echo [OK] nvinfer_plugin_10.dll
) else if exist "%TENSORRT_PATH%\bin\nvinfer_plugin.dll" (
    echo [OK] nvinfer_plugin.dll
) else (
    echo [WARN] nvinfer_plugin DLL 未找到
)

echo.
echo 列出所有 TensorRT DLL：
dir "%TENSORRT_PATH%\bin\*.dll" /b
echo.

echo ============================================================
echo 配置完成！
echo ============================================================
echo.
echo TensorRT 位置：%TENSORRT_PATH%
echo.
echo 已添加到 PATH：%TENSORRT_PATH%\bin
echo.
echo 重要：必须重启电脑才能生效！
echo.
echo 重启后：
echo 1. 运行: scripts/验证GPU库安装.bat
echo 2. 运行: 启动FaceFusion.bat
echo 3. 勾选 CUDA 和 TensorRT
echo 4. 开始处理
echo.
echo 预计速度：20-40 帧/秒
echo 你的视频（54650 帧）约需：20-45 分钟
echo.
echo ============================================================
pause
