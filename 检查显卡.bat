@echo off
chcp 65001 >nul
title 检查显卡类型

echo.
echo ============================================================
echo                      检查显卡类型
echo ============================================================
echo.

echo [1] 显卡信息:
powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"
echo.

echo [2] 推荐配置:
echo.

REM 检查是否有 NVIDIA 显卡
powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name" | findstr /i "NVIDIA" >nul
if %errorlevel%==0 (
    echo    检测到 NVIDIA 显卡
    echo    推荐: 运行 安装CUDA支持.bat
    echo    预计速度: 20-40 帧/秒
    echo.
    goto :end
)

REM 检查是否有 AMD 显卡
powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name" | findstr /i "AMD Radeon" >nul
if %errorlevel%==0 (
    echo    检测到 AMD 显卡
    echo    推荐: 运行 正确安装GPU.bat
    echo    预计速度: 10-20 帧/秒
    echo.
    goto :end
)

REM 检查是否有 Intel 显卡
powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name" | findstr /i "Intel" >nul
if %errorlevel%==0 (
    echo    检测到 Intel 显卡
    echo    推荐: 运行 正确安装GPU.bat
    echo    预计速度: 5-15 帧/秒
    echo.
    goto :end
)

echo    未检测到独立显卡
echo    推荐: 使用 CPU 模式
echo    预计速度: 2-5 帧/秒
echo.

:end
echo ============================================================
echo.
echo 在 FaceFusion 界面中:
echo 1. 找到"执行提供商"选项
echo 2. 勾选上面推荐的选项
echo 3. 重新开始处理
echo.
echo ============================================================
pause
