# FaceFusion 3.8.0-local.1

基于官方 **FaceFusion 3.8.0** 的本地定制发布（fork：`706412584/facefusion`）。

## 本版相对官方的主要变化

### 功能

- **疑难帧三层 Override**（单帧 > 区间 > 全局）  
  - 预览 / 播放 / 出片同一套规则  
  - 可 `skip_swap` / `skip_process`  
  - 规则可写入 job step，出片时生效  
  - 源/参考脸在 override 下保持 baseline，避免缓存污染  
- **WebUI 诊断与修复**：diagnostics、repair_options、控件提示  
- **中文界面**：`--language zh`，启动脚本默认中文 + instant_runner

### 仓库与工程

- 运维脚本集中到 `scripts/`  
- 中文文档集中到 `docs/`  
- `.gitignore` 排除 `dist/`、`build/`、`facefusion/out/`、`.cursor`、`*.db`、`*.rar` 等  
- 历史中超大 PyInstaller / 输出包已剔除，可正常推送 GitHub

### 未包含

- **不**附带 `dist/` 预编译 exe（体积过大且含第三方二进制）  
- **不**附带模型权重（首次运行按官方逻辑下载）  
- 非完整 NLE 时间线；override 白名单参数见 development 方案

## 快速开始

```bat
启动FaceFusion.bat
```

或：

```bash
python facefusion.py run --language zh --ui-workflow instant_runner
```

文档入口：`docs/README.md`

## 系统依赖

- Python ≥ 3.10  
- curl、ffmpeg、ffprobe  
- 可选：CUDA / cuDNN / TensorRT（见 `docs/gpu/`）

## 验证建议

1. WebUI 上传源脸 + 目标视频，instant_runner 跑通一小段  
2. 勾选 CUDA（若环境支持），`scripts/检查GPU是否工作.bat`  
3. 对坏帧设单帧/区间 override，确认预览与出片一致  
4. 可选：`pytest tests/test_frame_override.py`（若环境已装测试依赖）

## Tag

- `v3.8.0-local.1`
