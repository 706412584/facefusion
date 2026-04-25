"""
FaceFusion 打包脚本
用于将 FaceFusion 打包成 Windows 可执行文件
"""

import os
import sys
import shutil
import subprocess

def check_pyinstaller():
    """检查并安装 PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")

def create_spec_file():
    """创建 PyInstaller spec 文件"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

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
"""
    
    with open('facefusion.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ 已创建 facefusion.spec 文件")

def build_exe():
    """执行打包"""
    print("\n开始打包...")
    print("=" * 60)
    
    # 运行 PyInstaller（使用 python -m 方式）
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--clean',
        '--noconfirm',
        'facefusion.spec'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print("✓ 打包完成！")
        print("=" * 60)
        print("\n可执行文件位置: dist/FaceFusion/FaceFusion.exe")
        print("\n注意事项:")
        print("1. 首次运行需要下载 AI 模型文件")
        print("2. 需要将整个 dist/FaceFusion 文件夹一起分发")
        print("3. 如需使用 GPU，确保目标机器安装了对应的驱动")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 打包失败: {e}")
        return False
    
    return True

def create_readme():
    """创建使用说明"""
    readme_content = """# FaceFusion 可执行文件使用说明

## 运行方式

### 方法 1: 双击运行
直接双击 `FaceFusion.exe` 启动程序

### 方法 2: 命令行运行

打开命令提示符（CMD）或 PowerShell，进入程序目录：

```cmd
# 启动界面（中文）
FaceFusion.exe run --language zh

# 启动界面（英文）
FaceFusion.exe run --language en

# 无头模式处理
FaceFusion.exe headless-run --language zh -s source.jpg -t target.mp4 -o output.mp4

# 查看帮助
FaceFusion.exe --help
```

## 系统要求

- Windows 10/11 (64位)
- 至少 8GB 内存
- 推荐使用 NVIDIA GPU（可选，用于加速）

## 首次运行

首次运行时，程序会自动下载所需的 AI 模型文件，请保持网络连接。

## 常见问题

### 1. 程序无法启动
- 确保所有文件都在同一目录
- 检查是否有杀毒软件拦截
- 尝试以管理员身份运行

### 2. 缺少 DLL 文件
- 安装 Visual C++ Redistributable
- 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe

### 3. GPU 加速不可用
- 安装最新的 NVIDIA 驱动
- 确保 CUDA 版本兼容

## 文件结构

```
FaceFusion/
├── FaceFusion.exe          # 主程序
├── _internal/              # 依赖文件（不要删除）
├── facefusion.ico          # 图标文件
└── README.txt              # 本说明文件
```

## 技术支持

如遇问题，请访问项目主页获取帮助。
"""
    
    os.makedirs('dist/FaceFusion', exist_ok=True)
    with open('dist/FaceFusion/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✓ 已创建使用说明文件")

def main():
    print("=" * 60)
    print("FaceFusion 打包工具")
    print("=" * 60)
    print()
    
    # 检查环境
    print("1. 检查环境...")
    check_pyinstaller()
    print()
    
    # 创建 spec 文件
    print("2. 创建配置文件...")
    create_spec_file()
    print()
    
    # 执行打包
    print("3. 开始打包...")
    if build_exe():
        print()
        print("4. 创建说明文件...")
        create_readme()
        print()
        print("=" * 60)
        print("✓ 所有步骤完成！")
        print("=" * 60)
    else:
        print("\n打包过程中出现错误，请检查日志。")

if __name__ == '__main__':
    main()
