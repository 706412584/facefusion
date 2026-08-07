@echo off
chcp 65001 >nul
title 诊断 GPU 和处理问题

echo.
echo ============================================================
echo              诊断 GPU 和处理问题
echo ============================================================
echo.

echo [1] 检查 Python 和 ONNX Runtime...
python -c "import sys; print('Python:', sys.version)"
echo.

echo [2] 检查 ONNX Runtime 提供商...
python -c "try: import onnxruntime as ort; print('ONNX Runtime:', ort.__version__); providers = ort.get_available_providers(); print('可用提供商:', providers); print(''); print('状态:'); print('  CPU:', 'OK' if 'CPUExecutionProvider