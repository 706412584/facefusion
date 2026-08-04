from typing import Optional

import gradio

from facefusion.uis.core import register_ui_component
from facefusion.uis.ui_tips import FAQ_MARKDOWN

HELP_GUIDE_BUTTON : Optional[gradio.Button] = None
HELP_GUIDE_ACCORDION : Optional[gradio.Accordion] = None


def render() -> None:
	global HELP_GUIDE_BUTTON
	global HELP_GUIDE_ACCORDION

	with gradio.Row():
		HELP_GUIDE_BUTTON = gradio.Button(
			value = '疑难解答 / 参数说明',
			variant = 'secondary'
		)
	with gradio.Accordion('疑难解答（点击上方按钮展开/收起也可直接打开）', open = False) as HELP_GUIDE_ACCORDION:
		gradio.Markdown(FAQ_MARKDOWN)
		gradio.Markdown(
			'提示：各下拉框、滑块下方的灰色小字就是该参数的用法说明；'
			'鼠标移到标签附近也可查看 Gradio 自带的 info 提示。'
		)

	register_ui_component('help_guide_button', HELP_GUIDE_BUTTON)


def listen() -> None:
	# 按钮用于把用户注意力引导到手风琴；Gradio Accordion 本身可点开
	if HELP_GUIDE_BUTTON:
		HELP_GUIDE_BUTTON.click(lambda: gradio.Accordion(open = True), outputs = HELP_GUIDE_ACCORDION)
