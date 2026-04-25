# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 收集所有需要的数据文件
datas = [
    ('facefusion/uis/assets', 'facefusion/uis/assets'),
    ('facefusion.ico', '.'),
]

# 收集隐藏导入
hiddenimports = [
    'gradio',
    'gradio_rangeslider',
    'onnxruntime',
    'cv2',
    'numpy',
    'scipy',
    'tqdm',
    'PIL',
    'PIL.Image',
    'gradio.components',
    'gradio.themes',
    'gradio.processing_utils',
    'facefusion.uis.core',
    'facefusion.uis.layouts.default',
    'facefusion.uis.layouts.webcam',
    'facefusion.uis.layouts.benchmark',
    'facefusion.uis.layouts.jobs',
    'facefusion.processors.modules.face_swapper.core',
    'facefusion.processors.modules.face_enhancer.core',
    'facefusion.processors.modules.frame_enhancer.core',
    'facefusion.processors.modules.face_debugger.core',
    'facefusion.processors.modules.face_editor.core',
    'facefusion.processors.modules.lip_syncer.core',
    'facefusion.processors.modules.age_modifier.core',
    'facefusion.processors.modules.expression_restorer.core',
    'facefusion.processors.modules.frame_colorizer.core',
    'facefusion.processors.modules.background_remover.core',
    'facefusion.processors.modules.deep_swapper.core',
]

a = Analysis(
    ['facefusion.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=True,  # 设置为 False 可以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='facefusion.ico',
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
