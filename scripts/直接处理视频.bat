@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title 直接处理视频

echo.
echo ============================================================
echo              直接处理视频（命令行模式）
echo ============================================================
echo.
echo 这个模式绕过 Web 界面，直接处理
echo 更稳定，更容易看到错误信息
echo.

set /p SOURCE="源文件路径（人脸照片）: "
set /p TARGET="目标文件路径（视频）: "
set /p OUTPUT="输出文件路径: "

echo.
echo 开始处理...
echo   源: %SOURCE%
echo   目标: %TARGET%
echo   输出: %OUTPUT%
echo.

python facefusion.py run ^
  --source-paths "%SOURCE%" ^
  --target-path "%TARGET%" ^
  --output-path "%OUTPUT%" ^
  --processors face_swapper ^
  --execution-providers cuda ^
  --execution-thread-count 4 ^
  --face-selector-mode many ^
  --log-level info

echo.
echo ============================================================
if exist "%OUTPUT%" (
    echo 处理完成！
    echo 输出文件: %OUTPUT%
) else (
    echo 处理失败，请查看上面的错误信息
)
echo ============================================================
pause
