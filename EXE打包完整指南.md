# FaceFusion EXE 打包完整指南

## 📦 一键打包

### 最简单的方法

1. 双击运行 `build.bat`
2. 等待打包完成
3. 在 `dist/FaceFusion/` 目录找到可执行文件

就这么简单！

## 🔧 详细步骤

### 准备工作

#### 1. 检查 Python 环境

```bash
python --version
# 应该显示 Python 3.10 或更高版本
```

#### 2. 安装项目依赖

```bash
pip install -r requirements.txt
```

#### 3. 安装打包工具

```bash
pip install pyinstaller
```

### 开始打包

#### 方法 A：自动打包（推荐）

```bash
# Windows
build.bat

# 或使用 Python 脚本
python build_exe.py
```

#### 方法 B：手动打包

```bash
# 1. 清理旧文件
rmdir /s /q build dist
del facefusion.spec

# 2. 使用 spec 文件打包
pyinstaller --clean --noconfirm facefusion_simple.spec

# 3. 测试程序
cd dist\FaceFusion
FaceFusion.exe run --language zh
```

## 📁 打包后的文件

```
dist/FaceFusion/
├── FaceFusion.exe          # 主程序 (约 50MB)
├── _internal/              # 依赖文件 (约 800MB)
│   ├── facefusion/
│   ├── gradio/
│   ├── cv2/
│   ├── numpy/
│   ├── onnxruntime/
│   └── ...
└── README.txt              # 使用说明
```

**总大小**: 约 850MB - 1GB

## 🚀 使用打包后的程序

### 基本使用

```bash
# 启动中文界面
FaceFusion.exe run --language zh

# 启动英文界面
FaceFusion.exe run --language en

# 命令行处理
FaceFusion.exe headless-run --language zh -s source.jpg -t target.mp4 -o output.mp4
```

### 创建桌面快捷方式

1. 右键 `FaceFusion.exe` → 发送到 → 桌面快捷方式
2. 右键快捷方式 → 属性
3. 在"目标"后添加参数：
   ```
   "C:\path\to\FaceFusion.exe" run --language zh
   ```

## ⚙️ 高级配置

### 自定义打包选项

编辑 `facefusion_simple.spec` 文件：

#### 1. 隐藏控制台窗口

```python
exe = EXE(
    ...
    console=False,  # 改为 False
    ...
)
```

#### 2. 修改程序图标

```python
exe = EXE(
    ...
    icon='your_icon.ico',
)
```

#### 3. 添加版本信息

创建 `version.txt`:

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(3, 0, 0, 0),
    prodvers=(3, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'FaceFusion'),
        StringStruct(u'FileDescription', u'Face Manipulation Platform'),
        StringStruct(u'FileVersion', u'3.0.0'),
        StringStruct(u'InternalName', u'FaceFusion'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
        StringStruct(u'OriginalFilename', u'FaceFusion.exe'),
        StringStruct(u'ProductName', u'FaceFusion'),
        StringStruct(u'ProductVersion', u'3.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

然后在 spec 文件中添加：

```python
exe = EXE(
    ...
    version='version.txt',
)
```

### 优化打包体积

#### 1. 排除不需要的模块

```python
excludes=[
    'matplotlib',
    'tkinter',
    'PyQt5',
    'PyQt6',
    'pandas',
    'jupyter',
    'IPython',
    'sphinx',
    'pytest',
]
```

#### 2. 使用 UPX 压缩

```bash
# 下载 UPX: https://upx.github.io/
# 将 upx.exe 放到 PATH 或 PyInstaller 目录

# 在 spec 文件中启用
upx=True
```

#### 3. 只打包必要的 ONNX Runtime

如果只需要 CPU 版本：

```bash
pip uninstall onnxruntime-gpu
pip install onnxruntime
```

## 🐛 常见问题解决

### 问题 1: 打包失败 - 找不到模块

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方法**:
```python
# 在 spec 文件的 hiddenimports 中添加
hiddenimports = [
    ...
    'missing_module',
]
```

### 问题 2: 运行时错误 - 找不到文件

**错误信息**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'xxx'
```

**解决方法**:
```python
# 在 spec 文件的 datas 中添加
datas = [
    ('source_file_or_folder', 'destination_in_exe'),
]
```

### 问题 3: 程序启动慢

**原因**: 单文件模式需要解压

**解决方法**: 使用文件夹模式（当前默认配置）

### 问题 4: 杀毒软件误报

**解决方法**:
1. 添加到杀毒软件白名单
2. 使用代码签名证书签名程序
3. 上传到 VirusTotal 建立信誉

### 问题 5: ONNX Runtime 错误

**错误信息**:
```
Failed to load ONNX Runtime
```

**解决方法**:
1. 确保 ONNX Runtime 版本正确
2. 检查是否需要 GPU 支持
3. 安装 Visual C++ Redistributable

### 问题 6: Gradio 界面无法打开

**解决方法**:
1. 检查防火墙设置
2. 手动指定端口: `--server-port 7860`
3. 确保收集了 Gradio 的所有资源文件

## 📦 创建安装程序

### 使用 Inno Setup

1. 下载 Inno Setup: https://jrsoftware.org/isinfo.php

2. 创建 `installer.iss`:

```iss
[Setup]
AppName=FaceFusion
AppVersion=3.0
DefaultDirName={pf}\FaceFusion
DefaultGroupName=FaceFusion
OutputDir=installer
OutputBaseFilename=FaceFusion-Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\FaceFusion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\FaceFusion"; Filename: "{app}\FaceFusion.exe"
Name: "{group}\FaceFusion (中文)"; Filename: "{app}\FaceFusion.exe"; Parameters: "run --language zh"
Name: "{commondesktop}\FaceFusion"; Filename: "{app}\FaceFusion.exe"

[Run]
Filename: "{app}\FaceFusion.exe"; Description: "启动 FaceFusion"; Flags: postinstall nowait skipifsilent
```

3. 编译安装程序:
```bash
iscc installer.iss
```

## 🔐 代码签名

### 获取证书

1. 购买代码签名证书（如 DigiCert, Sectigo）
2. 或使用自签名证书（测试用）

### 签名程序

```bash
# 使用 signtool (Windows SDK)
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com /fd SHA256 FaceFusion.exe
```

## 📊 性能对比

| 配置 | 文件大小 | 启动时间 | 优点 | 缺点 |
|------|---------|---------|------|------|
| 文件夹模式 | ~850MB | 快 (2-3秒) | 启动快，易更新 | 文件多 |
| 单文件模式 | ~900MB | 慢 (10-15秒) | 单个文件 | 启动慢 |
| 压缩模式 | ~600MB | 中等 (5-8秒) | 体积小 | 兼容性 |

**推荐**: 文件夹模式（当前配置）

## 📝 分发清单

打包完成后，分发时应包含：

- [ ] `FaceFusion.exe` 和 `_internal/` 文件夹
- [ ] `README.txt` 使用说明
- [ ] `LICENSE.md` 许可证文件
- [ ] 系统要求说明
- [ ] 安装 Visual C++ Redistributable 的链接
- [ ] 首次运行指南

## 🎯 测试清单

打包后必须测试：

- [ ] 程序能正常启动
- [ ] 中文界面显示正常
- [ ] 英文界面显示正常
- [ ] 文件选择功能正常
- [ ] 图像处理功能正常
- [ ] 视频处理功能正常
- [ ] 模型自动下载正常
- [ ] 日志输出正常
- [ ] 程序能正常退出
- [ ] 在干净的 Windows 系统上测试

## 💡 最佳实践

1. **使用虚拟环境打包**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pyinstaller facefusion_simple.spec
   ```

2. **定期更新依赖**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

3. **版本控制**
   - 为每个版本创建 Git 标签
   - 记录打包配置的变更

4. **自动化打包**
   - 使用 CI/CD 自动打包
   - 创建 GitHub Actions 工作流

## 🔗 相关资源

- PyInstaller 官方文档: https://pyinstaller.org/
- Gradio 文档: https://www.gradio.app/
- ONNX Runtime 文档: https://onnxruntime.ai/
- Inno Setup 文档: https://jrsoftware.org/ishelp/

## 📞 获取帮助

如遇到问题：

1. 查看 `build/FaceFusion/warn-FaceFusion.txt` 日志
2. 使用 `--debug all` 参数获取详细信息
3. 在项目 Issues 中搜索类似问题
4. 提交新的 Issue 并附上日志

---

**祝你打包顺利！** 🎉
