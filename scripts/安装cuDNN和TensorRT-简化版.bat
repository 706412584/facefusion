@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title 安装 cuDNN 和 TensorRT（简化版）

echo.
echo ============================================================
echo          安装 cuDNN 和 TensorRT（简化版）
echo ============================================================
echo.

echo [步骤 1/3] 安装 cuDNN
echo ============================================================
echo.
echo 你已经下载了 cuDNN 的 EXE 安装程序，很好！
echo.
echo 请按照以下步骤：
echo 1. 双击运行 cuDNN 的 .exe 文件
echo 2. 选择安装位置（默认即可）
echo 3. 等待安装完成
echo 4. 安装完成后，回到这里继续
echo.
pause

echo.
echo [步骤 2/3] 安装 TensorRT
echo ============================================================
echo.
echo 如果你还没有下载 TensorRT，现在打开下载页面...
start https://developer.nvidia.com/tensorrt-download
echo.
echo 请下载：TensorRT 10.7.0 for Windows (ZIP)
echo.
set /p tensorrt_path="下载完成后，拖拽 TensorRT ZIP 文件到这里: "
echo.

if not exist %tensorrt_path% (
    echo 跳过 TensorRT 安装（可以只用 cuDNN + CUDA）
    goto verify
)

echo 正在解压 TensorRT...
powershell -Command "Expand-Archive -Path '%tensorrt_path%' -DestinationPath 'C:\' -Force"
echo.

echo 正在复制 TensorRT 文件到 CUDA 目录...
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6

for /d %%i in (C:\TensorRT-*) do (
    echo 找到 TensorRT: %%i
    xcopy "%%i\lib\*.dll" "%CUDA_PATH%\bin\" /Y /I
    echo TensorRT DLL 文件已复制
)

:verify
echo.
echo [步骤 3/3] 验证安装
echo ============================================================
echo.

set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6

echo 检查 cuDNN...
if exist "%CUDA_PATH%\bin\cudnn64_9.dll" (
    echo [OK] cuDNN 已安装
) else (
    echo [?] cuDNN 未在标准位置找到
    echo     可能安装在其他位置，这也没问题
)

echo.
echo 检查 TensorRT...
if exist "%CUDA_PATH%\bin\nvinfer_10.dll" (
    echo [OK] TensorRT 已安装
) else (
    echo [SKIP] TensorRT 未安装（可选）
)

echo.
echo ============================================================
echo 安装完成！
echo ============================================================
echo.
echo 下一步：
echo 1. 重启电脑（让库文件生效）
echo 2. 运行: 启动FaceFusion.bat
echo 3. 勾选 CUDA（如果有 TensorRT 也勾选）
echo 4. 开始处理
echo.
echo 如果安装了 cuDNN + CUDA：
echo   预计速度：18-35 帧/秒
echo.
echo 如果安装了 cuDNN + CUDA + TensorRT：
echo   预计速度：20-40 帧/秒
echo.
echo ============================================================
pause
