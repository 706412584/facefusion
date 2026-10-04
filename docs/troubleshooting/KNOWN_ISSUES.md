# 已知问题索引

> 整理自本地运维文档，**非实时 bug 列表**。有新复现时请附日志后再开诊断。  
> 日期：2026-10-05（3.9.1 合并后更新）

## 1. 任务 / 工作流

| 现象 | 常见原因 | 文档 |
|------|----------|------|
| job_runner 任务编号显示 `none` | job_runner **不创建**任务，只跑队列 | [工作流程完整说明](../workflows/FaceFusion工作流程完整说明.md) |
| 点开始无反应 / 任务失败 | 未提交 step、输出路径无效、处理器未勾选 | [任务失败诊断](任务失败诊断.txt) |
| 分析 100% 后停住、无输出 | **出片前 NSFW 内容检测**（看 rate>10）；上游合并易冲掉本地补丁 | [内容检测问题说明](../guides/内容检测问题说明.txt) |
| 输出 0 字节、退出码 1，日志却"成功" | **flac 音轨写入 mp4** 被判实验特性；`concat_video` 最易漏 `-strict -2` | [instant_runner使用说明](../workflows/instant_runner使用说明.txt) 的"flac 音频坑" |
| 不知用哪种 workflow | 新手用 instant_runner | [工作流程切换指南](../workflows/工作流程切换指南.txt) |

**建议**：日常用 `启动FaceFusion.bat`（instant_runner）；批量用 job_manager → job_runner。

## 2. GPU / 加速

| 现象 | 常见原因 | 文档 / 脚本 |
|------|----------|-------------|
| 只有 CPU、CUDA 不亮 | onnxruntime 无 CUDA EP、驱动/cuDNN 路径 | [GPU加速配置指南](../gpu/GPU加速配置指南.txt)、`scripts/检查GPU是否工作.bat` |
| TensorRT 装了仍不可用 | 版本与 CUDA 不匹配、DLL 未进 PATH | [GPU问题最终解决方案](../gpu/GPU问题最终解决方案.txt)、`scripts/验证GPU库安装.bat` |
| 首次很慢 | 模型下载 / TensorRT 引擎编译 | 配置代理：`scripts/setup_proxy.py`（启动 bat 会自动探测） |

**本机历史配置备忘**（文档中记载，以你机器实测为准）：RTX 4060、CUDA 12.x、cuDNN 9.x、TensorRT 10.x。

## 3. 换脸质量 / 预览

| 现象 | 常见原因 | 文档 |
|------|----------|------|
| 个别帧花脸、偏脸、没换上 | 检测阈值/角度、参考脸距离、遮罩 | [换脸质量问题说明](../guides/换脸质量问题说明.md) |
| 预览改了出片没改 | 旧版本；现已有 frame override 出片链路 | [frame-override-plan](../development/frame-override-plan.md) |
| 多人脸串脸 | 选择器 reference / one / many 配置 | [WebUI多人脸](../webui/WebUI多人脸使用指南.md) |

**定制能力**：疑难帧三层覆盖（单帧 > 区间 > 全局），见 development 方案；UI 在 repair / diagnostics。

## 4. 内容检测

| 现象 | 说明 | 文档 |
|------|------|------|
| 内容分析拦截处理 | 本地版相关说明与禁用说明 | [内容检测问题说明](../guides/内容检测问题说明.txt)、[已禁用内容检测说明](../guides/已禁用内容检测说明.txt) |

## 5. 打包 / 仓库

| 现象 | 说明 |
|------|------|
| 推送 GitHub 被拒（>100MB） | 勿提交 `dist/`、`build/`、`facefusion/out/`；已 ignore 并清历史 |
| 打包体积 ~1GB | 正常；见 [packaging/QUICK_START](../packaging/QUICK_START.txt) |

## 6. 尚无自动复现的项

当前会话**没有**附带新的失败日志或最小复现。若要做第 5 项「真机诊断」，请提供：

1. 完整报错 / 终端日志  
2. 源图、目标视频类型（分辨率、时长、是否多人）  
3. 处理器列表与 execution providers  
4. 是否只预览坏、还是出片也坏  

## 快速自检命令

```bat
scripts\检查GPU是否工作.bat
scripts\验证GPU库安装.bat
scripts\诊断启动问题.bat
python scripts\check_gpu.py
```
