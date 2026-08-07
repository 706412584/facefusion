# FaceFusion 本地定制文档

本目录存放中文操作说明、故障排查与开发笔记。根目录只保留启动脚本与上游入口。

## 目录

| 目录 | 内容 |
|------|------|
| [guides/](guides/) | 快速使用、处理流程、源/目标文件、质量与内容检测说明 |
| [webui/](webui/) | WebUI 操作、多人脸、界面位置 |
| [workflows/](workflows/) | instant_runner / job_manager / job_runner |
| [gpu/](gpu/) | CUDA / cuDNN / TensorRT 配置与排障 |
| [troubleshooting/](troubleshooting/) | 任务失败、已知问题索引 |
| [packaging/](packaging/) | 打包 EXE 快速指南 |
| [development/](development/) | 开发方案（frame override 等）、上游同步 |

## 常用入口

- 启动 WebUI：根目录 `启动FaceFusion.bat`
- 启动桌面版：根目录 `启动桌面版.bat`
- 运维脚本：`scripts/`
- 上游同步：见 [development/upstream-sync.md](development/upstream-sync.md)
- 已知问题：见 [troubleshooting/KNOWN_ISSUES.md](troubleshooting/KNOWN_ISSUES.md)
