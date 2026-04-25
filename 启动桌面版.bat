@echo off
chcp 65001 >nul
title FaceFusion 桌面版

echo ============================================================
echo                FaceFusion 桌面版启动中...
echo ============================================================
echo.

REM 检查 PyQt6
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 PyQt6...
    pip install PyQt6
    echo.
)

echo [启动] 正在启动桌面应用...
echo.
python facefusion_desktop.py

if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请检查错误信息
    pause
)
