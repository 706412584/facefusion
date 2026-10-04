FaceFusion（本地定制）
====================

> 基于 [官方 FaceFusion](https://github.com/facefusion/facefusion) **3.9.1** 的 fork：中文 UI、疑难帧 override、本机运维脚本与文档。

[![License](https://img.shields.io/badge/license-OpenRAIL--AS-green)](LICENSE.md)

本仓库远程：`https://github.com/706412584/facefusion`


快速开始
--------

**WebUI（推荐）**

```bat
启动FaceFusion.bat
```

默认：`--language zh`、`instant_runner`。

**桌面版**

```bat
启动桌面版.bat
```

**命令行**

```bash
python facefusion.py run --language zh --ui-workflow instant_runner
python facefusion.py headless-run --language zh -s source.jpg -t target.mp4 -o output.mp4 --processors face_swapper
```

依赖：Python ≥ 3.10，以及系统中的 `curl` / `ffmpeg` / `ffprobe`。Python 包见 `requirements.txt`。


本 fork 要点
------------

| 能力 | 说明 |
|------|------|
| 中文界面 | 启动脚本与 `--language zh` |
| 帧级修复 | 单帧 / 区间 / 全局 override，预览与出片一致 |
| 文档 | 全部在 [`docs/`](docs/README.md) |
| 运维脚本 | [`scripts/`](scripts/)（GPU 检查、安装、清理、压缩等） |
| 上游同步 | [`docs/development/upstream-sync.md`](docs/development/upstream-sync.md) |


目录约定
--------

```
├── 启动FaceFusion.bat      # WebUI
├── 启动桌面版.bat
├── 启动器.bat / 启动FaceFusion-instant.bat
├── facefusion.py           # CLI 入口
├── facefusion/             # 核心代码
├── docs/                   # 中文文档与开发笔记
├── scripts/                # 运维与诊断脚本
├── tests/                  # 测试
├── build.bat / build_exe.py
└── requirements.txt
```

**不要提交**：`dist/`、`build/`、`facefusion/out/`、`.caches/`、`.jobs/`、大体积模型与 rar。


官方命令一览
------------

```
python facefusion.py [commands] [options]

commands:
    run | headless-run | batch-run | force-download | benchmark
    job-list | job-create | job-submit | job-submit-all
    job-delete | job-delete-all
    job-add-step | job-remix-step | job-insert-step | job-remove-step
    job-run | job-run-all | job-retry | job-retry-all
```

完整说明见 [docs.facefusion.io](https://docs.facefusion.io) 与本地 [`docs/README.md`](docs/README.md)。


版本
----

- 上游基线：FaceFusion **3.9.1**（合并提交 `39932803`，2026-10-05）
- 本 fork 发布说明：见 `docs/RELEASE_NOTES_3.9.1-local.1.md`
- 上一版：`docs/RELEASE_NOTES_3.8.0-local.1.md` / tag `v3.8.0-local.1`
