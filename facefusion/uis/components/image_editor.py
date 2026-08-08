from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Tuple

import gradio
import numpy
from huggingface_hub import snapshot_download
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from facefusion.filesystem import create_directory, is_directory
from facefusion.uis.core import register_ui_component

IMAGE_EDITOR_CANVAS : Optional[gradio.ImageEditor] = None
IMAGE_EDITOR_PROMPT_TEXTBOX : Optional[gradio.Textbox] = None
IMAGE_EDITOR_NEGATIVE_PROMPT_TEXTBOX : Optional[gradio.Textbox] = None
IMAGE_EDITOR_MODEL_DROPDOWN : Optional[gradio.Dropdown] = None
IMAGE_EDITOR_STRENGTH_SLIDER : Optional[gradio.Slider] = None
IMAGE_EDITOR_STEPS_SLIDER : Optional[gradio.Slider] = None
IMAGE_EDITOR_SEED_NUMBER : Optional[gradio.Number] = None
IMAGE_EDITOR_WIDTH_SLIDER : Optional[gradio.Slider] = None
IMAGE_EDITOR_HEIGHT_SLIDER : Optional[gradio.Slider] = None
IMAGE_EDITOR_CFG_SLIDER : Optional[gradio.Slider] = None
IMAGE_EDITOR_SAMPLER_DROPDOWN : Optional[gradio.Dropdown] = None
IMAGE_EDITOR_INSTALL_BUTTON : Optional[gradio.Button] = None
IMAGE_EDITOR_MODE_RADIO : Optional[gradio.Radio] = None
IMAGE_EDITOR_APPLY_BUTTON : Optional[gradio.Button] = None
IMAGE_EDITOR_OUTPUT_IMAGE : Optional[gradio.Image] = None
IMAGE_EDITOR_MASK_PREVIEW_IMAGE : Optional[gradio.Image] = None
IMAGE_EDITOR_LOG_MARKDOWN : Optional[gradio.Markdown] = None
IMAGE_EDITOR_STATUS_MARKDOWN : Optional[gradio.Markdown] = None
IMAGE_EDITOR_INFO_MARKDOWN : Optional[gradio.Markdown] = None
IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX : Optional[gradio.Checkbox] = None
IMAGE_EDITOR_NSFW_MODE_RADIO : Optional[gradio.Radio] = None
IMAGE_EDITOR_NSFW_CONFIRM_CHECKBOX : Optional[gradio.Checkbox] = None
IMAGE_EDITOR_NSFW_NOTICE_MARKDOWN : Optional[gradio.Markdown] = None

DEFAULT_PROMPT = 'clean seamless background, remove text, no letters, no watermark, natural texture, high quality'
DEFAULT_NEGATIVE_PROMPT = 'text, letters, words, watermark, logo, signature, caption, subtitle, gibberish, deformed, blurry, low quality'
DEFAULT_STRENGTH = 0.65
DEFAULT_STEPS = 28
DEFAULT_SEED = 20260807
IMG2IMG_STRENGTH = 0.50
INPAINT_STRENGTH = 0.75
# 输出图缩略图最大边长，避免大图导致滚动卡顿
OUTPUT_PREVIEW_MAX = 768
_INPAINT_PIPELINE_CACHE : Dict[str, object] = {}

# sd.cpp 后端（Z-Image Turbo GGUF 拆分加载）
SDCPP_BIN = os.environ.get('FACEVISION_SDCPP_BIN', r'D:\models\sd-cpp\sd-cli.exe')
SDCPP_DIFFUSION_MODEL = os.environ.get('FACEVISION_SDCPP_DIFFUSION', r'D:\models\z-image\z-image-turbo-Q4_K_M.gguf')
SDCPP_VAE = os.environ.get('FACEVISION_SDCPP_VAE', r'D:\models\z-image\components\ae.safetensors')
SDCPP_LLM = os.environ.get('FACEVISION_SDCPP_LLM', r'D:\models\z-image\components\qwen3-4b-Q4_K_M.gguf')

MODEL_CATALOG : List[Dict[str, str]] = [
	{
		'label': '默认 · Z-Image Turbo (GGUF)',
		'repo_id': 'unsloth/Z-Image-Turbo-GGUF',
		'filename': 'z-image-turbo-Q4_K_M.gguf',
		'engine': 'sdcpp',
		'usage': '文生图 / 图生图 / 局部重绘主模型',
		'size_hint': 'Q4_K_M 量化，适合 8GB 显存',
		'notes': '默认模型。Qwen3-4B 文本编码器，原生支持中文 prompt。'
	},
	{
		'label': '可选 · SD 1.5 Inpainting',
		'repo_id': 'stable-diffusion-v1-5/stable-diffusion-inpainting',
		'engine': 'diffusers',
		'usage': '局部重绘 / 图片编辑（英文 prompt）',
		'size_hint': '适合 8GB 显存，首次下载较大',
		'notes': 'SD 1.5 CLIP 几乎不懂中文，创意编辑建议用英文。'
	},
	{
		'label': '可选 · RMBG 1.4',
		'repo_id': 'briaai/RMBG-1.4',
		'usage': '背景移除 / 自动 mask',
		'size_hint': '轻量，适合笔记本',
		'notes': '适合主体提取和自动选区。'
	},
	{
		'label': '可选 · NSFW 检测',
		'repo_id': 'Falconsai/nsfw_image_detection',
		'usage': '18+ 内容检测开关',
		'size_hint': '分类模型，部署较轻',
		'notes': '可用于编辑前后安全检查。'
	},
	{
		'label': '可选 · Real-ESRGAN',
		'repo_id': 'ai-forever/Real-ESRGAN',
		'usage': '放大 / 细节增强',
		'size_hint': '适合作为出图后处理',
		'notes': '用于最后一步放大更合适。'
	},
	{
		'label': '可选 · BiRefNet 分割',
		'repo_id': 'ZhengPeng7/BiRefNet',
		'usage': '高质量抠图 / 分割',
		'size_hint': '比 RMBG 更重，质量更高',
		'notes': '适合复杂边缘和主体分割。'
	},
	{
		'label': '可选 · IP-Adapter FaceID',
		'repo_id': 'h94/IP-Adapter-FaceID',
		'usage': '参考图驱动编辑',
		'size_hint': '高级控制组件',
		'notes': '后续做参考图编辑时再启用。'
	}
]

MODEL_BY_LABEL : Dict[str, Dict[str, str]] = { model.get('label'): model for model in MODEL_CATALOG }
MODEL_BY_REPO : Dict[str, Dict[str, str]] = { model.get('repo_id'): model for model in MODEL_CATALOG }
DEFAULT_MODEL_LABEL = MODEL_CATALOG[0].get('label')


def render() -> None:
	global IMAGE_EDITOR_CANVAS
	global IMAGE_EDITOR_PROMPT_TEXTBOX
	global IMAGE_EDITOR_NEGATIVE_PROMPT_TEXTBOX
	global IMAGE_EDITOR_MODEL_DROPDOWN
	global IMAGE_EDITOR_STRENGTH_SLIDER
	global IMAGE_EDITOR_STEPS_SLIDER
	global IMAGE_EDITOR_SEED_NUMBER
	global IMAGE_EDITOR_WIDTH_SLIDER
	global IMAGE_EDITOR_HEIGHT_SLIDER
	global IMAGE_EDITOR_CFG_SLIDER
	global IMAGE_EDITOR_SAMPLER_DROPDOWN
	global IMAGE_EDITOR_INSTALL_BUTTON
	global IMAGE_EDITOR_MODE_RADIO
	global IMAGE_EDITOR_APPLY_BUTTON
	global IMAGE_EDITOR_OUTPUT_IMAGE
	global IMAGE_EDITOR_MASK_PREVIEW_IMAGE
	global IMAGE_EDITOR_LOG_MARKDOWN
	global IMAGE_EDITOR_STATUS_MARKDOWN
	global IMAGE_EDITOR_INFO_MARKDOWN
	global IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX
	global IMAGE_EDITOR_NSFW_MODE_RADIO
	global IMAGE_EDITOR_NSFW_CONFIRM_CHECKBOX
	global IMAGE_EDITOR_NSFW_NOTICE_MARKDOWN

	gradio.Markdown(
		'### 图片编辑模式\n'
		'默认模型：**Z-Image Turbo (GGUF, Q4_K_M)**。\n\n'
		'**使用提示：**\n'
		'- **文生图**：纯文本生成，无需输入图片，写好提示词即可。\n'
		'- **图生图**：上传图片，不用涂 mask，全图重绘。适合换风格/换内容。\n'
		'- **局部重绘**：用白色画笔涂住要改的区域。\n'
		'- **去文字 / 去水印**：Z-Image 自动处理，提示词写 `remove text`。\n'
		'- 图生图强度 0.35–0.65；局部重绘 0.6–0.85。'
	)
	IMAGE_EDITOR_MODE_RADIO = gradio.Radio(
		choices = [ '文生图（纯文本）', '图生图（全图重绘）', '局部重绘（涂抹 mask）' ],
		value = '局部重绘（涂抹 mask）',
		label = '编辑模式',
		info = '文生图：仅文本；图生图：全图重绘；局部重绘：用白色画笔涂出要改的区域'
	)
	IMAGE_EDITOR_CANVAS = gradio.ImageEditor(
		label = '输入图片（文生图留空；局部重绘用白色画笔涂出要编辑的区域）',
		type = 'pil',
		image_mode = 'RGBA',
		brush = gradio.Brush(colors = [ '#ffffff' ], default_color = '#ffffff', color_mode = 'fixed'),
		eraser = gradio.Eraser(),
		layers = True,
		transforms = (),
		canvas_size = (768, 768)
	)
	IMAGE_EDITOR_PROMPT_TEXTBOX = gradio.Textbox(
		label = '编辑提示词（支持中文）',
		value = DEFAULT_PROMPT,
		lines = 2,
		info = 'Z-Image（Qwen3-4B）原生支持中文；去文字请用 remove text'
	)
	IMAGE_EDITOR_NEGATIVE_PROMPT_TEXTBOX = gradio.Textbox(
		label = '负向提示词',
		value = DEFAULT_NEGATIVE_PROMPT,
		lines = 2
	)
	with gradio.Row():
		IMAGE_EDITOR_STRENGTH_SLIDER = gradio.Slider(label = '编辑强度', minimum = 0.0, maximum = 1.0, step = 0.05, value = DEFAULT_STRENGTH)
		IMAGE_EDITOR_STEPS_SLIDER = gradio.Slider(label = '推理步数', minimum = 4, maximum = 40, step = 1, value = DEFAULT_STEPS)
		IMAGE_EDITOR_SEED_NUMBER = gradio.Number(label = '随机种子（-1 为随机）', value = DEFAULT_SEED, precision = 0)
	with gradio.Accordion('图像输出参数', open = False):
		with gradio.Row():
			IMAGE_EDITOR_WIDTH_SLIDER = gradio.Slider(label = '输出宽度', minimum = 256, maximum = 1024, step = 64, value = 512)
			IMAGE_EDITOR_HEIGHT_SLIDER = gradio.Slider(label = '输出高度', minimum = 256, maximum = 1024, step = 64, value = 512)
		with gradio.Row():
			IMAGE_EDITOR_CFG_SLIDER = gradio.Slider(label = 'CFG 引导强度', minimum = 1.0, maximum = 12.0, step = 0.5, value = 5.0, info = '越高越贴合提示词，太高易过饱和')
			IMAGE_EDITOR_SAMPLER_DROPDOWN = gradio.Dropdown(label = '采样方法', choices = [ 'euler_a', 'euler', 'dpm++2m', 'dpm++2mv', 'heun' ], value = 'euler_a')
	with gradio.Row():
		IMAGE_EDITOR_MODEL_DROPDOWN = gradio.Dropdown(
			label = '默认模型 / 可选模型',
			choices = [ model.get('label') for model in MODEL_CATALOG ],
			value = DEFAULT_MODEL_LABEL,
			info = '选择一个模型后点击一键安装'
		)
		IMAGE_EDITOR_INSTALL_BUTTON = gradio.Button(value = '一键安装所选模型', variant = 'primary', size = 'sm')
	IMAGE_EDITOR_APPLY_BUTTON = gradio.Button(value = '开始图片编辑', variant = 'primary', size = 'sm')
	with gradio.Row():
		# 输出图关闭交互（全屏/缩放），避免大图在滚动时反复重绘卡顿；按需下载用按钮
		IMAGE_EDITOR_OUTPUT_IMAGE = gradio.Image(label = '输出图片', type = 'pil', interactive = False, show_fullscreen_button = False, show_share_button = False)
		IMAGE_EDITOR_MASK_PREVIEW_IMAGE = gradio.Image(label = '本次识别到的 Mask', type = 'pil', interactive = False, show_fullscreen_button = False, show_share_button = False)
	IMAGE_EDITOR_LOG_MARKDOWN = gradio.Markdown(value = '### 运行日志\n等待执行。')
	IMAGE_EDITOR_STATUS_MARKDOWN = gradio.Markdown(value = _format_model_status(DEFAULT_MODEL_LABEL))
	IMAGE_EDITOR_INFO_MARKDOWN = gradio.Markdown(value = _format_model_info(DEFAULT_MODEL_LABEL))
	gradio.Markdown('#### NSFW 选项')
	IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX = gradio.Checkbox(label = '启用 NSFW 检测（18+）', value = False)
	IMAGE_EDITOR_NSFW_MODE_RADIO = gradio.Radio(label = '检测方式', choices = [ '仅提示', '检测并拦截' ], value = '仅提示', visible = False)
	IMAGE_EDITOR_NSFW_CONFIRM_CHECKBOX = gradio.Checkbox(label = '我已满 18 岁', value = False, visible = False)
	IMAGE_EDITOR_NSFW_NOTICE_MARKDOWN = gradio.Markdown(value = '开启后会在编辑前后执行 NSFW 检测。')

	register_ui_component('image_editor_model_dropdown', IMAGE_EDITOR_MODEL_DROPDOWN)
	register_ui_component('image_editor_install_button', IMAGE_EDITOR_INSTALL_BUTTON)
	register_ui_component('image_editor_steps_slider', IMAGE_EDITOR_STEPS_SLIDER)
	register_ui_component('image_editor_seed_number', IMAGE_EDITOR_SEED_NUMBER)
	register_ui_component('image_editor_status_markdown', IMAGE_EDITOR_STATUS_MARKDOWN)
	register_ui_component('image_editor_info_markdown', IMAGE_EDITOR_INFO_MARKDOWN)
	register_ui_component('image_editor_nsfw_enable_checkbox', IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX)
	register_ui_component('image_editor_nsfw_mode_radio', IMAGE_EDITOR_NSFW_MODE_RADIO)
	register_ui_component('image_editor_nsfw_confirm_checkbox', IMAGE_EDITOR_NSFW_CONFIRM_CHECKBOX)
	register_ui_component('image_editor_nsfw_notice_markdown', IMAGE_EDITOR_NSFW_NOTICE_MARKDOWN)


def listen() -> None:
	if IMAGE_EDITOR_MODEL_DROPDOWN:
		IMAGE_EDITOR_MODEL_DROPDOWN.change(update_model_details, inputs = IMAGE_EDITOR_MODEL_DROPDOWN, outputs = [ IMAGE_EDITOR_STATUS_MARKDOWN, IMAGE_EDITOR_INFO_MARKDOWN ])
	if IMAGE_EDITOR_INSTALL_BUTTON:
		IMAGE_EDITOR_INSTALL_BUTTON.click(install_model, inputs = IMAGE_EDITOR_MODEL_DROPDOWN, outputs = [ IMAGE_EDITOR_STATUS_MARKDOWN, IMAGE_EDITOR_INFO_MARKDOWN ])
	if IMAGE_EDITOR_APPLY_BUTTON:
		IMAGE_EDITOR_APPLY_BUTTON.click(
			apply_image_edit,
			inputs = [
				IMAGE_EDITOR_CANVAS,
				IMAGE_EDITOR_PROMPT_TEXTBOX,
				IMAGE_EDITOR_NEGATIVE_PROMPT_TEXTBOX,
				IMAGE_EDITOR_STRENGTH_SLIDER,
				IMAGE_EDITOR_STEPS_SLIDER,
				IMAGE_EDITOR_SEED_NUMBER,
				IMAGE_EDITOR_MODEL_DROPDOWN,
				IMAGE_EDITOR_MODE_RADIO,
				IMAGE_EDITOR_WIDTH_SLIDER,
				IMAGE_EDITOR_HEIGHT_SLIDER,
				IMAGE_EDITOR_CFG_SLIDER,
				IMAGE_EDITOR_SAMPLER_DROPDOWN,
				IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX,
				IMAGE_EDITOR_NSFW_CONFIRM_CHECKBOX
			],
			outputs = [ IMAGE_EDITOR_OUTPUT_IMAGE, IMAGE_EDITOR_MASK_PREVIEW_IMAGE, IMAGE_EDITOR_LOG_MARKDOWN ]
		)
	if IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX:
		IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX.change(toggle_nsfw_controls, inputs = IMAGE_EDITOR_NSFW_ENABLE_CHECKBOX, outputs = [ IMAGE_EDITOR_NSFW_MODE_RADIO, IMAGE_EDITOR_NSFW_CONFIRM_CHECKBOX, IMAGE_EDITOR_NSFW_NOTICE_MARKDOWN ])


def update_model_details(model_label : str) -> Tuple[gradio.Markdown, gradio.Markdown]:
	model_label = model_label or DEFAULT_MODEL_LABEL
	return gradio.Markdown(value = _format_model_status(model_label)), gradio.Markdown(value = _format_model_info(model_label))


def install_model(model_label : str) -> Tuple[gradio.Markdown, gradio.Markdown]:
	model_label = model_label or DEFAULT_MODEL_LABEL
	model = MODEL_BY_LABEL.get(model_label, MODEL_BY_LABEL.get(DEFAULT_MODEL_LABEL))
	if not model:
		return update_model_details(DEFAULT_MODEL_LABEL)

	# Z-Image GGUF：模型已下载到本地，只需检查拆分文件是否存在
	if model.get('engine') == 'sdcpp':
		if _is_model_installed(model.get('repo_id')):
			return gradio.Markdown(value = _format_model_status(model_label, '已安装')), gradio.Markdown(value = _format_model_info(model_label))
		missing = [p for p in (SDCPP_DIFFUSION_MODEL, SDCPP_VAE, SDCPP_LLM) if not os.path.isfile(p)]
		return gradio.Markdown(value = _format_model_status(model_label, '模型文件未找到')), gradio.Markdown(value = _format_model_info(model_label, f'缺失文件：{", ".join(missing)}'))

	cache_dir = _get_model_cache_dir(model.get('repo_id'))
	create_directory(cache_dir)

	try:
		_setup_huggingface_proxy()
		snapshot_download(repo_id = model.get('repo_id'), local_dir = cache_dir, local_dir_use_symlinks = False)
		return gradio.Markdown(value = _format_model_status(model_label, '已安装')), gradio.Markdown(value = _format_model_info(model_label))
	except Exception as exception:
		return gradio.Markdown(value = _format_model_status(model_label, '安装失败')), gradio.Markdown(value = _format_model_info(model_label, str(exception)))


def apply_image_edit(editor_value : Dict[str, object], prompt : str, negative_prompt : str, strength : float, steps : float, seed : float, model_label : str, edit_mode : str, out_width : float, out_height : float, cfg_scale : float, sampler : str, nsfw_enabled : bool, nsfw_confirmed : bool) -> Tuple[Optional[Image.Image], Optional[Image.Image], gradio.Markdown]:
	import time

	start_time = time.time()
	input_image, mask_image = _extract_editor_image_and_mask(editor_value)
	edit_mode = (edit_mode or '局部重绘（涂抹 mask）').strip()
	is_txt2img = edit_mode.startswith('文生图')
	is_img2img = edit_mode.startswith('图生图')
	is_inpaint = edit_mode.startswith('局部重绘')

	# 文生图无需输入图片；图生图/局部重绘都需要
	if not is_txt2img and input_image is None:
		return None, None, gradio.Markdown(value = '### 运行日志\n请先上传输入图片。')
	if is_inpaint and mask_image is None:
		return ImageOps.exif_transpose(input_image.convert('RGB')) if input_image else None, None, gradio.Markdown(value = '### 运行日志\n未检测到涂抹图层，请用白色画笔覆盖要编辑的区域。')
	if nsfw_enabled and not nsfw_confirmed:
		return None, mask_image, gradio.Markdown(value = '### 运行日志\n请先勾选“我已满 18 岁”。')

	model_label = model_label or DEFAULT_MODEL_LABEL
	model = MODEL_BY_LABEL.get(model_label, MODEL_BY_LABEL.get(DEFAULT_MODEL_LABEL))
	mask_bbox = mask_image.getbbox() if mask_image is not None else None
	resolved_prompt, prompt_note = _resolve_prompt(prompt)
	resolved_negative = (negative_prompt or DEFAULT_NEGATIVE_PROMPT).strip()
	if strength is not None:
		resolved_strength = float(strength)
	elif is_img2img:
		resolved_strength = IMG2IMG_STRENGTH
	elif is_txt2img:
		resolved_strength = 1.0
	else:
		resolved_strength = INPAINT_STRENGTH
	resolved_steps = int(steps or DEFAULT_STEPS)
	resolved_seed = int(seed if seed is not None else DEFAULT_SEED)
	resolved_width = int(out_width or 512)
	resolved_height = int(out_height or 512)
	resolved_cfg = float(cfg_scale or 5.0)
	resolved_sampler = sampler or 'euler_a'
	zimage_label = '默认 · Z-Image Turbo (GGUF)'
	sd15_label = '可选 · SD 1.5 Inpainting'
	zimage_installed = model and _is_model_installed(model.get('repo_id')) and model_label == zimage_label

	if is_txt2img:
		run_mode = '文生图 - Z-Image Turbo (GGUF) / sd.cpp（CUDA）'
		try:
			result_image = _apply_sdcpp_txt2img(resolved_prompt, resolved_negative, resolved_steps, resolved_seed, resolved_width, resolved_height, resolved_cfg, resolved_sampler)
		except Exception as exception:
			run_mode = f'文生图失败，无 fallback：{exception}'
			result_image = None
	elif is_img2img:
		run_mode = '图生图 - Z-Image Turbo (GGUF) / sd.cpp（CUDA）'
		try:
			result_image = _apply_sdcpp(input_image, None, resolved_prompt, resolved_negative, resolved_strength, resolved_steps, resolved_seed, resolved_width, resolved_height, resolved_cfg, resolved_sampler)
		except Exception as exception:
			run_mode = f'图生图失败，回退本地预览：{exception}'
			result_image = _apply_local_preview_edit(input_image, None, resolved_strength)
	elif zimage_installed:
		run_mode = '局部重绘 - Z-Image Turbo (GGUF) / sd.cpp（CUDA）'
		try:
			result_image = _apply_sdcpp(input_image, mask_image, resolved_prompt, resolved_negative, resolved_strength, resolved_steps, resolved_seed, resolved_width, resolved_height, resolved_cfg, resolved_sampler)
		except Exception as exception:
			run_mode = f'Z-Image 失败，回退本地预览：{exception}'
			result_image = _apply_local_preview_edit(input_image, mask_image, resolved_strength)
	elif model and _is_model_installed(model.get('repo_id')) and model_label == sd15_label:
		run_mode = '局部重绘 - SD 1.5 Inpainting / CUDA'
		try:
			result_image = _apply_diffusers_inpaint(input_image, mask_image, resolved_prompt, resolved_negative, resolved_strength, resolved_steps, resolved_seed, model.get('repo_id'))
		except Exception as exception:
			run_mode = f'SD 失败，回退本地预览：{exception}'
			result_image = _apply_local_preview_edit(input_image, mask_image, resolved_strength)
	else:
		run_mode = '本地预览 fallback（未使用生成模型）'
		result_image = _apply_local_preview_edit(input_image, mask_image, resolved_strength)

	# 输出图缩略，避免大图导致滚动卡顿；原图尺寸记录在日志
	display_image = _downscale_for_preview(result_image) if result_image is not None else None

	elapsed = time.time() - start_time
	input_size = input_image.size if input_image is not None else '无（文生图）'
	out_size = f'{resolved_width}x{resolved_height}'
	result_size = result_image.size if result_image is not None else '无'
	log = (
		'### 运行日志\n'
		f'- 执行模式：{run_mode}\n'
		f'- 原图尺寸：{input_size}\n'
		f'- 输出尺寸：{out_size}\n'
		f'- 结果尺寸：{result_size}\n'
		f'- Mask 边界：{mask_bbox}\n'
		f'- 编辑强度：{resolved_strength}\n'
		f'- 推理步数：{resolved_steps}\n'
		f'- CFG：{resolved_cfg}\n'
		f'- 采样方法：{resolved_sampler}\n'
		f'- 随机种子：{resolved_seed}\n'
		f'- 耗时：{elapsed:.2f} 秒\n'
		f'- 提示词：{resolved_prompt}\n'
		f'- 负向提示词：{resolved_negative}\n'
		f'- 提示说明：{prompt_note}\n'
	)
	return display_image, mask_image, gradio.Markdown(value = log)


def toggle_nsfw_controls(enabled : bool) -> Tuple[gradio.Radio, gradio.Checkbox, gradio.Markdown]:
	visible = bool(enabled)
	notice = '已开启 NSFW 检测：首次使用前请确认你已满 18 岁。' if visible else '开启后会在编辑前后执行 NSFW 检测。'
	return gradio.Radio(visible = visible), gradio.Checkbox(visible = visible), gradio.Markdown(value = notice)


def _extract_editor_image_and_mask(editor_value : object) -> Tuple[Optional[Image.Image], Optional[Image.Image]]:
	if isinstance(editor_value, Image.Image):
		return ImageOps.exif_transpose(editor_value.convert('RGB')), None
	if not isinstance(editor_value, dict):
		return None, None

	background = editor_value.get('background')
	layers = editor_value.get('layers') or []
	if not isinstance(background, Image.Image):
		return None, None

	input_image = ImageOps.exif_transpose(background.convert('RGB'))
	mask = Image.new('L', input_image.size, 0)
	for layer in layers:
		if not isinstance(layer, Image.Image):
			continue
		layer = layer.convert('RGBA').resize(input_image.size)
		alpha = layer.getchannel('A')
		mask = Image.composite(Image.new('L', input_image.size, 255), mask, alpha)

	if not mask.getbbox():
		return input_image, None
	return input_image, mask


def _resolve_prompt(prompt : str) -> Tuple[str, str]:
	raw = (prompt or '').strip()
	if not raw:
		return DEFAULT_PROMPT, '空提示词，已使用默认去字/清洁 prompt'
	has_cjk = bool(re.search(r'[\u4e00-\u9fff]', raw))
	if has_cjk:
		# Z-Image Turbo 使用 Qwen3-4B 文本编码器，原生支持中文 prompt
		return raw, '检测到中文提示词，Z-Image（Qwen3-4B）原生支持。'
	return raw, '使用用户提示词（Z-Image 支持中英文）'


def _downscale_for_preview(image : Image.Image) -> Image.Image:
	'''将输出图按长边缩到 OUTPUT_PREVIEW_MAX，避免大图在滚动时反复重绘卡顿。'''
	if image is None:
		return None
	image = ImageOps.exif_transpose(image.convert('RGB'))
	w, h = image.size
	long_side = max(w, h)
	if long_side <= OUTPUT_PREVIEW_MAX:
		return image
	scale = OUTPUT_PREVIEW_MAX / long_side
	return image.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)


def _get_inpaint_pipeline(repo_id : str):
	import torch
	from diffusers import StableDiffusionInpaintPipeline

	cache_key = repo_id
	cached = _INPAINT_PIPELINE_CACHE.get(cache_key)
	if cached is not None:
		return cached

	cache_dir = _get_model_cache_dir(repo_id)
	device = 'cuda' if torch.cuda.is_available() else 'cpu'
	torch_dtype = torch.float16 if device == 'cuda' else torch.float32
	load_kwargs = {
		'torch_dtype': torch_dtype,
		'safety_checker': None,
		'local_files_only': True
	}
	try:
		pipe = StableDiffusionInpaintPipeline.from_pretrained(cache_dir, variant = 'fp16', **load_kwargs)
	except Exception:
		pipe = StableDiffusionInpaintPipeline.from_pretrained(cache_dir, **load_kwargs)
	pipe = pipe.to(device)
	pipe.enable_attention_slicing()
	_INPAINT_PIPELINE_CACHE[cache_key] = pipe
	return pipe


def _apply_diffusers_inpaint(input_image : Image.Image, mask_image : Image.Image, prompt : str, negative_prompt : str, strength : float, steps : int, seed : int, repo_id : str) -> Image.Image:
	try:
		import torch

		pipe = _get_inpaint_pipeline(repo_id)
		device = str(pipe.device)
		original_image = ImageOps.exif_transpose(input_image.convert('RGB'))
		original_mask = _prepare_mask(mask_image, original_image.size)
		dilated = original_mask.filter(ImageFilter.MaxFilter(size = 5))
		canvas_image, canvas_mask, content_box = _prepare_inpaint_canvas(original_image, dilated, 512)
		generator = None
		if seed >= 0:
			generator = torch.Generator(device = device).manual_seed(seed)
		result = pipe(
			prompt = prompt or DEFAULT_PROMPT,
			negative_prompt = negative_prompt or DEFAULT_NEGATIVE_PROMPT,
			image = canvas_image,
			mask_image = canvas_mask,
			strength = max(0.05, min(float(strength or DEFAULT_STRENGTH), 1.0)),
			num_inference_steps = max(4, min(int(steps or DEFAULT_STEPS), 40)),
			guidance_scale = 8.0,
			generator = generator
		).images[0]
		result = result.crop(content_box).resize(original_image.size, Image.Resampling.LANCZOS)
		blend_mask = dilated.filter(ImageFilter.GaussianBlur(radius = 4))
		return Image.composite(result, original_image, blend_mask)
	except Exception as exception:
		raise RuntimeError(f'SD 1.5 inpainting 推理失败：{exception}') from exception


def _apply_sdcpp(input_image : Image.Image, mask_image : Optional[Image.Image], prompt : str, negative_prompt : str, strength : float, steps : int, seed : int, out_width : int = 512, out_height : int = 512, cfg_scale : float = 5.0, sampler : str = 'euler_a') -> Image.Image:
	import subprocess
	import tempfile

	original_image = ImageOps.exif_transpose(input_image.convert('RGB'))
	canvas_w = max(256, int(out_width or 512))
	canvas_h = max(256, int(out_height or 512))
	resolved_cfg = float(cfg_scale or 5.0)
	resolved_sampler = sampler or 'euler_a'
	resolved_strength = max(0.05, min(float(strength or DEFAULT_STRENGTH), 1.0))
	resolved_steps = max(4, min(int(steps or DEFAULT_STEPS), 40))
	resolved_seed = max(0, int(seed if seed is not None else DEFAULT_SEED))

	# 图生图：无 mask，直接用 --init-img，不传 --mask
	if mask_image is None:
		w, h = original_image.size
		scale = min(canvas_w / w, canvas_h / h)
		rw = max(1, int(w * scale))
		rh = max(1, int(h * scale))
		left = (canvas_w - rw) // 2
		top = (canvas_h - rh) // 2
		content_box = (left, top, left + rw, top + rh)
		canvas = Image.new('RGB', (canvas_w, canvas_h), (0, 0, 0))
		canvas.paste(original_image.resize((rw, rh), Image.Resampling.LANCZOS), (left, top))

		with tempfile.TemporaryDirectory() as temp_dir:
			init_path = os.path.join(temp_dir, 'init.png')
			out_path = os.path.join(temp_dir, 'out.png')
			canvas.save(init_path)

			command = [
				SDCPP_BIN,
				'--diffusion-model', SDCPP_DIFFUSION_MODEL,
				'--vae', SDCPP_VAE,
				'--llm', SDCPP_LLM,
				'-p', prompt or DEFAULT_PROMPT,
				'-n', negative_prompt or DEFAULT_NEGATIVE_PROMPT,
				'-i', init_path,
				'--strength', f'{resolved_strength:.2f}',
				'--steps', str(resolved_steps),
				'--cfg-scale', f'{resolved_cfg:.1f}',
				'--seed', str(resolved_seed),
				'--sampling-method', resolved_sampler,
				'--vae-tiling',
				'--max-vram', '6',
				'--diffusion-fa',
				'--backend', 'llm=cpu,vae=cuda0,diffusion=cuda0',
				'-o', out_path
			]
			process = subprocess.run(command, capture_output = True, text = True, timeout = 600)
			if process.returncode != 0 or not os.path.exists(out_path):
				raise RuntimeError(f'sd.cpp 图生图失败（exit {process.returncode}）：{(process.stderr or process.stdout)[-500:]}')

			result = Image.open(out_path).convert('RGB').crop(content_box).resize(original_image.size, Image.Resampling.LANCZOS)
		return result

	# 局部重绘：带 mask
	original_mask = _prepare_mask(mask_image, original_image.size)
	dilated = original_mask.filter(ImageFilter.MaxFilter(size = 5))
	canvas_size = min(canvas_w, canvas_h)
	canvas_image, canvas_mask, content_box = _prepare_inpaint_canvas(original_image, dilated, canvas_size)

	with tempfile.TemporaryDirectory() as temp_dir:
		init_path = os.path.join(temp_dir, 'init.png')
		mask_path = os.path.join(temp_dir, 'mask.png')
		out_path = os.path.join(temp_dir, 'out.png')
		canvas_image.save(init_path)
		canvas_mask.save(mask_path)

		command = [
			SDCPP_BIN,
			'--diffusion-model', SDCPP_DIFFUSION_MODEL,
			'--vae', SDCPP_VAE,
			'--llm', SDCPP_LLM,
			'-p', prompt or DEFAULT_PROMPT,
			'-n', negative_prompt or DEFAULT_NEGATIVE_PROMPT,
			'-i', init_path,
			'--mask', mask_path,
			'--strength', f'{resolved_strength:.2f}',
			'--steps', str(resolved_steps),
			'--cfg-scale', f'{resolved_cfg:.1f}',
			'--seed', str(resolved_seed),
			'--sampling-method', resolved_sampler,
			'--vae-tiling',
			'--max-vram', '6',
			'--diffusion-fa',
			'--backend', 'llm=cpu,vae=cuda0,diffusion=cuda0',
			'-o', out_path
		]
		process = subprocess.run(command, capture_output = True, text = True, timeout = 600)
		if process.returncode != 0 or not os.path.exists(out_path):
			raise RuntimeError(f'sd.cpp 局部重绘失败（exit {process.returncode}）：{(process.stderr or process.stdout)[-500:]}')

		result = Image.open(out_path).convert('RGB').crop(content_box).resize(original_image.size, Image.Resampling.LANCZOS)
	blend_mask = dilated.filter(ImageFilter.GaussianBlur(radius = 4))
	return Image.composite(result, original_image, blend_mask)


def _apply_sdcpp_txt2img(prompt : str, negative_prompt : str, steps : int, seed : int, width : int = 512, height : int = 512, cfg_scale : float = 5.0, sampler : str = 'euler_a') -> Image.Image:
	import subprocess
	import tempfile

	resolved_width = max(256, int(width or 512))
	resolved_height = max(256, int(height or 512))
	resolved_cfg = float(cfg_scale or 5.0)
	resolved_sampler = sampler or 'euler_a'
	resolved_steps = max(4, min(int(steps or DEFAULT_STEPS), 40))
	resolved_seed = max(0, int(seed if seed is not None else DEFAULT_SEED))

	with tempfile.TemporaryDirectory() as temp_dir:
		out_path = os.path.join(temp_dir, 'out.png')
		command = [
			SDCPP_BIN,
			'--diffusion-model', SDCPP_DIFFUSION_MODEL,
			'--vae', SDCPP_VAE,
			'--llm', SDCPP_LLM,
			'-p', prompt or DEFAULT_PROMPT,
			'-n', negative_prompt or DEFAULT_NEGATIVE_PROMPT,
			'--steps', str(resolved_steps),
			'--cfg-scale', f'{resolved_cfg:.1f}',
			'--seed', str(resolved_seed),
			'--sampling-method', resolved_sampler,
			'-W', str(resolved_width),
			'-H', str(resolved_height),
			'--vae-tiling',
			'--max-vram', '6',
			'--diffusion-fa',
			'--backend', 'llm=cpu,vae=cuda0,diffusion=cuda0',
			'-o', out_path
		]
		process = subprocess.run(command, capture_output = True, text = True, timeout = 600)
		if process.returncode != 0 or not os.path.exists(out_path):
			raise RuntimeError(f'sd.cpp 文生图失败（exit {process.returncode}）：{(process.stderr or process.stdout)[-500:]}')
		return Image.open(out_path).convert('RGB')


def _apply_local_preview_edit(input_image : Image.Image, mask_image : Optional[Image.Image], strength : float) -> Image.Image:
	image = ImageOps.exif_transpose(input_image.convert('RGB'))
	strength = max(0.0, min(float(strength or 0.55), 1.0))
	edited = ImageEnhance.Sharpness(image).enhance(1.0 + strength)
	edited = ImageEnhance.Contrast(edited).enhance(1.0 + strength * 0.25)
	if mask_image:
		mask = _prepare_mask(mask_image, image.size).filter(ImageFilter.GaussianBlur(radius = 8))
		return Image.composite(edited, image, mask)
	return edited


def _prepare_mask(mask_image : Image.Image, size : Tuple[int, int]) -> Image.Image:
	mask = ImageOps.exif_transpose(mask_image).convert('L').resize(size)
	mask_array = numpy.array(mask)
	mask_array = numpy.where(mask_array > 32, 255, 0).astype(numpy.uint8)
	return Image.fromarray(mask_array, mode = 'L')


def _prepare_inpaint_canvas(image : Image.Image, mask : Image.Image, canvas_size : int) -> Tuple[Image.Image, Image.Image, Tuple[int, int, int, int]]:
	width, height = image.size
	scale = min(canvas_size / width, canvas_size / height)
	resized_width = max(1, int(width * scale))
	resized_height = max(1, int(height * scale))
	left = (canvas_size - resized_width) // 2
	top = (canvas_size - resized_height) // 2
	content_box = (left, top, left + resized_width, top + resized_height)
	canvas_image = Image.new('RGB', (canvas_size, canvas_size), (0, 0, 0))
	canvas_mask = Image.new('L', (canvas_size, canvas_size), 0)
	canvas_image.paste(image.resize((resized_width, resized_height), Image.Resampling.LANCZOS), (left, top))
	canvas_mask.paste(mask.resize((resized_width, resized_height), Image.Resampling.NEAREST), (left, top))
	return canvas_image, canvas_mask, content_box


def _setup_huggingface_proxy() -> None:
	proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or 'http://127.0.0.1:7887'
	os.environ.setdefault('HTTP_PROXY', proxy_url)
	os.environ.setdefault('HTTPS_PROXY', proxy_url)
	os.environ.setdefault('ALL_PROXY', proxy_url)


def _get_model_cache_dir(repo_id : str) -> str:
	return os.path.abspath(os.path.join('.caches', 'image_editor_models', repo_id.replace('/', '__')))


def _is_model_installed(repo_id : str) -> bool:
	model = MODEL_BY_REPO.get(repo_id)
	if model and model.get('engine') == 'sdcpp':
		return os.path.isfile(SDCPP_DIFFUSION_MODEL) and os.path.isfile(SDCPP_VAE) and os.path.isfile(SDCPP_LLM)
	cache_dir = _get_model_cache_dir(repo_id)
	return is_directory(cache_dir) and any(os.scandir(cache_dir))


def _format_model_status(model_label : str, override_status : Optional[str] = None) -> str:
	model = MODEL_BY_LABEL.get(model_label, MODEL_BY_LABEL.get(DEFAULT_MODEL_LABEL))
	if not model:
		return '### 模型状态\n未找到默认模型配置。'
	installed_status = '已安装' if _is_model_installed(model.get('repo_id')) else '未安装'
	status_text = override_status or installed_status
	if model.get('engine') == 'sdcpp':
		cache_dir = SDCPP_DIFFUSION_MODEL
	else:
		cache_dir = _get_model_cache_dir(model.get('repo_id'))
	return f'### 模型状态\n- 当前选择：**{model.get("label")}**\n- 安装状态：**{status_text}**\n- 缓存目录：`{cache_dir}`\n'


def _format_model_info(model_label : str, extra_message : Optional[str] = None) -> str:
	model = MODEL_BY_LABEL.get(model_label, MODEL_BY_LABEL.get(DEFAULT_MODEL_LABEL))
	if not model:
		return '### 模型说明\n暂无可用模型。'
	message_line = f'- 备注：{extra_message}' if extra_message else f'- 备注：{model.get("notes")}'
	return f'### 模型说明\n- 用途：{model.get("usage")}\n- 轻重：{model.get("size_hint")}\n{message_line}\n'