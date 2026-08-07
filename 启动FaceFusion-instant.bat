@echo off
chcp 65001 >nul
title FaceFusion - Instant Runner

echo ============================================================
echo           FaceFusion 启动中 (Instant Runner)
echo ============================================================
echo.

python facefusion.py run --language zh --ui-workflow instant_runner

pause
