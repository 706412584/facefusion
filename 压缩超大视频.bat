@echo off
chcp 65001 >nul
title 压缩超大视频

echo ============================================================
echo                    压缩超大视频工具
echo ============================================================
echo.
echo 此工具将超大视频压缩到正常大小
echo.
echo [重要提示] 请先关闭以下程序：
echo   - 视频播放器
echo   - FaceFusion 程序
echo   - 文件资源管理器预览
echo.
pause
echo.

REM 检查 ffmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 ffmpeg
    pause
    exit /b 1
)

echo [1/2] 请拖入要压缩的视频文件：
set /p INPUT_VIDEO=
set INPUT_VIDEO=%INPUT_VIDEO:"=%
echo.

echo [2/2] 输出文件名（默认：压缩_output.mp4）：
set /p OUTPUT_NAME=
if "%OUTPUT_NAME%"=="" set OUTPUT_NAME=压缩_output.mp4
echo.

REM 检查文件是否被占用
echo [检查] 测试文件访问权限...
copy "%INPUT_VIDEO%" "%INPUT_VIDEO%.test" >nul 2>&1
if errorlevel 1 (
    echo [错误] 文件被占用或无法访问
    echo [提示] 请关闭所有使用该文件的程序后重试
    echo.
    pause
    exit /b 1
) else (
    del "%INPUT_VIDEO%.test" >nul 2>&1
    echo [OK] 文件可以访问
)
echo.

echo ============================================================
echo 正在压缩视频...
echo ============================================================
echo.
echo 输入: %INPUT_VIDEO%
echo 输出: %OUTPUT_NAME%
echo.
echo [提示] 这可能需要一些时间，请耐心等待...
echo.

REM 压缩到 1280x720，高质量 H.264
ffmpeg -i "%INPUT_VIDEO%" -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k "%OUTPUT_NAME%" -y

if errorlevel 1 (
    echo.
    echo [错误] 压缩失败
    echo [提示] 可能的原因：
    echo   1. 文件仍被占用
    echo   2. 磁盘空间不足
    echo   3. 文件损坏
) else (
    echo.
    echo ============================================================
    echo [成功] 视频已压缩！
    echo ============================================================
    echo 输出文件: %OUTPUT_NAME%
    echo.
    
    REM 显示文件大小对比
    for %%A in ("%INPUT_VIDEO%") do set INPUT_SIZE=%%~zA
    for %%A in ("%OUTPUT_NAME%") do set OUTPUT_SIZE=%%~zA
    echo 原始大小: %INPUT_SIZE% 字节
    echo 压缩后: %OUTPUT_SIZE% 字节
)

echo.
pause
