from typing import Any, List, Optional, Tuple

import cv2
import gradio
import numpy

from facefusion import frame_override, state_manager
from facefusion.face_creator import get_many_faces, get_one_face, get_static_faces
from facefusion.face_selector import find_match_faces, sort_and_filter_faces
from facefusion.face_store import clear_faces
from facefusion.filesystem import is_image, is_video
from facefusion.processors.modules.face_debugger.core import draw_bounding_box, draw_face_landmark_5_68, draw_face_mask
from facefusion.types import Face, VisionFrame
from facefusion.uis.components.repair_options import apply_by_scope, apply_fix
from facefusion.uis.core import get_ui_component, register_ui_component

DIAGNOSTICS_CHECKBOX : Optional[gradio.Checkbox] = None
DIAGNOSTICS_IMAGE : Optional[gradio.Image] = None
DIAGNOSTICS_TEXTBOX : Optional[gradio.Textbox] = None
DIAGNOSTICS_FIX_NO_SWAP_BUTTON : Optional[gradio.Button] = None
DIAGNOSTICS_FIX_DOUBLE_BUTTON : Optional[gradio.Button] = None
DIAGNOSTICS_FIX_DISTORTION_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global DIAGNOSTICS_CHECKBOX
	global DIAGNOSTICS_IMAGE
	global DIAGNOSTICS_TEXTBOX
	global DIAGNOSTICS_FIX_NO_SWAP_BUTTON
	global DIAGNOSTICS_FIX_DOUBLE_BUTTON
	global DIAGNOSTICS_FIX_DISTORTION_BUTTON

	gradio.Markdown('### 诊断（叠加检测信息，仅用于排查；就地修复跟随「疑难帧修复」作用域）')
	DIAGNOSTICS_CHECKBOX = gradio.Checkbox(
		label = '开启诊断',
		value = False
	)
	DIAGNOSTICS_TEXTBOX = gradio.Textbox(
		label = '诊断结果',
		lines = 4,
		interactive = False,
		visible = False
	)
	with gradio.Row():
		DIAGNOSTICS_FIX_NO_SWAP_BUTTON = gradio.Button(
			value = '修复：人脸不替换',
			size = 'sm',
			variant = 'primary',
			visible = False
		)
		DIAGNOSTICS_FIX_DOUBLE_BUTTON = gradio.Button(
			value = '修复：两脸重合',
			size = 'sm',
			variant = 'primary',
			visible = False
		)
		DIAGNOSTICS_FIX_DISTORTION_BUTTON = gradio.Button(
			value = '修复：面部扭曲',
			size = 'sm',
			variant = 'primary',
			visible = False
		)
	DIAGNOSTICS_IMAGE = gradio.Image(
		label = '诊断视图',
		visible = False
	)
	register_ui_component('diagnostics_checkbox', DIAGNOSTICS_CHECKBOX)
	register_ui_component('diagnostics_image', DIAGNOSTICS_IMAGE)
	register_ui_component('diagnostics_textbox', DIAGNOSTICS_TEXTBOX)


def _diagnostics_outputs() -> List[Any]:
	return [ DIAGNOSTICS_IMAGE, DIAGNOSTICS_TEXTBOX, DIAGNOSTICS_FIX_NO_SWAP_BUTTON, DIAGNOSTICS_FIX_DOUBLE_BUTTON, DIAGNOSTICS_FIX_DISTORTION_BUTTON ]


def listen() -> None:
	preview_frame_slider = get_ui_component('preview_frame_slider')
	preview_image = get_ui_component('preview_image')
	preview_mode_dropdown = get_ui_component('preview_mode_dropdown')
	preview_resolution_dropdown = get_ui_component('preview_resolution_dropdown')
	control_outputs = _collect_control_outputs()
	outputs = _diagnostics_outputs()

	if preview_frame_slider:
		DIAGNOSTICS_CHECKBOX.change(toggle_diagnostics, inputs = [ DIAGNOSTICS_CHECKBOX, preview_frame_slider ], outputs = outputs)
		# 拖动到新帧、松手后若诊断开启则刷新诊断视图
		preview_frame_slider.release(update_diagnostics, inputs = [ DIAGNOSTICS_CHECKBOX, preview_frame_slider ], outputs = outputs, show_progress = 'hidden')
	else:
		DIAGNOSTICS_CHECKBOX.change(toggle_diagnostics, inputs = DIAGNOSTICS_CHECKBOX, outputs = outputs)

	# 诊断面板内的修复按钮：跟随 repair 作用域写入 -> 刷新主预览/诊断
	if preview_frame_slider and preview_image and control_outputs:
		preview_inputs = [ preview_mode_dropdown, preview_resolution_dropdown, preview_frame_slider ]
		diagnostics_inputs = [ DIAGNOSTICS_CHECKBOX, preview_frame_slider ]
		repair_scope_radio = get_ui_component('repair_scope_radio')
		repair_range_start = get_ui_component('repair_range_start_number')
		repair_range_end = get_ui_component('repair_range_end_number')
		rules_markdown = get_ui_component('repair_rules_markdown')
		effective_source_markdown = get_ui_component('repair_effective_source_markdown')
		scope_inputs = None
		if repair_scope_radio and repair_range_start and repair_range_end:
			scope_inputs = [ repair_scope_radio, repair_range_start, repair_range_end, preview_frame_slider ]
		meta_outputs = []
		if rules_markdown and effective_source_markdown:
			meta_outputs = [ rules_markdown, effective_source_markdown ]

		for button, preset_name in [
		
			(DIAGNOSTICS_FIX_NO_SWAP_BUTTON, 'no_swap'),
			(DIAGNOSTICS_FIX_DOUBLE_BUTTON, 'double'),
			(DIAGNOSTICS_FIX_DISTORTION_BUTTON, 'distortion')
		]:
			if scope_inputs:
				button.click(
					lambda scope, start, end, frame, preset_name = preset_name : _apply_diagnostics_fix(scope, start, end, frame, preset_name),
					inputs = scope_inputs,
					outputs = control_outputs + meta_outputs
				).then(_refresh_preview, inputs = preview_inputs, outputs = preview_image).then(update_diagnostics, inputs = diagnostics_inputs, outputs = outputs)
			else:
				button.click(lambda preset_name = preset_name : apply_fix(preset_name), outputs = control_outputs).then(_refresh_preview, inputs = preview_inputs, outputs = preview_image).then(update_diagnostics, inputs = diagnostics_inputs, outputs = outputs)


def _apply_diagnostics_fix(scope : str, range_start : float, range_end : float, frame_number : float, preset_name : str) -> Tuple[Any, ...]:
	return apply_by_scope(scope, range_start, range_end, frame_number, preset_name, 'normal')


def _collect_control_outputs() -> List[Any]:
	component_names =\
	[
		'face_detector_angles_checkbox_group',
		'face_detector_score_slider',
		'face_landmarker_score_slider',
		'reference_face_distance_slider',
		'face_mask_types_checkbox_group',
		'face_mask_blur_slider'
	]
	return [ get_ui_component(component_name) for component_name in component_names ]


def _refresh_preview(preview_mode : str, preview_resolution : str, frame_number : int = 0) -> gradio.Image:
	from facefusion.uis.components.preview import update_preview_image

	clear_faces()
	return update_preview_image(preview_mode, preview_resolution, frame_number)


def toggle_diagnostics(is_enabled : bool, frame_number : int = 0) -> Tuple[gradio.Image, gradio.Textbox, gradio.Button, gradio.Button, gradio.Button]:
	if not is_enabled:
		return gradio.Image(value = None, visible = False), gradio.Textbox(visible = False), gradio.Button(visible = False), gradio.Button(visible = False), gradio.Button(visible = False)
	return update_diagnostics(is_enabled, frame_number)


def update_diagnostics(is_enabled : bool, frame_number : int = 0) -> Tuple[gradio.Image, gradio.Textbox, gradio.Button, gradio.Button, gradio.Button]:
	if not is_enabled:
		return gradio.Image(visible = False), gradio.Textbox(visible = False), gradio.Button(visible = False), gradio.Button(visible = False), gradio.Button(visible = False)

	vision_frame = _resolve_target_frame(frame_number)
	if vision_frame is None:
		return gradio.Image(value = None, visible = True), gradio.Textbox(value = '请先选择目标图像或视频。', visible = True), gradio.Button(visible = False), gradio.Button(visible = False), gradio.Button(visible = False)

	# 诊断按当前帧 effective 参数检测；reference 身份用 baseline
	with frame_override.apply_context(int(frame_number or 0)):
		clear_faces()
		target_faces = get_many_faces([ vision_frame ])
		target_faces = sort_and_filter_faces([], target_faces)
		matched_faces = _resolve_matched_faces(vision_frame, target_faces, frame_number)
		report = frame_override.format_effective_source(int(frame_number or 0)) + chr(10) + _build_report(target_faces, matched_faces)
		debug_vision_frame = _draw_overlay(vision_frame, target_faces)
		debug_vision_frame = cv2.cvtColor(debug_vision_frame, cv2.COLOR_BGR2RGB)
		clear_faces()

	# 根据检测到的问题，决定显示哪些就地修复按钮
	face_total = len(target_faces)
	has_no_swap = face_total == 0 or (state_manager.get_item('face_selector_mode') == 'reference' and len(matched_faces) == 0)
	has_double = _count_duplicate_faces(target_faces) > 0
	has_distortion = _count_unrefined_landmarks(target_faces) > 0

	return (
		gradio.Image(value = debug_vision_frame, visible = True),
		gradio.Textbox(value = report, visible = True),
		gradio.Button(visible = has_no_swap),
		gradio.Button(visible = has_double),
		gradio.Button(visible = has_distortion)
	)


def _resolve_target_frame(frame_number : int) -> Optional[VisionFrame]:
	from facefusion.vision import read_static_image, read_video_frame

	target_path = state_manager.get_item('target_path')

	if is_image(target_path):
		return read_static_image(target_path)
	if is_video(target_path):
		return read_video_frame(target_path, frame_number)
	return None


def _resolve_matched_faces(vision_frame : VisionFrame, target_faces : List[Face], frame_number : int) -> List[Face]:
	# 复现 reference 模式下"哪些脸会被实际替换"，用于判断匹配是否过严/过松
	if state_manager.get_item('face_selector_mode') != 'reference':
		return target_faces

	from facefusion.vision import read_static_image, read_video_frame

	target_path = state_manager.get_item('target_path')
	reference_frame_number = state_manager.get_item('reference_frame_number')

	if is_image(target_path):
		reference_vision_frame = read_static_image(target_path)
	elif is_video(target_path):
		reference_vision_frame = read_video_frame(target_path, reference_frame_number)
	else:
		return []

	reference_faces = sort_and_filter_faces([], get_static_faces([ reference_vision_frame ], use_baseline = True))
	reference_face = get_one_face(reference_faces, state_manager.get_item('reference_face_position'))
	if reference_face:
		return find_match_faces([ reference_face ], target_faces, state_manager.get_item('reference_face_distance'))
	return []


def _build_report(target_faces : List[Face], matched_faces : List[Face]) -> str:
	lines = []
	face_total = len(target_faces)
	lines.append('检测到人脸：{0} 张'.format(face_total))

	if face_total == 0:
		lines.append('未检测到人脸 → 此帧不会被替换。建议：降低"人脸检测器分数"、开启多角度检测、或换用 retinaface/scrfd 检测器。')
		return '\n'.join(lines)

	# 重复检测（中心非常接近的多个框）
	duplicate_pairs = _count_duplicate_faces(target_faces)
	if duplicate_pairs:
		lines.append('疑似重复检测：{0} 处中心重叠 → 可能"两脸重合/重复换"。可点下方"修复：两脸重合"。'.format(duplicate_pairs))

	# 关键点是否精修（黄点=未精修）
	unrefined = _count_unrefined_landmarks(target_faces)
	if unrefined:
		lines.append('{0} 张人脸关键点未精修 → 可能贴歪/扭曲。可点下方"修复：面部扭曲"或调整"面部特征点分数"。'.format(unrefined))

	# 选脸匹配情况（reference 模式）
	if state_manager.get_item('face_selector_mode') == 'reference':
		matched_total = len(matched_faces)
		lines.append('参考模式匹配到：{0} / {1} 张将被替换'.format(matched_total, face_total))
		if matched_total == 0:
			lines.append('没有人脸匹配上参考脸 → 此帧不会被替换。建议调大"参考人脸距离"，或点下方"修复：人脸不替换"。')
		elif matched_total < face_total:
			lines.append('有人脸未匹配（可能是其他人）。若漏换目标，调大"参考人脸距离"。')

	# 低分检测提醒
	low_score = [ face for face in target_faces if face.score_set.get('detector') < 0.6 ]
	if low_score:
		lines.append('{0} 张人脸检测置信度偏低（<0.6），角度/模糊较极端。'.format(len(low_score)))

	if len(lines) == 1:
		lines.append('未发现明显异常。')
	return '\n'.join(lines)


def _count_duplicate_faces(faces : List[Face]) -> int:
	duplicate_total = 0

	for index, face in enumerate(faces):
		start_x, start_y, end_x, end_y = face.bounding_box
		face_center = numpy.array([ (start_x + end_x) / 2, (start_y + end_y) / 2 ])
		face_size = max(end_x - start_x, end_y - start_y)

		for other_face in faces[index + 1:]:
			other_start_x, other_start_y, other_end_x, other_end_y = other_face.bounding_box
			other_center = numpy.array([ (other_start_x + other_end_x) / 2, (other_start_y + other_end_y) / 2 ])
			other_size = max(other_end_x - other_start_x, other_end_y - other_start_y)

			if numpy.linalg.norm(face_center - other_center) < min(face_size, other_size) * 0.45:
				duplicate_total += 1

	return duplicate_total


def _count_unrefined_landmarks(faces : List[Face]) -> int:
	unrefined_total = 0

	for face in faces:
		face_landmark_5 = face.landmark_set.get('5')
		face_landmark_5_68 = face.landmark_set.get('5/68')
		# 5/68 与 5 相等说明 68 点精修失败，退回了粗略检测点
		if face_landmark_5 is not None and face_landmark_5_68 is not None and numpy.array_equal(face_landmark_5, face_landmark_5_68):
			unrefined_total += 1

	return unrefined_total


def _draw_overlay(vision_frame : VisionFrame, target_faces : List[Face]) -> VisionFrame:
	debug_vision_frame = vision_frame.copy()

	for target_face in target_faces:
		debug_vision_frame = draw_bounding_box(target_face, debug_vision_frame)
		debug_vision_frame = draw_face_mask(target_face, debug_vision_frame)
		debug_vision_frame = draw_face_landmark_5_68(target_face, debug_vision_frame)

	return debug_vision_frame
