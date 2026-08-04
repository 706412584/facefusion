from typing import Any, Dict, List, Optional, Tuple

import gradio

import facefusion.choices
from facefusion import state_manager, translator
from facefusion.processors.modules.face_enhancer import choices as face_enhancer_choices
from facefusion.processors.modules.face_swapper import choices as face_swapper_choices
from facefusion.uis.core import get_ui_component, register_ui_component

PRESET_SPEED_BUTTON : Optional[gradio.Button] = None
PRESET_BALANCED_BUTTON : Optional[gradio.Button] = None
PRESET_QUALITY_BUTTON : Optional[gradio.Button] = None

# 三档质量/速度预设：在速度与换脸效果之间做不同取舍
PRESET_SET : Dict[str, Dict[str, Any]] =\
{
	'speed':
	{
		'processors': [ 'face_swapper' ],
		'face_swapper_model': 'inswapper_128',
		'face_swapper_pixel_boost': '128x128',
		'face_mask_types': [ 'box' ],
		'face_mask_blur': 0.3
	},
	'balanced':
	{
		'processors': [ 'face_swapper' ],
		'face_swapper_model': 'hyperswap_1a_256',
		'face_swapper_pixel_boost': '256x256',
		'face_mask_types': [ 'box', 'occlusion' ],
		'face_mask_blur': 0.3
	},
	'quality':
	{
		'processors': [ 'face_swapper', 'face_enhancer' ],
		'face_swapper_model': 'hyperswap_1a_256',
		'face_swapper_pixel_boost': '512x512',
		'face_enhancer_model': 'gfpgan_1.4',
		'face_enhancer_blend': 80,
		'face_mask_types': [ 'box', 'occlusion' ],
		'face_mask_blur': 0.3
	}
}


def render() -> None:
	global PRESET_SPEED_BUTTON
	global PRESET_BALANCED_BUTTON
	global PRESET_QUALITY_BUTTON

	gradio.Markdown('### 质量预设（一键切换）')
	with gradio.Row():
		PRESET_SPEED_BUTTON = gradio.Button(
			value = '极速',
			size = 'sm'
		)
		PRESET_BALANCED_BUTTON = gradio.Button(
			value = '均衡',
			size = 'sm',
			variant = 'primary'
		)
		PRESET_QUALITY_BUTTON = gradio.Button(
			value = '高质量',
			size = 'sm'
		)
	register_ui_component('preset_speed_button', PRESET_SPEED_BUTTON)
	register_ui_component('preset_balanced_button', PRESET_BALANCED_BUTTON)
	register_ui_component('preset_quality_button', PRESET_QUALITY_BUTTON)


def listen() -> None:
	outputs = _collect_outputs()

	if outputs:
		PRESET_SPEED_BUTTON.click(lambda : apply_preset('speed'), outputs = outputs)
		PRESET_BALANCED_BUTTON.click(lambda : apply_preset('balanced'), outputs = outputs)
		PRESET_QUALITY_BUTTON.click(lambda : apply_preset('quality'), outputs = outputs)


def _collect_outputs() -> List[Any]:
	component_names =\
	[
		'processors_checkbox_group',
		'face_swapper_model_dropdown',
		'face_swapper_pixel_boost_dropdown',
		'face_enhancer_model_dropdown',
		'face_enhancer_blend_slider',
		'face_mask_types_checkbox_group',
		'face_mask_blur_slider'
	]
	return [ get_ui_component(component_name) for component_name in component_names ]


def apply_preset(preset_name : str) -> Tuple[gradio.CheckboxGroup, gradio.Dropdown, gradio.Dropdown, gradio.Dropdown, gradio.Slider, gradio.CheckboxGroup, gradio.Slider]:
	preset = PRESET_SET.get(preset_name)

	# 同步底层状态，确保实际处理使用预设参数
	state_manager.set_item('processors', preset.get('processors'))
	state_manager.set_item('face_swapper_model', preset.get('face_swapper_model'))
	state_manager.set_item('face_swapper_pixel_boost', preset.get('face_swapper_pixel_boost'))
	state_manager.set_item('face_mask_types', preset.get('face_mask_types'))
	state_manager.set_item('face_mask_blur', preset.get('face_mask_blur'))

	if preset.get('face_enhancer_model'):
		state_manager.set_item('face_enhancer_model', preset.get('face_enhancer_model'))
	if preset.get('face_enhancer_blend') is not None:
		state_manager.set_item('face_enhancer_blend', preset.get('face_enhancer_blend'))

	pixel_boost_choices = face_swapper_choices.face_swapper_set.get(preset.get('face_swapper_model'))

	# 把新值连同（已翻译的）choices 一起回传，保持中文标签并避免 value 不在 choices 中的告警；
	# 面板显隐由 processors_checkbox_group 的 change 级联自动处理
	return (
		gradio.CheckboxGroup(value = preset.get('processors')),
		gradio.Dropdown(value = preset.get('face_swapper_model'), choices = translator.translate_choices(face_swapper_choices.face_swapper_models)),
		gradio.Dropdown(value = preset.get('face_swapper_pixel_boost'), choices = pixel_boost_choices),
		gradio.Dropdown(value = state_manager.get_item('face_enhancer_model'), choices = translator.translate_choices(face_enhancer_choices.face_enhancer_models)),
		gradio.Slider(value = state_manager.get_item('face_enhancer_blend')),
		gradio.CheckboxGroup(value = preset.get('face_mask_types'), choices = translator.translate_choices(facefusion.choices.face_mask_types)),
		gradio.Slider(value = preset.get('face_mask_blur'))
	)
