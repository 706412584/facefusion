"""按帧 / 时段参数覆盖（预览与播放优先；进程内会话）。

优先级：单帧例外 > 时段覆盖（后写优先）> 全局 state_manager。
通过 contextvars 注入，禁止在多线程里 per-frame set_item。
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from typing import Any, Dict, Generator, List, Literal, Optional, TypedDict
from uuid import uuid4

OVERRIDE_PARAM_KEYS = (
	'face_detector_angles',
	'face_detector_score',
	'face_landmarker_score',
	'reference_face_distance',
	'face_mask_types',
	'face_mask_blur'
)

ActionName = Literal['normal', 'skip_swap', 'skip_process']
SourceName = Literal['frame', 'range', 'global']
ScopeName = Literal['global', 'frame', 'range']
PresetName = Literal['no_swap', 'distortion', 'double', 'edge']

PRESET_PARAMS : Dict[PresetName, Dict[str, Any]] =\
{
	'no_swap':
	{
		'face_detector_angles': [ 0, 90, 180, 270 ],
		'face_detector_score': 0.3,
		'reference_face_distance': 0.6
	},
	'distortion':
	{
		'face_landmarker_score': 0.5,
		'face_detector_score': 0.5,
		'face_detector_angles': [ 0, 90, 180, 270 ],
		'face_mask_types_add': 'occlusion'
	},
	'double':
	{
		'face_detector_angles': [ 0 ],
		'face_detector_score': 0.6,
		'face_landmarker_score': 0.5
	},
	'edge':
	{
		'face_mask_types': [ 'box', 'occlusion' ],
		'face_mask_blur': 0.5
	}
}


class FrameRule(TypedDict, total = False):
	id: str
	frame: int
	action: ActionName
	preset: Optional[str]
	params: Dict[str, Any]
	label: str
	enabled: bool


class RangeRule(TypedDict, total = False):
	id: str
	start_frame: int
	end_frame: int
	action: ActionName
	preset: Optional[str]
	params: Dict[str, Any]
	label: str
	enabled: bool


class ResolvedSettings(TypedDict):
	action: ActionName
	source: SourceName
	rule_id: Optional[str]
	params: Dict[str, Any]
	label: str


_FRAME_RULES : Dict[int, FrameRule] = {}
_RANGE_RULES : List[RangeRule] = []
_CONTEXT : ContextVar[Optional[ResolvedSettings]] = ContextVar('frame_override_context', default = None)


def is_override_param_key(key : str) -> bool:
	return key in OVERRIDE_PARAM_KEYS


def get_context_override() -> Optional[ResolvedSettings]:
	return _CONTEXT.get()


def get_override_item(key : str) -> Any:
	resolved = _CONTEXT.get()
	if not resolved:
		return None
	if key not in OVERRIDE_PARAM_KEYS:
		return None
	params = resolved.get('params') or {}
	if key not in params:
		return None
	return deepcopy(params[key])


def get_context_action() -> ActionName:
	resolved = _CONTEXT.get()
	if not resolved:
		return 'normal'
	return resolved.get('action') or 'normal'


def clear_all() -> None:
	_FRAME_RULES.clear()
	_RANGE_RULES.clear()


def list_rules() -> List[Dict[str, Any]]:
	rows : List[Dict[str, Any]] = []
	for frame_number, rule in sorted(_FRAME_RULES.items()):
		if not rule.get('enabled', True):
			continue
		rows.append(
		{
			'id': rule.get('id'),
			'type': '单帧',
			'range': str(frame_number),
			'action': rule.get('action') or 'normal',
			'summary': _summarize_rule(rule),
			'label': rule.get('label') or ''
		})
	for rule in _RANGE_RULES:
		if not rule.get('enabled', True):
			continue
		rows.append(
		{
			'id': rule.get('id'),
			'type': '时段',
			'range': f"{rule.get('start_frame')}-{rule.get('end_frame')}",
			'action': rule.get('action') or 'normal',
			'summary': _summarize_rule(rule),
			'label': rule.get('label') or ''
		})
	return rows


def remove_rule(rule_id : str) -> bool:
	for frame_number, rule in list(_FRAME_RULES.items()):
		if rule.get('id') == rule_id:
			del _FRAME_RULES[frame_number]
			return True
	for index, rule in enumerate(list(_RANGE_RULES)):
		if rule.get('id') == rule_id:
			_RANGE_RULES.pop(index)
			return True
	return False


def remove_frame_rule(frame_number : int) -> bool:
	if frame_number in _FRAME_RULES:
		del _FRAME_RULES[frame_number]
		return True
	return False


def add_frame_rule(frame_number : int, action : ActionName = 'normal', preset : Optional[str] = None, params : Optional[Dict[str, Any]] = None, label : str = '') -> FrameRule:
	frame_number = int(frame_number)
	clean_params = _sanitize_params(params or {})
	if preset:
		clean_params = _merge_preset_params(preset, clean_params)
	rule : FrameRule =\
	{
		'id': uuid4().hex[:8],
		'frame': frame_number,
		'action': action,
		'preset': preset,
		'params': clean_params,
		'label': label or (preset or action),
		'enabled': True
	}
	_FRAME_RULES[frame_number] = rule
	return rule


def add_range_rule(start_frame : int, end_frame : int, action : ActionName = 'normal', preset : Optional[str] = None, params : Optional[Dict[str, Any]] = None, label : str = '') -> RangeRule:
	start_frame = int(start_frame)
	end_frame = int(end_frame)
	if end_frame < start_frame:
		start_frame, end_frame = end_frame, start_frame
	clean_params = _sanitize_params(params or {})
	if preset:
		clean_params = _merge_preset_params(preset, clean_params)
	rule : RangeRule =\
	{
		'id': uuid4().hex[:8],
		'start_frame': start_frame,
		'end_frame': end_frame,
		'action': action,
		'preset': preset,
		'params': clean_params,
		'label': label or (preset or action),
		'enabled': True
	}
	_RANGE_RULES.append(rule)
	return rule


def resolve_frame_settings(frame_number : int) -> ResolvedSettings:
	frame_number = int(frame_number)
	frame_rule = _FRAME_RULES.get(frame_number)
	if frame_rule and frame_rule.get('enabled', True):
		return\
		{
			'action': frame_rule.get('action') or 'normal',
			'source': 'frame',
			'rule_id': frame_rule.get('id'),
			'params': deepcopy(frame_rule.get('params') or {}),
			'label': frame_rule.get('label') or ''
		}

	matched : Optional[RangeRule] = None
	for rule in _RANGE_RULES:
		if not rule.get('enabled', True):
			continue
		if rule['start_frame'] <= frame_number <= rule['end_frame']:
			matched = rule
	if matched:
		return\
		{
			'action': matched.get('action') or 'normal',
			'source': 'range',
			'rule_id': matched.get('id'),
			'params': deepcopy(matched.get('params') or {}),
			'label': matched.get('label') or ''
		}

	return\
	{
		'action': 'normal',
		'source': 'global',
		'rule_id': None,
		'params': {},
		'label': ''
	}


def format_effective_source(frame_number : int) -> str:
	resolved = resolve_frame_settings(frame_number)
	source = resolved['source']
	action = resolved['action']
	rule_id = resolved.get('rule_id') or '-'
	label = resolved.get('label') or ''
	params = resolved.get('params') or {}
	source_text =\
	{
		'frame': '单帧',
		'range': '时段',
		'global': '全局'
	}.get(source, source)
	param_bits = []
	for key, value in params.items():
		param_bits.append(f'{key}={value}')
	param_text = ', '.join(param_bits) if param_bits else '无参数覆盖'
	action_text = action if action != 'normal' else 'normal'
	extra = f' · {label}' if label else ''
	return f'当前帧 {int(frame_number)} 生效：来源={source_text} · 规则={rule_id}{extra} · action={action_text} · {param_text}'


def format_rules_markdown() -> str:
	rows = list_rules()
	if not rows:
		return '_暂无帧/时段补丁（仅全局参数）_'
	lines = [ '| id | 类型 | 范围 | action | 摘要 |', '|---|---|---|---|---|' ]
	for row in rows:
		lines.append(f"| `{row['id']}` | {row['type']} | {row['range']} | {row['action']} | {row['summary']} |")
	return '\n'.join(lines)


@contextmanager
def apply_context(frame_number : int) -> Generator[ResolvedSettings, None, None]:
	resolved = resolve_frame_settings(frame_number)
	token = _CONTEXT.set(resolved)
	try:
		yield resolved
	finally:
		_CONTEXT.reset(token)


def build_preset_params(preset_name : str, current_mask_types : Optional[List[str]] = None) -> Dict[str, Any]:
	raw = deepcopy(PRESET_PARAMS.get(preset_name, {})) #type:ignore[arg-type]
	add_mask = raw.pop('face_mask_types_add', None)
	params = _sanitize_params(raw)
	if add_mask:
		mask_types = list(current_mask_types or [])
		if add_mask not in mask_types:
			mask_types.append(add_mask)
		params['face_mask_types'] = mask_types
	return params


def _merge_preset_params(preset_name : str, base : Dict[str, Any]) -> Dict[str, Any]:
	merged = build_preset_params(preset_name, current_mask_types = base.get('face_mask_types'))
	merged.update(base)
	return _sanitize_params(merged)


def _sanitize_params(params : Dict[str, Any]) -> Dict[str, Any]:
	clean : Dict[str, Any] = {}
	for key, value in params.items():
		if key in OVERRIDE_PARAM_KEYS:
			clean[key] = deepcopy(value)
	return clean


def _summarize_rule(rule : Dict[str, Any]) -> str:
	action = rule.get('action') or 'normal'
	preset = rule.get('preset') or ''
	params = rule.get('params') or {}
	bits = []
	if preset:
		bits.append(f'preset={preset}')
	if action != 'normal':
		bits.append(f'action={action}')
	for key in OVERRIDE_PARAM_KEYS:
		if key in params:
			bits.append(f'{key}={params[key]}')
	return '; '.join(bits) if bits else '-'
