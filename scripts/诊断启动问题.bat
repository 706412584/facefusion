@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title FaceFusion 启动诊断

echo ============================================================
echo                  FaceFusion 启动诊断
echo ============================================================
echo.

echo [1/5] 检查 Python 版本...
python --version
echo.

echo [2/5] 检查配置文件...
if exist facefusion.ini (
    echo [OK] facefusion.ini 存在
) else (
    echo [错误] facefusion.ini 不存在
)
echo.

echo [3/5] 检查核心模块...
python -c "import facefusion; print('[OK] facefusion 模块正常')" 2>&1
echo.

echo [4/5] 检查 Gradio...
python -c "import gradio; print('[OK] Gradio 版本:', gradio.__version__)" 2>&1
echo.

echo [5/5] 尝试启动（显示详细错误）...
echo.
python facefusion.py run --language zh --ui-workflow instant_runner 2>&1
echo.

echo ============================================================
echo 诊断完成
echo ============================================================
pause
