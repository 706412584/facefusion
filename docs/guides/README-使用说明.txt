FaceFusion 中文版 - 快速使用指南
====================================

## 快速开始

1. 启动 Web 界面
   运行: 启动FaceFusion.bat

2. 启动桌面版
   运行: 启动桌面版.bat

3. 选择启动方式
   运行: 启动器.bat


## GPU 加速配置

你的显卡：RTX 4060

### 方案 1：已安装 cuDNN（推荐）
1. 运行: scripts/验证GPU库安装.bat
2. 检查 cuDNN 是否安装成功
3. 重启电脑
4. 启动 FaceFusion
5. 勾选 CUDA

### 方案 2：完整安装 cuDNN + TensorRT
1. 下载 cuDNN EXE（已下载）
2. 双击安装 cuDNN
3. 下载 TensorRT ZIP
4. 运行: 安装cuDNN和TensorRT-简化版.bat
5. 重启电脑

### 方案 3：快速修复（如果上面都不行）
运行: 修复CUDA缺少库文件.bat


## 检查工具

- 检查显卡类型: scripts/检查显卡.bat
- 详细 GPU 信息: python scripts/check_gpu.py
- 验证安装: scripts/验证GPU库安装.bat


## 文档

- GPU 问题解决: docs/gpu/GPU问题最终解决方案.txt
- GPU 配置指南: docs/gpu/GPU加速配置指南.txt
- cuDNN/TensorRT 安装: 下载cuDNN和TensorRT指南.md
- 多人脸换脸: WebUI多人脸使用指南.md
- 处理流程说明: 处理流程说明.txt


## 当前状态

你的视频：54650 帧（约 30 分钟）
输出路径：C:\Users\70641\Documents

处理速度预估：
- CPU 模式：2-5 帧/秒（3-6 小时）
- CUDA 模式：18-35 帧/秒（30-60 分钟）
- CUDA + TensorRT：20-40 帧/秒（20-45 分钟）


## 下一步

1. 安装完 cuDNN 后，运行: scripts/验证GPU库安装.bat
2. 重启电脑
3. 运行: 启动FaceFusion.bat
4. 勾选 CUDA
5. 开始处理
