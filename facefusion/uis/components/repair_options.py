from typing import Any, List, Optional, Tuple

import gradio

from facefusion import config, frame_override, state_manager
from facefusion.face_store import clear_faces
from facefusion.filesystem import is_video
from facefusion.uis.components.preview import update_preview_image
from facefusion.uis.core import get_ui_component, register_ui_component

REDETECT_FRAME_BUTTON : Optional[gradio.Button] = None
FIX_NO_SWAP_BUTTON : Optional[gradio.Button] = None
FIX_DISTORTION_BUTTON : Optional[gradio.Button] = None
FIX_DOUBLE_BUTTON : Optional[gradio.Button] = None
FIX_EDGE_BUTTON : Optional[gradio.Button] = None
SKIP_SWAP_BUTTON : Optional[gradio.Button] = None
SKIP_PROCESS_BUTTON : Optional[gradio.Button] = None
RESET_DEFAULT_BUTTON : Optional[gradio.Button] = None
CLEAR_PATCHES_BUTTON : Optional[gradio.Button] = None
DELETE_RULE_BUTTON : Optional[gradio.Button] = None
REPAIR_SCOPE_RADIO : Optional[gradio.Radio] = None
RANGE_START_NUMBER : Optional[gradio.Number] = None
RANGE_END_NUMBER : Optional[gradio.Number] = None
RULE_ID_TEXTBOX : Optional[gradio.Textbox] = None
RULES_MARKDOWN : Optional[gradio.Markdown] = None
EFFECTIVE_SOURCE_MARKDOWN : Optional[gradio.Markdown] = None

SCOPE_CHOICES = [ '全局', '当前帧', '区间' ]


def render() -> None:
	global REDETECT_FRAME_BUTTON
	global FIX_NO_SWAP_BUTTON
	global FIX_DISTORTION_BUTTON
	global FIX_DOUBLE_BUTTON
	global FIX_EDGE_BUTTON
	global SKIP_SWAP_BUTTON
	global SKIP_PROCESS_BUTTON
	global RESET_DEFAULT_BUTTON
	global CLEAR_PATCHES_BUTTON
	global DELETE_RULE_BUTTON
	global REPAIR_SCOPE_RADIO
	global RANGE_START_NUMBER
	global RANGE_END_NUMBER
	global RULE_ID_TEXTBOX
	global RULES_MARKDOWN
	global EFFECTIVE_SOURCE_MARKDOWN

	gradio.Markdown(
		'### 疑难帧修复\n'
		'**全局**改默认参数（控件会回写，出片也用这套默认）；'
		'**当前帧 / 区间**写入补丁（仅本会话；预览、播放与出片按帧生效）。'
		'优先级：单帧 > 时段 > 全局。左侧滑条始终显示全局 base。'
	)
	REPAIR_SCOPE_RADIO = gradio.Radio(
		label = '作用域',
		choices = SCOPE_CHOICES,
		value = '全局'
	)
	with gradio.Row():
		RANGE_START_NUMBER = gradio.Number(
			label = '区间起帧',
			value = 0,
			precision = 0
		)
		RANGE_END_NUMBER = gradio.Number(
			label = '区间止帧',
			value = 0,
			precision = 0
		)
	with gradio.Row():
		REDETECT_FRAME_BUTTON = gradio.Button(value = '重新检测此帧', size = 'sm')
		FIX_NO_SWAP_BUTTON = gradio.Button(value = '人脸不替换', size = 'sm')
	with gradio.Row():
		FIX_DISTORTION_BUTTON = gradio.Button(value = '面部扭曲/歪斜', size = 'sm')
		FIX_DOUBLE_BUTTON = gradio.Button(value = '两脸重合/重复换', size = 'sm')
	with gradio.Row():
		FIX_EDGE_BUTTON = gradio.Button(value = '边缘/遮挡穿帮', size = 'sm')
		RESET_DEFAULT_BUTTON = gradio.Button(value = '恢复默认参数(全局)', size = 'sm')
	with gradio.Row():
		SKIP_SWAP_BUTTON = gradio.Button(value = '跳过换脸(本帧/区间)', size = 'sm')
		SKIP_PROCESS_BUTTON = gradio.Button(value = '强制不处理(原画)', size = 'sm')
	with gradio.Row():
		CLEAR_PATCHES_BUTTON = gradio.Button(value = '清空全部补丁', size = 'sm')
		RULE_ID_TEXTBOX = gradio.Textbox(label = '删除规则 id', placeholder = '粘贴规则 id', lines = 1)
		DELETE_RULE_BUTTON = gradio.Button(value = '删除指定规则', size = 'sm')

	EFFECTIVE_SOURCE_MARKDOWN = gradio.Markdown(value = frame_override.format_effective_source(0))
	RULES_MARKDOWN = gradio.Markdown(value = frame_override.format_rules_markdown())

	register_ui_component('repair_scope_radio', REPAIR_SCOPE_RADIO)
	register_ui_component('redetect_frame_button', REDETECT_FRAME_BUTTON)
	register_ui_component('fix_no_swap_button', FIX_NO_SWAP_BUTTON)
	register_ui_component('fix_distortion_button', FIX_DISTORTION_BUTTON)
	register_ui_component('fix_double_button', FIX_DOUBLE_BUTTON)
	register_ui_component('fix_edge_button', FIX_EDGE_BUTTON)
	register_ui_component('reset_default_button', RESET_DEFAULT_BUTTON)


def listen() -> None:
	preview_image = get_ui_component('preview_image')
	preview_mode_dropdown = get_ui_component('preview_mode_dropdown')
	preview_resolution_dropdown = get_ui_component('preview_resolution_dropdown')
	preview_frame_slider = get_ui_component('preview_frame_slider')
	control_outputs = _collect_control_outputs()
	preview_inputs = [ preview_mode_dropdown, preview_resolution_dropdown, preview_frame_slider ]
	meta_outputs = [ RULES_MARKDOWN, EFFECTIVE_SOURCE_MARKDOWN ]

	if not all(preview_inputs) or not preview_image:
		return

	scope_inputs = [ REPAIR_SCOPE_RADIO, RANGE_START_NUMBER, RANGE_END_NUMBER, preview_frame_slider ]

	REDETECT_FRAME_BUTTON.click(redetect_frame, inputs = preview_inputs, outputs = preview_image)\
		.then(refresh_meta, inputs = [ preview_frame_slider ], outputs = meta_outputs)

	for button, preset_name in\
	[
		(FIX_NO_SWAP_BUTTON, 'no_swap'),
		(FIX_DISTORTION_BUTTON, 'distortion'),
		(FIX_DOUBLE_BUTTON, 'double'),
		(FIX_EDGE_BUTTON, 'edge')
	]:
		button.click(
			lambda scope, start, end, frame, preset_name = preset_name : apply_by_scope(scope, start, end, frame, preset_name, 'normal'),
			inputs = scope_inputs,
			outputs = control_outputs + meta_outputs
		).then(redetect_frame, inputs = preview_inputs, outputs = preview_image)

	SKIP_SWAP_BUTTON.click(
		lambda scope, start, end, frame : apply_by_scope(scope, start, end, frame, None, 'skip_swap'),
		inputs = scope_inputs,
		outputs = control_outputs + meta_outputs
	).then(redetect_frame, inputs = preview_inputs, outputs = preview_image)

	SKIP_PROCESS_BUTTON.click(
		lambda scope, start, end, frame : apply_by_scope(scope, start, end, frame, None, 'skip_process'),
		inputs = scope_inputs,
		outputs = control_outputs + meta_outputs
	).then(redetect_frame, inputs = preview_inputs, outputs = preview_image)

	RESET_DEFAULT_BUTTON.click(reset_defaults, outputs = control_outputs)\
		.then(redetect_frame, inputs = preview_inputs, outputs = preview_image)\
		.then(refresh_meta, inputs = [ preview_frame_slider ], outputs = meta_outputs)

	CLEAR_PATCHES_BUTTON.click(clear_patches, outputs = meta_outputs)\
		.then(redetect_frame, inputs = preview_inputs, outputs = preview_image)

	DELETE_RULE_BUTTON.click(delete_rule, inputs = [ RULE_ID_TEXTBOX, preview_frame_slider ], outputs = meta_outputs)\
		.then(redetect_frame, inputs = preview_inputs, outputs = preview_image)

	if preview_frame_slider:
		preview_frame_slider.release(refresh_meta, inputs = [ preview_frame_slider ], outputs = meta_outputs, show_progress = 'hidden')
		preview_frame_slider.change(refresh_meta, inputs = [ preview_frame_slider ], outputs = meta_outputs, show_progress = 'hidden', trigger_mode = 'once')


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


def redetect_frame(preview_mode : str, preview_resolution : str, frame_number : int = 0) -> gradio.Image:
	clear_faces()
	return update_preview_image(preview_mode, preview_resolution, frame_number)


def refresh_meta(frame_number : int = 0) -> Tuple[gradio.Markdown, gradio.Markdown]:
	return gradio.Markdown(value = frame_override.format_rules_markdown()), gradio.Markdown(value = frame_override.format_effective_source(int(frame_number or 0)))


def clear_patches() -> Tuple[gradio.Markdown, gradio.Markdown]:
	frame_override.clear_all()
	clear_faces()
	return refresh_meta(0)


def delete_rule(rule_id : str, frame_number : int = 0) -> Tuple[gradio.Markdown, gradio.Markdown]:
	if rule_id:
		frame_override.remove_rule(rule_id.strip())
		clear_faces()
	return refresh_meta(frame_number)


def apply_by_scope(scope : str, range_start : float, range_end : float, frame_number : float, preset_name : Optional[str], action : str) -> Tuple[Any, ...]:
	scope_key = _normalize_scope(scope)
	frame_number = int(frame_number or 0)
	start_frame = int(range_start or 0)
	end_frame = int(range_end or 0)

	if scope_key == 'global':
		if action in { 'skip_swap', 'skip_process' }:
			# 跳过类动作无全局语义，降级为当前帧补丁
			frame_override.add_frame_rule(frame_number, action = action, label = action) #type:ignore[arg-type]
			return _empty_control_values() + refresh_meta(frame_number)
		if preset_name:
			apply_fix(preset_name)
		return _build_control_values() + refresh_meta(frame_number)

	params = {}
	if preset_name:
		params = frame_override.build_preset_params(preset_name, current_mask_types = state_manager.get_item('face_mask_types'))

	if scope_key == 'frame':
		frame_override.add_frame_rule(frame_number, action = action, preset = preset_name, params = params, label = preset_name or action) #type:ignore[arg-type]
	elif scope_key == 'range':
		if end_frame < start_frame:
			start_frame, end_frame = end_frame, start_frame
		if start_frame == end_frame == 0 and is_video(state_manager.get_item('target_path')):
			# 未填区间时，用当前帧作为单点区间，避免误写 0-0 全片
			start_frame = frame_number
			end_frame = frame_number
		frame_override.add_range_rule(start_frame, end_frame, action = action, preset = preset_name, params = params, label = preset_name or action) #type:ignore[arg-type]

	# 帧/区间不回写全局控件
	return _empty_control_values() + refresh_meta(frame_number)


def apply_fix(preset_name : str) -> Tuple[gradio.CheckboxGroup, gradio.Slider, gradio.Slider, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	"""供 diagnostics 等继续按「全局」调用。"""
	params = frame_override.build_preset_params(preset_name, current_mask_types = state_manager.get_item('face_mask_types'))
	for key, value in params.items():
		state_manager.set_item(key, value) #type:ignore[arg-type]
	return _build_control_values()


def reset_defaults() -> Tuple[gradio.CheckboxGroup, gradio.Slider, gradio.Slider, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	state_manager.set_item('face_detector_angles', config.get_int_list('face_detector', 'face_detector_angles', '0'))
	state_manager.set_item('face_detector_score', config.get_float_value('face_detector', 'face_detector_score', '0.5'))
	state_manager.set_item('face_landmarker_score', config.get_float_value('face_landmarker', 'face_landmarker_score', '0.5'))
	state_manager.set_item('reference_face_distance', config.get_float_value('face_selector', 'reference_face_distance', '0.3'))
	state_manager.set_item('face_mask_types', config.get_str_list('face_masker', 'face_mask_types', 'box'))
	state_manager.set_item('face_mask_blur', config.get_float_value('face_masker', 'face_mask_blur', '0.3'))
	return _build_control_values()


def _normalize_scope(scope : str) -> str:
	if scope in { '当前帧', 'frame' }:
		return 'frame'
	if scope in { '区间', 'range' }:
		return 'range'
	return 'global'


def _empty_control_values() -> Tuple[gradio.CheckboxGroup, gradio.Slider, gradio.Slider, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	return (
		gradio.CheckboxGroup(),
		gradio.Slider(),
		gradio.Slider(),
		gradio.Slider(),
		gradio.CheckboxGroup(),
		gradio.Slider()
	)


def _build_control_values() -> Tuple[gradio.CheckboxGroup, gradio.Slider, gradio.Slider, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	return (
		gradio.CheckboxGroup(value = state_manager.get_item('face_detector_angles')),
		gradio.Slider(value = state_manager.get_item('face_detector_score')),
		gradio.Slider(value = state_manager.get_item('face_landmarker_score')),
		gradio.Slider(value = state_manager.get_item('reference_face_distance')),
		gradio.CheckboxGroup(value = state_manager.get_item('face_mask_types')),
		gradio.Slider(value = state_manager.get_item('face_mask_blur'))
	)
