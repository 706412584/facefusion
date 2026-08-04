from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.common_helper import get_first
from facefusion.face_store import clear_faces
from facefusion.filesystem import filter_image_paths, is_image, is_video
from facefusion.uis.core import register_ui_component
from facefusion.uis.types import ComponentOptions, File

TARGET_FILE : Optional[gradio.File] = None
TARGET_IMAGE : Optional[gradio.Image] = None
TARGET_VIDEO : Optional[gradio.Video] = None


def render() -> None:
	global TARGET_FILE
	global TARGET_IMAGE
	global TARGET_VIDEO

	target_paths = state_manager.get_item('target_paths') or ([ state_manager.get_item('target_path') ] if state_manager.get_item('target_path') else None)
	target_file_value = target_paths if target_paths else None
	target_preview_path = get_first(target_paths) if target_paths else None
	is_target_image = is_image(target_preview_path)
	is_target_video = is_video(target_preview_path)
	TARGET_FILE = gradio.File(
		label = translator.get('uis.target_file'),
		file_count = 'multiple',
		value = target_file_value if is_target_image or is_target_video else None
	)
	target_image_options : ComponentOptions =\
	{
		'show_label': False,
		'visible': False
	}
	target_video_options : ComponentOptions =\
	{
		'show_label': False,
		'visible': False
	}
	if is_target_image:
		target_image_options['value'] = target_preview_path
		target_image_options['visible'] = True
	if is_target_video:
		target_video_options['value'] = target_preview_path
		target_video_options['visible'] = True
	TARGET_IMAGE = gradio.Image(**target_image_options)
	TARGET_VIDEO = gradio.Video(**target_video_options)
	register_ui_component('target_image', TARGET_IMAGE)
	register_ui_component('target_video', TARGET_VIDEO)


def listen() -> None:
	TARGET_FILE.change(update, inputs = TARGET_FILE, outputs = [ TARGET_IMAGE, TARGET_VIDEO ])


def update(files : List[File]) -> Tuple[gradio.Image, gradio.Video]:
	clear_faces()
	file_names = [ file.name for file in files ] if files else []
	target_paths = filter_image_paths(file_names) + [ file_name for file_name in file_names if is_video(file_name) ]

	if target_paths:
		target_preview_path = get_first(target_paths)
		state_manager.set_item('target_paths', target_paths)
		state_manager.set_item('target_path', target_preview_path)

		if is_image(target_preview_path):
			return gradio.Image(value = target_preview_path, visible = True), gradio.Video(value = None, visible = False)
		if is_video(target_preview_path):
			return gradio.Image(value = None, visible = False), gradio.Video(value = target_preview_path, visible = True)

	state_manager.clear_item('target_paths')
	state_manager.clear_item('target_path')
	return gradio.Image(value = None, visible = False), gradio.Video(value = None, visible = False)
