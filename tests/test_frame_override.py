import concurrent.futures

import pytest

from facefusion import frame_override, state_manager
from facefusion.state_manager import STATE_SET


@pytest.fixture(scope = 'function', autouse = True)
def before_each() -> None:
	frame_override.clear_all()
	STATE_SET['cli'] = {} #type:ignore[typeddict-item]
	STATE_SET['ui'] = {} #type:ignore[typeddict-item]
	state_manager.init_item('face_detector_score', 0.5)
	state_manager.init_item('face_detector_angles', [ 0 ])
	state_manager.init_item('reference_face_distance', 0.3)


def test_priority_frame_over_range_over_global() -> None:
	frame_override.add_range_rule(10, 20, preset = 'double')
	frame_override.add_frame_rule(15, preset = 'no_swap')

	resolved_frame = frame_override.resolve_frame_settings(15)
	resolved_range = frame_override.resolve_frame_settings(12)
	resolved_global = frame_override.resolve_frame_settings(5)

	assert resolved_frame['source'] == 'frame'
	assert resolved_frame['params']['face_detector_score'] == 0.3
	assert resolved_range['source'] == 'range'
	assert resolved_range['params']['face_detector_score'] == 0.6
	assert resolved_global['source'] == 'global'
	assert resolved_global['params'] == {}


def test_later_range_overrides_earlier() -> None:
	frame_override.add_range_rule(0, 100, preset = 'double')
	frame_override.add_range_rule(0, 100, preset = 'no_swap')
	resolved = frame_override.resolve_frame_settings(50)
	assert resolved['source'] == 'range'
	assert resolved['params']['face_detector_score'] == 0.3


def test_get_item_reads_context_whitelist_only() -> None:
	frame_override.add_frame_rule(7, params = { 'face_detector_score': 0.11, 'video_memory_strategy': 'strict' })
	assert state_manager.get_item('face_detector_score') == 0.5
	with frame_override.apply_context(7):
		assert state_manager.get_item('face_detector_score') == 0.11
		# 非白名单 key 即使误塞进 params 也不会经 get_override_item 生效
		assert frame_override.get_override_item('video_memory_strategy') is None
	assert state_manager.get_item('face_detector_score') == 0.5


def test_context_action_skip() -> None:
	frame_override.add_frame_rule(3, action = 'skip_process')
	with frame_override.apply_context(3) as resolved:
		assert resolved['action'] == 'skip_process'
		assert frame_override.get_context_action() == 'skip_process'
	assert frame_override.get_context_action() == 'normal'


def test_context_isolation_across_threads() -> None:
	frame_override.add_frame_rule(1, params = { 'face_detector_score': 0.1 })
	frame_override.add_frame_rule(2, params = { 'face_detector_score': 0.9 })

	def read_score(frame_number : int) -> float:
		with frame_override.apply_context(frame_number):
			return float(state_manager.get_item('face_detector_score'))

	with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as executor:
		future_a = executor.submit(read_score, 1)
		future_b = executor.submit(read_score, 2)
		assert future_a.result() == 0.1
		assert future_b.result() == 0.9


def test_remove_and_clear() -> None:
	rule = frame_override.add_frame_rule(9, action = 'skip_swap')
	assert frame_override.resolve_frame_settings(9)['source'] == 'frame'
	assert frame_override.remove_rule(rule['id']) is True
	assert frame_override.resolve_frame_settings(9)['source'] == 'global'
	frame_override.add_range_rule(1, 2, preset = 'edge')
	frame_override.clear_all()
	assert frame_override.list_rules() == []
