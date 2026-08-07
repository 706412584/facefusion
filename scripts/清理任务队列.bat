@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title 清理任务队列

echo.
echo ============================================================
echo              清理 FaceFusion 任务队列
echo ============================================================
echo.
echo 这将清理所有失败和卡住的任务
echo.
pause

echo.
echo [1/3] 清理失败的任务...
del /q ".jobs\failed\*.json" 2>nul
echo [OK] 已清理 failed 目录
echo.

echo [2/3] 清理队列中的任务...
del /q ".jobs\queued\*.json" 2>nul
echo [OK] 已清理 queued 目录
echo.

echo [3/3] 清理草稿任务...
del /q ".jobs\drafted\*.json" 2>nul
echo [OK] 已清理 drafted 目录
echo.

echo ============================================================
echo 清理完成！
echo ============================================================
echo.
echo 现在可以：
echo 1. 重启电脑（让 GPU 库生效）
echo 2. 重新启动 FaceFusion
echo 3. 重新提交任务
echo.
echo 或者如果不想重启：
echo 1. 关闭 FaceFusion
echo 2. 重新运行: 启动FaceFusion.bat
echo 3. 重新提交任务
echo.
echo ============================================================
pause
