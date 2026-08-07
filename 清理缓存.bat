@echo off
chcp 65001 >nul
title 清理缓存

echo ============================================================
echo                    清理 FaceFusion 缓存
echo ============================================================
echo.

echo [1/2] 清理 Gradio 缓存...
if exist ".caches\gradio" (
    rmdir /s /q ".caches\gradio"
    echo [OK] Gradio 缓存已清理
) else (
    echo [提示] Gradio 缓存不存在
)
echo.

echo [2/2] 清理临时文件...
if exist ".caches\facefusion" (
    echo [提示] 临时帧文件夹存在，是否清理？
    echo [警告] 这会删除所有缓存的视频帧
    choice /c YN /m "确认清理"
    if errorlevel 2 (
        echo [取消] 保留临时帧
    ) else (
        rmdir /s /q ".caches\facefusion"
        echo [OK] 临时帧已清理
    )
) else (
    echo [提示] 临时帧不存在
)
echo.

echo ============================================================
echo 清理完成
echo ============================================================
pause
