@echo off
chcp 65001 >nul
title FaceFusion - 人脸融合工具

echo ============================================================
echo                    FaceFusion 启动中...
echo ============================================================
echo.

REM 清理 Gradio 缓存
echo [缓存] 清理 Gradio 缓存文件...
if exist ".caches\gradio" (
    powershell -Command "Remove-Item -Recurse -Force '.caches\gradio' -ErrorAction SilentlyContinue"
    echo [完成] Gradio 缓存已清理
) else (
    echo [提示] 缓存目录不存在
)
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

REM 自动检测和配置代理
echo [代理] 正在检测代理设置...
python -c "import sys; sys.path.insert(0, 'scripts'); import setup_proxy; proxy_info = setup_proxy.detect_proxy(); print(f'http://{proxy_info[0]}:{proxy_info[1]}' if proxy_info else 'NONE')" > temp_proxy.txt 2>nul
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
    set NO_PROXY=127.0.0.1,localhost
    set no_proxy=127.0.0.1,localhost
    echo [提示] 代理配置成功 - 下载速度将大幅提升
) else (
    echo [提示] 未检测到代理，使用直连
    echo [提示] 如果下载很慢，请运行 检查代理.bat 诊断问题
)
echo.

REM 禁用 Gradio 遥测和更新检查
set GRADIO_ANALYTICS_ENABLED=False
set DO_NOT_TRACK=1

REM 跳过 import gradio 检查（Python 3.13 下 import 会卡死）
REM 如需安装依赖请手动运行: pip install -r requirements.txt

echo [启动] 正在启动中文界面（instant_runner 模式）...
echo [提示] 已禁用内容检测，可以正常处理视频
echo.
python facefusion.py run --language zh --ui-workflow instant_runner

pause
