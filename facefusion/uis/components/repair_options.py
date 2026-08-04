from typing import Any, List, Optional, Tuple

import gradio

import facefusion.choices
from facefusion import config, state_manager
from facefusion.face_store import clear_faces
from facefusion.uis.components.preview import update_preview_image
from facefusion.uis.core import get_ui_component, register_ui_component

REDETECT_FRAME_BUTTON : Optional[gradio.Button] = None
FIX_NO_SWAP_BUTTON : Optional[gradio.Button] = None
FIX_DISTORTION_BUTTON : Optional[gradio.Button] = None
FIX_DOUBLE_BUTTON : Optional[gradio.Button] = None
FIX_EDGE_BUTTON : Optional[gradio.Button] = None
RESET_DEFAULT_BUTTON : Optional[gradio.Button] = None

# 这些修复方案只调整"检测 / 选脸 / 遮罩"层（真正决定某帧能否正确替换的环节），
# 不切换检测器模型，避免触发模型下载或离线失败；参数会写入全局状态，因此对最终出片同样生效。


def render() -> None:
	global REDETECT_FRAME_BUTTON
	global FIX_NO_SWAP_BUTTON
	global FIX_DISTORTION_BUTTON
	global FIX_DOUBLE_BUTTON
	global FIX_EDGE_BUTTON
	global RESET_DEFAULT_BUTTON

	gradio.Markdown('### 疑难帧修复（作用于全局，出片同样生效）')
	with gradio.Row():
		REDETECT_FRAME_BUTTON = gradio.Button(
			value = '重新检测此帧',
			size = 'sm'
		)
		FIX_NO_SWAP_BUTTON = gradio.Button(
			value = '人脸不替换',
			size = 'sm'
		)
	with gradio.Row():
		FIX_DISTORTION_BUTTON = gradio.Button(
			value = '面部扭曲/歪斜',
			size = 'sm'
		)
		FIX_DOUBLE_BUTTON = gradio.Button(
			value = '两脸重合/重复换',
			size = 'sm'
		)
	with gradio.Row():
		FIX_EDGE_BUTTON = gradio.Button(
			value = '边缘/遮挡穿帮',
			size = 'sm'
		)
		RESET_DEFAULT_BUTTON = gradio.Button(
			value = '恢复默认参数',
			size = 'sm'
		)
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

	if not all(preview_inputs) or not preview_image:
		return

	# 重新检测：清掉这一帧的检测缓存后重算预览（不改参数）
	REDETECT_FRAME_BUTTON.click(redetect_frame, inputs = preview_inputs, outputs = preview_image)

	for button, preset_name in\
	[
		(FIX_NO_SWAP_BUTTON, 'no_swap'),
		(FIX_DISTORTION_BUTTON, 'distortion'),
		(FIX_DOUBLE_BUTTON, 'double'),
		(FIX_EDGE_BUTTON, 'edge')
	]:
		# 先应用修复参数并回写控件，再清缓存刷新预览
		button.click(lambda preset_name = preset_name : apply_fix(preset_name), outputs = control_outputs)\
			.then(redetect_frame, inputs = preview_inputs, outputs = preview_image)

	# 恢复默认：把检测/选脸/遮罩参数还原成程序启动时的默认值，再清缓存刷新预览
	RESET_DEFAULT_BUTTON.click(reset_defaults, outputs = control_outputs)\
		.then(redetect_frame, inputs = preview_inputs, outputs = preview_image)


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
	# 人脸检测结果按帧像素哈希缓存，必须先清缓存，改过的检测参数才会重新生效
	clear_faces()
	return update_preview_image(preview_mode, preview_resolution, frame_number)


def apply_fix(preset_name : str) -> Tuple[gradio.CheckboxGroup, gradio.Slider, gradio.Slider, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	if preset_name == 'no_swap':
		# 人脸漏检 / 匹配过严：开多角度检测、降低检测阈值、放宽参考人脸匹配距离
		state_manager.set_item('face_detector_angles', [ 0, 90, 180, 270 ])
		state_manager.set_item('face_detector_score', 0.3)
		state_manager.set_item('reference_face_distance', 0.6)

	if preset_name == 'distortion':
		# 关键点拟合错误导致的扭曲：提高关键点采用阈值（不确定时退回更稳的检测点）、
		# 略升检测阈值丢弃低质量误检、开多角度并叠加遮挡遮罩
		state_manager.set_item('face_landmarker_score', 0.5)
		state_manager.set_item('face_detector_score', 0.5)
		state_manager.set_item('face_detector_angles', [ 0, 90, 180, 270 ])
		_ensure_mask_type('occlusion')

	if preset_name == 'double':
		# 两脸重合 / 同一张脸被换两次：大角度仰头/侧脸时多角度会重复检出同一张脸。
		# 收紧到单一角度减少重复源，并提高检测/关键点阈值丢弃低质量的重复框。
		state_manager.set_item('face_detector_angles', [ 0 ])
		state_manager.set_item('face_detector_score', 0.6)
		state_manager.set_item('face_landmarker_score', 0.5)

	if preset_name == 'edge':
		# 边缘 / 遮挡穿帮：框遮罩 + 遮挡遮罩，并加大边缘羽化
		state_manager.set_item('face_mask_types', [ 'box', 'occlusion' ])
		state_manager.set_item('face_mask_blur', 0.5)

	return _build_control_values()


def reset_defaults() -> Tuple[gradio.CheckboxGroup, gradio.Slider, gradio.Slider, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	# 按程序启动时的来源（配置文件 + 与 program.py 相同的回退值）还原各参数
	state_manager.set_item('face_detector_angles', config.get_int_list('face_detector', 'face_detector_angles', '0'))
	state_manager.set_item('face_detector_score', config.get_float_value('face_detector', 'face_detector_score', '0.5'))
	state_manager.set_item('face_landmarker_score', config.get_float_value('face_landmarker', 'face_landmarker_score', '0.5'))
	state_manager.set_item('reference_face_distance', config.get_float_value('face_selector', 'reference_face_distance', '0.3'))
	state_manager.set_item('face_mask_types', config.get_str_list('face_masker', 'face_mask_types', 'box'))
	state_manager.set_item('face_mask_blur', config.get_float_value('face_masker', 'face_mask_blur', '0.3'))
	return _build_control_values()


def _ensure_mask_type(mask_type : str) -> None:
	face_mask_types = list(state_manager.get_item('face_mask_types') or [])
	if mask_type not in face_mask_types:
		face_mask_types.append(mask_type)
	state_manager.set_item('face_mask_types', face_mask_types)


def _build_control_values() -> Tuple[gradio.CheckboxGroup, gradio.Slider, gradio.Slider, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	# 全部按当前状态回写，保证控件与实际生效参数一致；遮罩相关面板的显隐由其 change 级联自动处理
	return (
		gradio.CheckboxGroup(value = state_manager.get_item('face_detector_angles')),
		gradio.Slider(value = state_manager.get_item('face_detector_score')),
		gradio.Slider(value = state_manager.get_item('face_landmarker_score')),
		gradio.Slider(value = state_manager.get_item('reference_face_distance')),
		gradio.CheckboxGroup(value = state_manager.get_item('face_mask_types')),
		gradio.Slider(value = state_manager.get_item('face_mask_blur'))
	)
