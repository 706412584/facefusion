"""WebUI 控件说明（Gradio info / 疑难解答文案）。"""

from typing import Dict


CONTROL_TIPS : Dict[str, str] =\
{
	# face detector
	'face_detector_model': '决定“能不能找到脸”。yolo_face 快稳（日常）；retinaface/scrfd 大角度更强但更慢；many 多模型联检最强也最慢，易重复框。',
	'face_detector_size': '检测输入分辨率。越大越能看清小人脸/远脸，也更吃显存和更慢。一般 640x640 足够。',
	'face_detector_margin': '检测前给画面加边距，减少贴边人脸被裁切。侧脸/贴边漏检可略增；过大可能引入误检。',
	'face_detector_angles': '按角度旋转后再检测。只开 0 最稳；侧脸/倒脸多再加 90/270。角度越多越慢，也更容易重复框和乱换。',
	'face_detector_score': '检测置信度阈值。越高越“挑剔”（糊脸/侧脸更少被检到）；越低越容易把路人/糊脸也检进来。乱换时先提到 0.55~0.65。',

	# landmarker
	'face_landmarker_model': '定位五官关键点，影响贴脸是否歪。2dfan4 默认稳妥；peppa_wutz 可作备选；many 更慢。',
	'face_landmarker_score': '关键点质量门槛。提高可过滤大角度/模糊导致关键点很差的脸，减少硬贴翻车；过高会漏换。建议 0.5~0.6。',

	# selector
	'face_selector_mode': 'many=所有脸都换；one=只换排序后第一张；reference=只换与参考脸相似的人（防乱换首选）。',
	'face_selector_order': '多脸时的排序方式。large-small 通常优先主脸；left-right 等按位置。',
	'face_selector_gender': '按性别过滤目标脸。none 不过滤；不确定时保持 none。',
	'face_selector_race': '按种族标签过滤。none 不过滤；过滤过严会漏换。',
	'face_selector_age_range': '只处理该年龄段内的脸。范围过窄会漏换。',
	'reference_face_gallery': 'reference 模式下点选要换的目标人物。必须点对，否则会串脸或漏换。',
	'reference_face_distance': '与参考脸的相似度阈值。越小越严格（更不易串路人）；越大越宽松。乱换时从 0.75 降到 0.35~0.45。',

	# tracker
	'face_tracker_score': '视频跨帧跟踪阈值。>0 开启跟踪，减少晃动时脸跳变/乱换。建议 0.3~0.5；0 表示关闭。需配合 target_frame_amount>1。',

	# masker
	'face_occluder_model': '遮挡分割（xseg）。处理手挡脸、麦克风等。xseg_1 常用；更高版本可能更细但更重。',
	'face_parser_model': '五官区域解析（bisenet）。用于 region mask。resnet_34 通常更准也更重。',
	'face_mask_types': 'box=矩形融合；occlusion=遮挡感知；area/region=按区域融合。视频常用 box+occlusion。',
	'face_mask_blur': 'mask 边缘羽化。越大边缘越柔和，过大易“糊一圈”。',
	'face_mask_padding': 'box mask 四边内缩/外扩。脸边缘露原脸就减小；换脸“贴饼”过大可增大。',

	# swapper
	'face_swapper_model': '真正换脸的核心模型。hyperswap_1a_256 默认综合好；inswapper_128(_fp16) 老牌更快更省；ghost/simswap 等各有风格差异。',
	'face_swapper_pixel_boost': '换脸推理分辨率增强。越高越清晰也越慢、更吃显存。显存不够先降。',
	'face_swapper_weight': '源脸特征融入强度（部分模型支持）。过高可能假；过低不像源脸。',

	# enhancer
	'face_enhancer_model': '换脸后的清晰度修复。gfpgan_1.4 常用；codeformer 可调强度；过强可能“整容感”。',
	'face_enhancer_blend': '增强结果与原图混合比例。100 全增强；降低可保留更多原肤质。',
	'face_enhancer_weight': '部分增强模型的修复强度。糊脸可提高，假脸感重则降低。',

	# processors / runtime
	'processors': '处理流水线。至少保留 face_swapper；需要更清晰再勾 face_enhancer。勾选越多越慢。',
	'execution_providers': '推理后端。有 NVIDIA 优先 CUDA/TensorRT；CPU 很慢。改后需确保环境已装对应库。',
	'execution_thread_count': '并行线程数。视频可适当提高加速，过高会显存爆或反而变慢。',
	'video_memory_strategy': '显存策略。strict 更省显存（慢）；tolerant 更快更吃显存。OOM 时改 strict。',
	'workflow_strategy': 'disk=落盘逐帧（稳、可续跑）；memory=内存管道（更快更吃 RAM/VRAM）。',
	'output_video_encoder': '导出编码。libx264 兼容最好；硬件编码更快但质量/兼容看驱动。',
	'output_video_quality': '导出画质。越高文件越大。一般 80~95。',
}


FAQ_MARKDOWN = """
## 疑难解答（常见换脸问题）

### 1. 侧脸 / 倾斜 / 路人脸也被换进去
1. **人脸选择** 改为 `reference`，并在参考脸画廊 **点中目标人物**
2. **参考脸距离** 从宽松改严格：建议 `0.35 ~ 0.45`（原 0.75 太松）
3. **检测分数** 提到 `0.55 ~ 0.65`
4. **检测角度** 先只开 `0`；确认需要再加 `90/270`
5. **关键点分数** 提到 `0.50 ~ 0.60`

### 2. 晃动、模糊帧乱换 / 脸跳来跳去
1. 开启 **人脸跟踪**：`face_tracker_score = 0.3 ~ 0.5`
2. **目标帧数量** `target_frame_amount` 设为 `3 ~ 5`
3. 同步提高检测分与关键点分，过滤低质量脸
4. 极端运动模糊无法完美，可接受部分帧质量下降

### 3. 两脸重合 / 同一人被换两次
1. 不要用检测模型 `many`
2. 减少检测角度（避免 0/90/180/270 全开）
3. 提高检测分数
4. 使用右侧 **诊断 / 修复** 面板查看重复框

### 4. 主脸漏换
1. 略降检测分数（如 `0.50`）
2. 检测模型改 `retinaface`，尺寸 `640x640`
3. reference 距离略放宽（如 `0.45 ~ 0.55`）
4. 确认参考脸点对、源脸清晰正面

### 5. 贴歪、五官撕裂
1. 关键点模型用 `2dfan4`，分数 `0.5+`
2. 换脸模型优先 `hyperswap_1a_256` 或 `inswapper_128_fp16`
3. mask 使用 `box + occlusion`，适当增加 edge blur
4. 大侧脸本身难度高，可配合多角度检测但别降太低分

### 6. 显存不足 / 很慢
1. `video_memory_strategy = strict`
2. 降低 pixel boost、关闭不必要 processor
3. 线程数不要盲目拉满
4. 换脸模型可改 `inswapper_128_fp16`

### 推荐起步（防乱换）
- 检测：`retinaface` / `yolo_face`，角度仅 `0`，分数 `0.60`
- 关键点：`2dfan4`，分数 `0.55`
- 选择：`reference`，距离 `0.40`
- 跟踪：`0.40`，目标帧数 `3`
- 换脸：`hyperswap_1a_256`
"""


def tip(key : str) -> str:
	return CONTROL_TIPS.get(key, '')
