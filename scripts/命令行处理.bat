@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title FaceFusion 命令行处理

echo.
echo ============================================================
echo              FaceFusion 命令行处理模式
echo ============================================================
echo.
echo 这个模式绕过 Web 界面，直接处理视频
echo 更稳定，更快速，更容易调试
echo.

set /p SOURCE="请输入源文件路径（人脸照片）: "
set /p TARGET="请输入目标文件路径（视频）: "
set /p OUTPUT="请输入输出文件路径: "

echo.
echo 配置：
echo   源文件: %SOURCE%
echo   目标文件: %TARGET%
echo   输出文件: %OUTPUT%
echo   处理器: face_swapper
echo   执行提供商: CUDA + TensorRT
echo.
pause

echo.
echo 开始处理...
echo.

python facefusion.py run ^
  --source-paths "%SOURCE%" ^
  --target-path "%TARGET%" ^
  --output-path "%OUTPUT%" ^
  --processors face_swapper ^
  --execution-providers cuda tensorrt ^
  --execution-thread-count 8 ^
  --face-selector-mode many

echo.
echo ============================================================
echo 处理完成！
echo ============================================================
echo.
echo 输出文件: %OUTPUT%
echo.
pause
