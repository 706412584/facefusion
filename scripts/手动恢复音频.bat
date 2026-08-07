@echo off
chcp 65001 >nul
cd /d "%~dp0.."
title 手动恢复音频

echo ============================================================
echo                    手动恢复视频音频
echo ============================================================
echo.
echo 此工具将原视频的音频添加到处理后的无声视频中
echo.

REM 检查 ffmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 ffmpeg
    echo [提示] FaceFusion 应该已经安装了 ffmpeg
    echo [提示] 请确保 Python Scripts 目录在 PATH 中
    pause
    exit /b 1
)

echo [1/3] 请拖入原始视频文件（有音频的）：
set /p SOURCE_VIDEO=
set SOURCE_VIDEO=%SOURCE_VIDEO:"=%
echo.

echo [2/3] 请拖入处理后的视频文件（无音频的）：
set /p TARGET_VIDEO=
set TARGET_VIDEO=%TARGET_VIDEO:"=%
echo.

echo [3/3] 输出文件名（默认：带音频_output.mp4）：
set /p OUTPUT_NAME=
if "%OUTPUT_NAME%"=="" set OUTPUT_NAME=带音频_output.mp4
echo.

echo ============================================================
echo 正在合并音频...
echo ============================================================
echo.
echo 原视频: %SOURCE_VIDEO%
echo 目标视频: %TARGET_VIDEO%
echo 输出文件: %OUTPUT_NAME%
echo.

ffmpeg -i "%TARGET_VIDEO%" -i "%SOURCE_VIDEO%" -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -shortest "%OUTPUT_NAME%" -y

if errorlevel 1 (
    echo.
    echo [错误] 音频合并失败
    echo [提示] 请检查文件路径是否正确
) else (
    echo.
    echo ============================================================
    echo [成功] 音频已恢复！
    echo ============================================================
    echo 输出文件: %OUTPUT_NAME%
)

echo.
pause
