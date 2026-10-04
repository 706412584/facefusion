# 与官方上游同步

本仓库 `origin` 指向 fork：`https://github.com/706412584/facefusion.git`  
官方上游应配置为 `upstream`：`https://github.com/facefusion/facefusion.git`

## 一次性配置

```bash
git remote add upstream https://github.com/facefusion/facefusion.git
# 若已存在可改 URL：
# git remote set-url upstream https://github.com/facefusion/facefusion.git

git remote -v
```

期望类似：

```
origin    https://github.com/706412584/facefusion.git (fetch/push)
upstream  https://github.com/facefusion/facefusion.git (fetch)
```

建议：**不要**对 `upstream` 执行 `git push`（无写权限或易误推）。

---

## ⚠️ 本 fork 历史特殊性（合并前必读）

本 fork 的提交历史曾被改写过，上游 3.8.0 的官方提交 **不是** 本仓库 3.8.0 的祖先。具体表现：

- 本地标签 `3.8.0` 指向 `625b01d5`（上游 3.8.0 的树 + 本地补丁），**不是**上游的 `3.8.0`（`b60ea40d`）。
- 二者的 **tree 完全一致**（仅 SHA 不同），因为 `f370c1dd` 这类"merge"其实是单亲提交（`git log --parents` 可验证）。
- 直接 `git merge upstream/master` 会以远古提交（3.5.x 时代）为合并基点，产生 **上百个伪冲突**。

### 解决办法：用 replace graft 把 fork 的 3.8.0 接回上游 3.8.0

```bash
# 一次性执行（本仓库已执行，refs/replace/625b01d5... 已存在，请勿删除）
git replace --graft 625b01d5 b60ea40d
```

执行后合并基点回到真实上游 3.8.0，冲突数从 100+ 降到个位数。

**注意：**

- `git fetch upstream --tags` 时，本地 `3.8.0`/`3.8.1` 等标签会与上游同名标签冲突（`would clobber existing tag`）。这是预期现象，不要用 `--force` 覆盖本地标签；需要上游标签时用 `git fetch upstream refs/tags/<tag>:refs/tags/up-<tag>` 取到带前缀的名字。
- 建议长期保留该 graft，后续每次同步上游都依赖它。
- 如需查看是否生效：`git merge-base master <upstream-tag>` 应落在真实上游提交上。

---

## 常规同步流程（推荐）

本地有大量定制（中文 UI、frame override、scripts/docs）。优先 **merge**，避免 rebase 整段定制历史。

```bash
git fetch upstream
git checkout master

# 查看将要合入的官方提交（用 graft 生效后的基点）
git log --oneline HEAD..<上游标签或 upstream/master> | head -30

# 合并上游（先在独立分支试合，确认后再 ff 到 master）
git checkout -b merge/upstream-<版本>
git merge <上游标签或 upstream/master>

# 解决冲突后
git add <具体文件>          # 不要用 git add -A，会误收 .playwright-mcp/ 等未跟踪文件
git commit                  # 若 merge 已自动生成可省略
git checkout master
git merge --ff-only merge/upstream-<版本>
git branch -d merge/upstream-<版本>
git push origin master
```

### 冲突高发区（本 fork）

合并时重点检查：

- `facefusion/locales.py` / `translator.py`（中文）
- `facefusion/uis/components/*`（repair、diagnostics、preview）
- `facefusion/frame_override.py`、`state_manager.py`、`workflows/core.py`
- `facefusion/core.py`（language 路由）
- 根目录启动 bat、`.gitignore`

冲突原则：**保留本 fork 定制行为**，再手工接入上游 bugfix / API 变更。

### 易被上游覆盖的本地补丁（务必逐次核对）

上游会周期性"恢复"这些行为，合并时极易把本地改动冲掉：

| 本地补丁 | 位置 | 期望状态 |
|---|---|---|
| 出片前关闭 NSFW 内容检测 | `workflows/to_video.py` `analyse_video()`、`workflows/to_image.py` `analyse_image()` | 函数体 `return 0`，且**不** import `content_analyser` |
| flac 写入 mp4 需 `-strict -2` | `ffmpeg_builder.allow_experimental_codec()`，被 `ffmpeg.py` 的 `restore_audio` / `replace_audio` / `concat_video` 调用 | 三处都要调用；`concat_video` 最易遗漏 |
| 源脸 baseline 预热 | `workflows/core.py` `preheat_static_faces()` + `to_video.py`/`to_image.py` 调用点 | 保留调用 |
| frame override 注入 | `workflows/core.py` `process_temp_frame()` 的 `frame_override.apply_context` | 保留 |

> `concat_video` 走 `job_runner.finalize_steps`，flac 音轨 `-c copy` 会因"实验特性"写头失败，导致**输出 0 字节、headless-run 返回 1**，而日志仍打印"成功"。排查时优先怀疑这里。

---

## 合并后必做的验证

```bash
# 1) 无冲突残留
grep -rn "<<<<<<<\|>>>>>>>" facefusion/ --include=*.py

# 2) 定制层完整：文件集合应与合并前一致（138 个）
git diff --name-only <上游标签> HEAD | wc -l

# 3) 上游改动确实落地 + 本地补丁仍在（逐项对照上面的"易被覆盖"表）
grep -n "def analyse_video\|def analyse_image" facefusion/workflows/to_video.py facefusion/workflows/to_image.py
grep -n "allow_experimental_codec" facefusion/ffmpeg.py facefusion/ffmpeg_builder.py

# 4) 导入冒烟
python -c "import facefusion.core, facefusion.workflows.core, facefusion.workflows.to_video, facefusion.uis.components.output_options"

# 5) 端到端出片（flac 编码器同时覆盖 concat 路径）
python facefusion.py headless-run --language zh -s <源> -t <视频> -o out/x.mp4 \
  --processors face_swapper --output-audio-encoder flac --trim-frame-end 12
ffprobe -v error -show_entries stream=codec_type,codec_name -of csv=p=0 out/x.mp4
# 期望：EXIT=0，输出非 0 字节，含 h264,video + flac,audio

# 6) 测试（注意 test_get_available_encoder_set / test_restore_audio 在无 GPU 环境会卡住）
python -m pytest tests/ -q --deselect tests/test_ffmpeg.py::test_get_available_encoder_set
```

---

## 合并记录

### 3.9.1（2026-10-05）

- 上游提交：`72470819`（tag `3.9.1`），自 3.8.0 起 10 个提交。
- 前置：`git replace --graft 625b01d5 b60ea40d`（修复合并基点）。
- 合并提交：`39932803`（master）。
- 冲突：仅 3 处，均为 import 行合并（上游新增符号 + 本地新增符号）：
  - `facefusion/workflows/core.py`（vision 导入）
  - `facefusion/workflows/to_video.py`（vision / workflows 导入）
  - `facefusion/uis/components/output_options.py`（`get_ui_component` + `ui_tips.tip`）
- 同时修复：`ffmpeg.py` 的 `concat_video` 补 `-strict -2`（见上方"易被覆盖"表）。
- 验证：定制层 138 文件集合前后一致（0 丢失）；上游 `resolve_extract_frame_number` / `fps_mode passthrough` 等已落地；flac 编码器下 memory/disk 两种策略均正常出片。
- 遗留（合并前既有，与本次无关）：`test_extract_frames`（示例资产 0 字节）、`test_cli_lip_syncer` 视频用例、`test_curl_builder`/`test_download`（代理环境）。

---

## 仅挑上游某次修复

```bash
git fetch upstream
git cherry-pick <upstream-commit-sha>
```

适合单点 hotfix（如内存泄漏），不适合大版本跳跃。

## 大版本（例如 3.9 → 4.x）

1. 先读官方 changelog / breaking changes  
2. 新建分支 `merge/upstream-4.x`，不要直接在 `master` 硬刚  
3. 先让官方测试 greening，再逐项移植定制  
4. 用 `tests/` 与 frame override 相关用例做回归
5. 4.x 可能改动 workflow/vision/video_manager 结构，重点核对"易被覆盖的本地补丁"表

## 本机 remote 维护备忘

```bash
# 确认
git remote -v
git status -sb

# 只推自己的 fork
git push origin master

# 更新上游引用（不合并）
git fetch upstream --tags

# 本机未配置 git user.name/email 时，提交用一次性参数（不改全局配置）
git -c user.name="你的姓名" -c user.email="you@example.com" commit -m "..."
```
