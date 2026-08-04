from typing import List, Optional

import gradio

from facefusion import state_manager, translator
from facefusion.filesystem import get_file_name, resolve_file_paths
from facefusion.processors.core import get_processors_modules
from facefusion.uis.core import register_ui_component
from facefusion.uis.ui_tips import tip

PROCESSORS_CHECKBOX_GROUP : Optional[gradio.CheckboxGroup] = None


def render() -> None:
	global PROCESSORS_CHECKBOX_GROUP

	PROCESSORS_CHECKBOX_GROUP = gradio.CheckboxGroup(
		label = translator.get('uis.processors_checkbox_group'),
		choices = translator.translate_choices(sort_processors()),
		value = state_manager.get_item('processors'),
		info = tip('processors')
	)
	register_ui_component('processors_checkbox_group', PROCESSORS_CHECKBOX_GROUP)


def listen() -> None:
	PROCESSORS_CHECKBOX_GROUP.change(update_processors, inputs = PROCESSORS_CHECKBOX_GROUP, outputs = PROCESSORS_CHECKBOX_GROUP)


def update_processors(processors : List[str]) -> gradio.CheckboxGroup:
	for processor_module in get_processors_modules(state_manager.get_item('processors')):
		if hasattr(processor_module, 'clear_inference_pool'):
			processor_module.clear_inference_pool()

	for processor_module in get_processors_modules(processors):
		if not processor_module.pre_check():
			# pre_check 失败（例如模型缺失）时保留当前已选项，避免清空整个选择状态
			return gradio.CheckboxGroup(value = state_manager.get_item('processors'), choices = translator.translate_choices(sort_processors()))

	state_manager.set_item('processors', processors)
	return gradio.CheckboxGroup(value = state_manager.get_item('processors'), choices = translator.translate_choices(sort_processors()))


def sort_processors(processors : Optional[List[str]] = None) -> List[str]:
	# 始终返回固定顺序，避免勾选/取消时复选框位置跳动导致的选择状态错乱
	return [ get_file_name(file_path) for file_path in resolve_file_paths('facefusion/processors/modules') ]
