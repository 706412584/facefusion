@echo off
chcp 65001 >nul
title FaceFusion - 人脸融合工具

echo ============================================================
echo                    FaceFusion 启动中...
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包，请稍候...
    pip install -r requirements.txt
)

echo [启动] 正在启动中文界面...
echo.
python facefusion.py run --language zh

pause
