@echo off
chcp 65001 >nul
title 配置 cuDNN

echo.
echo ============================================================
echo              配置 cuDNN 9.21
echo ============================================================
echo.

set CUDNN_PATH=C:\Program Files\NVIDIA\CUDNN\v9.21

echo [1/3] 检查 cuDNN 安装...
if not exist "%CUDNN_PATH%" (
    echo 错误：cuDNN 未找到
    pause
    exit /b 1
)

echo [OK] cuDNN 路径: %CUDNN_PATH%
echo.

echo [2/3] 复制 cuDNN DLL 到 CUDA 目录...
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6

if not exist "%CUDA_PATH%" (
    echo 警告：CUDA 12.6 未找到
    echo 将只配置环境变量
    goto skip_copy
)

REM 使用 CUDA 12.9 的 cuDNN（最接近 12.6）
echo 从: %CUDNN_PATH%\bin\12.9\x64
echo 到: %CUDA_PATH%\bin

xcopy "%CUDNN_PATH%\bin\12.9\x64\*.dll" "%CUDA_PATH%\bin\" /Y /I
echo [OK] cuDNN DLL 文件已复制
echo.

:skip_copy
echo [3/3] 配置环境变量...

REM 添加 cuDNN 到 PATH
setx PATH "%PATH%;%CUDNN_PATH%\bin\12.9\x64" /M >nul 2>&1
if %errorlevel%==0 (
    echo [OK] PATH 已更新（系统级）
) else (
    echo [WARN] 无法更新系统 PATH（需要管理员权限）
    echo       尝试用户级 PATH...
    setx PATH "%PATH%;%CUDNN_PATH%\bin\12.9\x64" >nul 2>&1
    echo [OK] PATH 已更新（用户级）
)

REM 创建 CUDNN_PATH 环境变量
setx CUDNN_PATH "%CUDNN_PATH%" /M >nul 2>&1
if %errorlevel% neq 0 (
    setx CUDNN_PATH "%CUDNN_PATH%" >nul 2>&1
)
echo [OK] CUDNN_PATH = %CUDNN_PATH%
echo.

echo ============================================================
echo 配置完成！
echo ============================================================
echo.
echo cuDNN 位置：%CUDNN_PATH%
echo 已添加到 PATH：%CUDNN_PATH%\bin\12.9\x64
echo.
echo 检查安装的文件：
dir "%CUDNN_PATH%\bin\12.9\x64\cudnn*.dll" /b
echo.
echo ============================================================
pause
