@echo off
chcp 65001 >nul
title FaceFusion 桌面版

echo ============================================================
echo                FaceFusion 桌面版启动中...
echo ============================================================
echo.

REM 自动检测和配置代理
echo [代理] 正在检测代理设置...
python -c "import setup_proxy; proxy_info = setup_proxy.detect_proxy(); print(f'http://{proxy_info[0]}:{proxy_info[1]}' if proxy_info else 'NONE')" > temp_proxy.txt 2>nul
set /p PROXY_URL=<temp_proxy.txt
del temp_proxy.txt 2>nul

if "%PROXY_URL%"=="NONE" (
    echo [提示] 未检测到代理，使用直连
    set PROXY_URL=
) else if defined PROXY_URL (
    echo [提示] 检测到代理: %PROXY_URL%
    set HTTP_PROXY=%PROXY_URL%
    set HTTPS_PROXY=%PROXY_URL%
    set http_proxy=%PROXY_URL%
    set https_proxy=%PROXY_URL%
    echo [提示] 代理配置成功 - 下载速度将大幅提升
) else (
    echo [提示] 未检测到代理，使用直连
    echo [提示] 如果下载很慢，请运行 检查代理.bat 诊断问题
)
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
