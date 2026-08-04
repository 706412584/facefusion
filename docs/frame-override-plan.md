# 疑难帧修复三层 Override — 修订方案（二审后）

> 状态：二审 **CHANGES_NEEDED** 已吸收；待产品决策拍板后实现。  
> 日期：2026-08-05

## 1. 目标 / 非目标

### 目标
- 三层：**单帧例外 > 时段覆盖 > 全局默认**
- 预览修正后立即看到最新状态
- **播放预览**吃到同一套补丁（与单帧共用 `update_preview_image`）
- 作用域可写：全局 / 当前帧 / 区间；规则列表 + 当前帧生效来源

### 非目标（MVP）
- 完整 NLE 时间线 / 关键帧曲线
- 按帧换模型、换 source、换 processor 列表
- 复用 `trim_frame` 作为 override 区间（trim 只裁出片范围）

## 2. 二审结论摘要

| 来源 | 结论 |
|------|------|
| Explore | 挂点：`update_preview_image` + `process_temp_frame`；播放复用单帧；FACE_STORE 无参数指纹；多线程禁止 per-frame `set_item` |
| Plan | 进程内 rule store + contextvars + 白名单 6 键 + skip；MVP 含出片 |
| Critic | **CHANGES_NEEDED**：MVP 含出片过大；`get_item` 契约未定；reference 污染；全局语义与 diagnostics 冲突；skip 未覆盖 deep_swapper |
| Reviewer | **CHANGES_NEEDED**：帧 context 协议、skip 挂点、播放验收（步进 20）、repair/diagnostics 统一写入 |

## 3. 修订后 MVP（推荐）

### Phase A — 预览 + 播放（先做，满足主诉求）
1. 新建 `facefusion/frame_override.py`  
   - `frame_rules: Dict[int, FrameRule]`  
   - `range_rules: List[RangeRule]`（后写优先；重叠时后写覆盖）  
   - `resolve_frame_settings(frame) -> {action, source, rule_id, params}`  
   - `apply_context(frame)`：`contextvars`，线程隔离  
2. **不默认永久改写全库语义**：  
   - 用 `apply_context` 包住处理链；  
   - `state_manager.get_item` **仅当 context 激活且 key∈白名单** 时返回覆盖值，否则原逻辑（无 context = baseline / CLI 安全）。  
3. 挂点：  
   - `preview.update_preview_image`（或紧邻 `process_preview_frame`）在视频分支按 slider 帧号 `apply_context`  
   - `play_preview` **不必单改**（已循环调用 `update_preview_image`）  
4. `skip_process`：在预览处理入口早退，返回原帧  
5. `skip_swap`：`face_swapper.process_frame` + **`deep_swapper.process_frame`** 早退  
6. UI（`repair_options`）：  
   - 作用域 Radio：全局 | 当前帧 | 区间  
   - 全局 → 现有 `apply_fix` / `reset_defaults`（写 state + 回写 6 控件）  
   - 当前帧 / 区间 → 只写 override store，**不回写** 6 控件  
   - 规则列表 +「当前帧生效来源」  
   - 写规则后：`clear_faces()` + `update_preview_image` + 刷新列表/来源  
7. `diagnostics`：MVP **仍写全局**并文案标明；或与 repair 共用 scope（实现时二选一，默认仍全局以免扩大面）  
8. 生命周期：**仅当前 UI 进程**；换 target / 清空补丁按钮可清 store；**不进 job JSON**（文案写明）

### Phase B — 出片（预览验收通过后）
1. `workflows/core.process_temp_frame` 包同一 `apply_context(frame_number)`  
2. 出片前 **单线程、零 override** 预热 `get_static_faces([reference])`；处理中禁止在 override 下重写 reference 缓存  
3. 多线程只靠 contextvars，禁止 worker `set_item` 临时改参  
4. 抽检：`execution_thread_count≥2` 时补丁帧与邻帧

## 4. 数据与优先级

```
effective(frame) =
  if frame_rules[frame] enabled: use it (action 优先)
  else if last matching range_rule: use its params
  else: global state_manager (白名单字段)
```

### 白名单（与现 repair 对齐，宁少勿多）
- `face_detector_angles`
- `face_detector_score`
- `face_landmarker_score`
- `reference_face_distance`
- `face_mask_types`
- `face_mask_blur`

### Actions
- `normal` + params  
- `skip_swap`：不换脸（face_swapper + deep_swapper）  
- `skip_process`：整帧跳过全部 processor，出原画  

### 不做（MVP）
- detector model/size、selector mode、reference_frame_number、mask padding、tracker、换 source

## 5. 缓存策略

| 场景 | 策略 |
|------|------|
| 增删改规则 / 全局 apply_fix | `clear_faces()` |
| 仅滑帧、参数未变 | 不 clear |
| 播放每帧 | **禁止**每帧 clear |
| 出片开始（Phase B） | 零 override 预热 reference；可选 clear 后预热 |

## 6. 关键文件

| 文件 | 动作 |
|------|------|
| `facefusion/frame_override.py` | 新建 |
| `facefusion/state_manager.py` | `get_item` 条件读 context 白名单 |
| `facefusion/uis/components/preview.py` | 按帧 apply_context |
| `facefusion/uis/components/repair_options.py` | 作用域 UI + 写入分流 |
| `facefusion/processors/modules/face_swapper/core.py` | skip_swap |
| `facefusion/processors/modules/deep_swapper/core.py` | skip_swap |
| `facefusion/workflows/core.py` | Phase B |
| `facefusion/workflows/to_video.py` | Phase B reference 预热 |
| `tests/test_frame_override.py` | 优先级 / context 隔离 |

## 7. 验收

### Phase A
1. 无规则：预览与改前一致  
2. 作用域=全局：与现网一致（控件回写、邻帧也变）  
3. 作用域=当前帧：仅该帧变；邻帧回全局；来源显示「单帧」  
4. 作用域=区间：区间内变、外不变  
5. 单帧压过时段  
6. 播放：对规则帧用 slider/`update_preview_image` **确切帧号**抽检（play 步进 20 可能跳过短补丁，文档说明；可选后续降步进）  
7. skip_swap / skip_process 目视正确  
8. 单元测试：resolve 优先级、白名单、无 context 透传、两线程 context 不串

### Phase B
1. 成片对应帧与预览策略一致  
2. 多线程不串台、reference 匹配稳定  
3. 无规则 baseline 出片不变

## 8. 回退
- store 空时 resolve 恒 global，context 空操作  
- 可选 `FRAME_OVERRIDE_ENABLED=0`  
- UI 可隐藏作用域，按钮只走旧 `apply_fix`

## 9. 待用户拍板（实现前）

1. **全局层**：A) 继续 = `state_manager`+滑条（推荐） / B) 独立 global_rules  
2. **skip 默认**：A) 提供 skip_swap + skip_process 两个按钮（推荐） / B) 只要其一  
3. **生命周期**：A) 仅 UI 会话（推荐 MVP） / B) 写入 job 可复现  
4. **控件显示**：A) 始终显示全局 base，另示「本帧生效来源」（推荐） / B) 滑条跟随 effective  
5. **出片**：A) Phase A 先预览播放，通过后再 Phase B（推荐） / B) 一次做完含出片  
6. **diagnostics**：A) 仍只写全局并标明 / B) 跟 repair 作用域  

默认推荐：**1A 2A 3A 4A 5A 6A**。
