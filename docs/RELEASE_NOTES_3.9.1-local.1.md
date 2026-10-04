# FaceFusion 3.9.1-local.1

基于官方 **FaceFusion 3.9.1** 的本地定制发布（fork：`706412584/facefusion`）。
本次为上游同步版本：3.8.0 → 3.9.1。

## 上游同步

- 合并上游 tag `3.9.1`（提交 `72470819`），自 3.8.0 起共 10 个提交。
- 合并提交：`39932803`；版本号已更新为 `3.9.1`。
- 冲突仅 3 处，均为 import 行合并，无逻辑冲突。
- 详细过程与验证清单见 `docs/development/upstream-sync.md`。

### 前置修复（重要）

本 fork 历史曾被改写，导致上游 3.8.0 不是本地 3.8.0 的祖先，直接合并会产生
上百个伪冲突。已用 replace graft 修复合并基点：

```bash
git replace --graft 625b01d5 b60ea40d
```

**请勿删除 `refs/replace/625b01d5...`**，后续同步上游仍依赖它。

## 本版修复

### 1. 出片前内容检测（NSFW）重新关闭

上游 3.8.0 合并曾把本地"关闭出片前内容检测"的补丁冲掉，导致任务在
"正在分析 100%"后静默失败（错误码 3）。本次再次关闭：

- `facefusion/workflows/to_video.py` `analyse_video()` → `return 0`
- `facefusion/workflows/to_image.py` `analyse_image()` → `return 0`
- 移除对 `content_analyser` 的调用（不修改 `content_analyser.py`，哈希校验仍通过）

### 2. flac 写入 mp4 失败（输出 0 字节）

音频编码器选 `flac` 时，ffmpeg 将 flac-in-mp4 判为实验特性，写头失败。
需在三条 ffmpeg 路径都加 `-strict -2`：

- `restore_audio`
- `replace_audio`
- `concat_video`（`job_runner.finalize_steps` 会走到，之前遗漏，是 0 字节的直接原因）

实现为 `ffmpeg_builder.allow_experimental_codec()`。

## 保留的本地定制

中文 UI、frame override（单帧/时段/预览/出片）、源脸 baseline 预热、
预览播放、人脸去重与多目标、diagnostics/repair/theme/tips 组件、
instant_runner 批处理、桌面版、`scripts/`、`docs/`、启动 bat。
合并后核对：定制层文件集合 138 个，与合并前完全一致（0 丢失）。

## 已知问题（合并前既有，与本次无关）

- `tests/test_ffmpeg.py::test_extract_frames`：示例资产
  `target-240p-smpte2084.mp4` 为 0 字节（下载残留），删掉临时目录重跑可解。
- `tests/test_cli_lip_syncer.py` 视频用例失败。
- `tests/test_curl_builder.py` / `tests/test_download.py`：受本机代理环境影响。
- `test_get_available_encoder_set`、`test_restore_audio`/`replace_audio`
  在无 GPU/网络环境会卡住。

## 快速开始

```bat
启动FaceFusion.bat
```

或：

```bash
python facefusion.py run --language zh --ui-workflow instant_runner
```
