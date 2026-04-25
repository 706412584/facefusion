@echo off
chcp 65001 >nul
title FaceFusion 启动器

:menu
cls
echo ============================================================
echo                    FaceFusion 启动器
echo ============================================================
echo.
echo 请选择启动方式:
echo.
echo [1] 启动中文界面
echo [2] 启动英文界面
echo [3] 无头模式（命令行处理）
echo [4] 查看帮助
echo [5] 退出
echo.
echo ============================================================
set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" goto chinese
if "%choice%"=="2" goto english
if "%choice%"=="3" goto headless
if "%choice%"=="4" goto help
if "%choice%"=="5" goto end
goto menu

:chinese
cls
echo 正在启动中文界面...
python facefusion.py run --language zh
pause
goto menu

:english
cls
echo Starting English interface...
python facefusion.py run --language en
pause
goto menu

:headless
cls
echo ============================================================
echo 无头模式 - 命令行处理
echo ============================================================
echo.
echo 示例命令:
echo python facefusion.py headless-run --language zh -s source.jpg -t target.mp4 -o output.mp4
echo.
set /p source=请输入源文件路径: 
set /p target=请输入目标文件路径: 
set /p output=请输入输出文件路径: 
echo.
echo 正在处理...
python facefusion.py headless-run --language zh -s "%source%" -t "%target%" -o "%output%"
echo.
pause
goto menu

:help
cls
python facefusion.py --help
pause
goto menu

:end
exit
