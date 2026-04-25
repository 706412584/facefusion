# -*- mode: python ; coding: utf-8 -*-
"""
FaceFusion PyInstaller 配置文件
用于打包成 Windows 可执行文件
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

# 收集 ONNX Runtime 的动态库（关键！）
onnx_binaries = collect_dynamic_libs('onnxruntime')

# 收集数据文件
try:
    gradio_datas = collect_data_files('gradio')
except:
    gradio_datas = []

try:
    gradio_rangeslider_datas = collect_data_files('gradio_rangeslider')
except:
    gradio_rangeslider_datas = []

try:
    onnx_datas = collect_data_files('onnxruntime')
except:
    onnx_datas = []

# 项目数据文件
project_datas = [
    ('facefusion/uis/assets', 'facefusion/uis/assets'),
]

# 如果有图标文件
if os.path.exists('facefusion.ico'):
    project_datas.append(('facefusion.ico', '.'))

# 合并所有数据文件
datas = gradio_datas + gradio_rangeslider_datas + onnx_datas + project_datas

# 收集所有子模块
hiddenimports = [
    # Gradio 相关
    'gradio',
    'gradio_rangeslider',
    'gradio.components',
    'gradio.themes',
    'gradio.processing_utils',
    'gradio.blocks',
    'gradio.routes',
    
    # 核心依赖
    'onnxruntime',
    'cv2',
    'numpy',
    'scipy',
    'tqdm',
    'PIL',
    'PIL.Image',
    
    # FaceFusion 模块
    'facefusion',
    'facefusion.uis.core',
    'facefusion.uis.layouts.default',
    'facefusion.uis.layouts.webcam',
    'facefusion.uis.layouts.benchmark',
    'facefusion.uis.layouts.jobs',
    
    # 处理器模块
    'facefusion.processors.core',
] + collect_submodules('facefusion.processors.modules')

a = Analysis(
    ['facefusion.py'],
    pathex=[],
    binaries=onnx_binaries,  # 添加 ONNX Runtime 二进制文件
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FaceFusion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 改为 False 可隐藏控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='facefusion.ico' if os.path.exists('facefusion.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FaceFusion',
)
