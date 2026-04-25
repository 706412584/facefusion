@echo off
chcp 65001 >nul
echo ============================================================
echo FaceFusion 打包工具
echo ============================================================
echo.

echo [1/3] 检查 PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
) else (
    echo ✓ PyInstaller 已安装
)
echo.

echo [2/3] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✓ 清理完成
echo.

echo [3/3] 开始打包...
python -m PyInstaller --clean --noconfirm facefusion_simple.spec
echo.

if exist dist\FaceFusion\FaceFusion.exe (
    echo ============================================================
    echo ✓ 打包完成！
    echo ============================================================
    echo.
    echo 可执行文件位置: dist\FaceFusion\FaceFusion.exe
    echo.
    echo 测试运行:
    echo   cd dist\FaceFusion
    echo   FaceFusion.exe run --language zh
) else (
    echo ============================================================
    echo ✗ 打包失败，请检查错误信息
    echo ============================================================
)
echo.
pause
