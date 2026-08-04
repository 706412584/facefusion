from typing import Optional

import gradio

from facefusion import state_manager, translator
from facefusion.filesystem import is_video
from facefusion.uis import choices as uis_choices
from facefusion.uis.core import get_ui_components, register_ui_component
from facefusion.uis.types import ComponentOptions
from facefusion.vision import count_video_frame_total

PREVIEW_FRAME_SLIDER: Optional[gradio.Slider] = None
PREVIEW_MODE_DROPDOWN: Optional[gradio.Dropdown] = None
PREVIEW_RESOLUTION_DROPDOWN: Optional[gradio.Dropdown] = None
PREVIEW_PLAY_BUTTON: Optional[gradio.Button] = None
PREVIEW_STOP_BUTTON: Optional[gradio.Button] = None
PREVIEW_SPEED_SLIDER: Optional[gradio.Slider] = None


def render() -> None:
	global PREVIEW_FRAME_SLIDER, PREVIEW_MODE_DROPDOWN, PREVIEW_RESOLUTION_DROPDOWN, PREVIEW_PLAY_BUTTON, PREVIEW_STOP_BUTTON, PREVIEW_SPEED_SLIDER

	preview_frame_slider_options : ComponentOptions =\
	{
		'label': translator.get('uis.preview_frame_slider'),
		'step': 1,
		'minimum': 0,
		'maximum': 100,
		'visible': False
	}
	if is_video(state_manager.get_item('target_path')):
		video_frame_total = count_video_frame_total(state_manager.get_item('target_path'))
		preview_frame_slider_options['value'] = state_manager.get_item('reference_frame_number')
		preview_frame_slider_options['maximum'] = video_frame_total - 1
		preview_frame_slider_options['visible'] = True
	PREVIEW_FRAME_SLIDER = gradio.Slider(**preview_frame_slider_options)
	
	with gradio.Row():
		PREVIEW_MODE_DROPDOWN = gradio.Dropdown(
			label = translator.get('uis.preview_mode_dropdown'),
			value = translator.translate_choice(uis_choices.preview_modes[0]),
			choices = translator.translate_choices(uis_choices.preview_modes),
			visible = True
		)
		PREVIEW_RESOLUTION_DROPDOWN = gradio.Dropdown(
			label = translator.get('uis.preview_resolution_dropdown'),
			value = uis_choices.preview_resolutions[-1],
			choices = uis_choices.preview_resolutions,
			visible = True
		)
	
	# 添加播放控制
	with gradio.Row():
		PREVIEW_PLAY_BUTTON = gradio.Button(
			value = '播放预览',
			visible = False
		)
		PREVIEW_STOP_BUTTON = gradio.Button(
			value = '停止',
			visible = False
		)
		PREVIEW_SPEED_SLIDER = gradio.Slider(
			label = '播放速度 (帧/秒)',
			minimum = 1,
			maximum = 30,
			step = 1,
			value = 20,
			visible = False
		)
	
	register_ui_component('preview_mode_dropdown', PREVIEW_MODE_DROPDOWN)
	register_ui_component('preview_resolution_dropdown', PREVIEW_RESOLUTION_DROPDOWN)
	register_ui_component('preview_frame_slider', PREVIEW_FRAME_SLIDER)
	register_ui_component('preview_play_button', PREVIEW_PLAY_BUTTON)
	register_ui_component('preview_stop_button', PREVIEW_STOP_BUTTON)
	register_ui_component('preview_speed_slider', PREVIEW_SPEED_SLIDER)


def listen() -> None:
	for ui_component in get_ui_components([ 'target_image', 'target_video' ]):
		for method in [ 'change', 'clear' ]:
			getattr(ui_component, method)(update_preview_frame_slider, outputs = PREVIEW_FRAME_SLIDER)
			getattr(ui_component, method)(update_play_controls_visibility, outputs = [ PREVIEW_PLAY_BUTTON, PREVIEW_STOP_BUTTON, PREVIEW_SPEED_SLIDER ])


def update_play_controls_visibility() -> tuple:
	"""更新播放控制的可见性"""
	is_video_loaded = is_video(state_manager.get_item('target_path'))
	return gradio.Button(visible = is_video_loaded), gradio.Button(visible = is_video_loaded), gradio.Slider(visible = is_video_loaded)


def update_preview_frame_slider() -> gradio.Slider:
	if is_video(state_manager.get_item('target_path')):
		video_frame_total = count_video_frame_total(state_manager.get_item('target_path'))
		return gradio.Slider(maximum = video_frame_total - 1, visible = True)
	return gradio.Slider(value = 0, visible = False)
