import gradio

from facefusion import state_manager
from facefusion.uis.components import image_editor


def pre_check() -> bool:
	return True


def render() -> gradio.Blocks:
	with gradio.Blocks() as layout:
		with gradio.Row():
			with gradio.Column(scale = 1):
				image_editor.render()
	return layout


def listen() -> None:
	image_editor.listen()


def run(ui : gradio.Blocks) -> None:
	ui.launch(favicon_path = 'facefusion.ico', inbrowser = state_manager.get_item('open_browser'))
