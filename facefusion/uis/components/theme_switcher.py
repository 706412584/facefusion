from typing import Optional

import gradio

from facefusion.uis.core import register_ui_component

THEME_SWITCHER_BUTTON : Optional[gradio.Button] = None

# 页面加载时读取上次选择并自动套用：默认跟随 Gradio 当前状态，
# 仅当用户此前手动选过主题时才覆盖。
THEME_LOAD_JS =\
'''
() => {
	try {
		const saved = localStorage.getItem('facefusion-theme');
		if (saved === 'dark') {
			document.body.classList.add('dark');
		}
		if (saved === 'light') {
			document.body.classList.remove('dark');
		}
	} catch (error) {}
	return [];
}
'''

# 客户端切换深色/浅色：Gradio 的主题变量同时定义了浅色与 *_dark 两套，
# 通过在 body 上增删 'dark' 类即可实时切换，无需刷新页面。
THEME_TOGGLE_JS =\
'''
() => {
	const root = document.querySelector('gradio-app') || document;
	const body = (root.shadowRoot ? root.shadowRoot.querySelector('.gradio-container') : null) || document.body;
	const isDark = document.body.classList.toggle('dark');
	if (body !== document.body) {
		body.classList.toggle('dark', isDark);
	}
	try {
		localStorage.setItem('facefusion-theme', isDark ? 'dark' : 'light');
	} catch (error) {}
	return [];
}
'''


def render() -> None:
	global THEME_SWITCHER_BUTTON

	THEME_SWITCHER_BUTTON = gradio.Button(
		value = '深色 / 浅色',
		size = 'sm',
		elem_classes = [ 'theme-switcher-button' ]
	)
	register_ui_component('theme_switcher_button', THEME_SWITCHER_BUTTON)


def listen() -> None:
	# fn 为 None，仅执行客户端 JS，不触发任何服务端处理
	THEME_SWITCHER_BUTTON.click(None, inputs = [], outputs = [], js = THEME_TOGGLE_JS)
