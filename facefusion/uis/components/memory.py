from typing import Optional

import gradio

import facefusion.choices
from facefusion import state_manager, translator
from facefusion.types import VideoMemoryStrategy
from facefusion.uis.ui_tips import tip

VIDEO_MEMORY_STRATEGY_DROPDOWN : Optional[gradio.Dropdown] = None


def render() -> None:
	global VIDEO_MEMORY_STRATEGY_DROPDOWN

	VIDEO_MEMORY_STRATEGY_DROPDOWN = gradio.Dropdown(
		label = translator.get('uis.video_memory_strategy_dropdown'),
		choices = translator.translate_choices(facefusion.choices.video_memory_strategies),
		value = translator.translate_choice(state_manager.get_item('video_memory_strategy')),
		info = tip('video_memory_strategy')
	)


def listen() -> None:
	VIDEO_MEMORY_STRATEGY_DROPDOWN.change(update_video_memory_strategy, inputs = VIDEO_MEMORY_STRATEGY_DROPDOWN)


def update_video_memory_strategy(video_memory_strategy : VideoMemoryStrategy) -> None:
	video_memory_strategy = translator.untranslate_choice(video_memory_strategy)
	state_manager.set_item('video_memory_strategy', video_memory_strategy)
