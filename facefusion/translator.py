import importlib
import os
from typing import Dict, List, Optional, Tuple, Union

from facefusion.types import Language, LocalePoolSet, Locales

LOCALE_POOL_SET : LocalePoolSet = {}
CURRENT_LANGUAGE : Language = os.environ.get('FACEFUSION_LANGUAGE', 'en')


def __autoload__(module_name : str) -> None:
	try:
		__locales__ = importlib.import_module(module_name + '.locales')
		load(__locales__.LOCALES, module_name)
	except ImportError:
		pass


def load(__locales__ : Locales, module_name : str) -> None:
	LOCALE_POOL_SET[module_name] = __locales__


def get(notation : str, module_name : str = 'facefusion') -> Optional[str]:
	if module_name not in LOCALE_POOL_SET:
		__autoload__(module_name)

	current = LOCALE_POOL_SET.get(module_name).get(CURRENT_LANGUAGE)

	for fragment in notation.split('.'):
		if fragment in current:
			current = current.get(fragment)

			if isinstance(current, str):
				return current

	return None


def _build_choice_mapping(module_name : str = 'facefusion') -> Dict[str, str]:
	"""Build the English -> localized label mapping for choices"""
	if module_name not in LOCALE_POOL_SET:
		__autoload__(module_name)

	if CURRENT_LANGUAGE == 'en':
		return {}

	locales = LOCALE_POOL_SET.get(module_name, {})
	return dict(locales.get(CURRENT_LANGUAGE, {}).get('choices', {}))


def _format_choice_token(token : str) -> str:
	token_map =\
	{
		'amf': 'AMF',
		'ben': 'BEN',
		'bfr': 'BFR',
		'ddcolor': 'DDColor',
		'deoldify': 'DeOldify',
		'edtalk': 'EDTalk',
		'esrgan': 'ESRGAN',
		'fp16': 'FP16',
		'fran': 'FRAN',
		'gan': 'GAN',
		'gfpgan': 'GFPGAN',
		'gpen': 'GPEN',
		'hatgan': 'HATGAN',
		'hififace': 'HiFiFace',
		'inswapper': 'InSwapper',
		'isnet': 'ISNet',
		'lsdir': 'LSDIR',
		'modnet': 'MODNet',
		'nomos8k': 'Nomos8K',
		'ormbg': 'ORMBG',
		'qsv': 'QSV',
		'remacri': 'Remacri',
		'rmbg': 'RMBG',
		'sc': 'SC',
		'siax': 'Siax',
		'silueta': 'Silueta',
		'simswap': 'SimSwap',
		'span': 'SPAN',
		'sr': 'SR',
		'styleganex': 'StyleGANEX',
		'swin2': 'Swin2',
		'tghq': 'TGHQ',
		'u2net': 'U2Net',
		'u2netp': 'U2NetP',
		'ultra': 'Ultra',
		'uniface': 'UniFace',
		'unofficial': '非官方',
		'uvr': 'UVR',
		'videotoolbox': 'VideoToolbox',
		'wav2lip': 'Wav2Lip',
		'xseg': 'XSeg'
	}

	if token in token_map:
		return token_map.get(token)
	if token.startswith('x') and token[1:].isdigit():
		return token
	if token.isdigit():
		return token
	if token.replace('.', '').isdigit():
		return token
	if any(character.isdigit() for character in token):
		return token.upper()
	return token.capitalize()


def _format_choice_label(choice : str) -> str:
	if CURRENT_LANGUAGE != 'zh' or not choice:
		return choice
	if '/' in choice:
		choice_prefix, choice_suffix = choice.split('/', 1)
		return _format_choice_token(choice_prefix) + ' / ' + _format_choice_label(choice_suffix)

	choice_tokens = choice.split('_')

	if len(choice_tokens) > 1 and choice_tokens[-1].isdigit():
		return ' '.join(_format_choice_token(token) for token in choice_tokens[:-1]) + ' (' + choice_tokens[-1] + ')'
	return ' '.join(_format_choice_token(token) for token in choice_tokens)


def translate_label(choice : str, module_name : str = 'facefusion') -> str:
	"""Return the localized display label for an English choice value"""
	if CURRENT_LANGUAGE == 'en' or not choice:
		return choice

	choice_mapping = _build_choice_mapping(module_name)
	return choice_mapping.get(choice) or _format_choice_label(choice)


def translate_choice(choice : str, module_name : str = 'facefusion') -> str:
	"""Pass the choice value through unchanged.

	With native Gradio (label, value) choices the stored value always stays in
	English, so single-select `value=` arguments no longer need translation.
	"""
	return choice


def untranslate_choice(choice : str, module_name : str = 'facefusion') -> str:
	"""Pass the choice value through unchanged.

	Gradio now returns the English value directly from (label, value) choices,
	so no reverse lookup is required.
	"""
	return choice


def translate_choices(choices : Union[List[str], tuple], module_name : str = 'facefusion') -> List[Union[str, Tuple[str, str]]]:
	"""Build native Gradio choices as (localized_label, english_value) tuples.

	Gradio displays the label but keeps the value in English, eliminating the
	need to translate values back and forth.
	"""
	if CURRENT_LANGUAGE == 'en':
		return list(choices)

	return [ (translate_label(choice, module_name), choice) for choice in choices ]


def untranslate_choices(choices : Union[List[str], tuple], module_name : str = 'facefusion') -> List[str]:
	"""Pass choice values through unchanged (already English from Gradio)"""
	return list(choices)


def set_language(language : Language) -> None:
	global CURRENT_LANGUAGE
	CURRENT_LANGUAGE = language


def get_language() -> Language:
	return CURRENT_LANGUAGE
