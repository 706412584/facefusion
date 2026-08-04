import json
import threading
from typing import List, Optional

from facefusion.hash_helper import create_hash
from facefusion.types import Face, FaceStore, VisionFrame
from facefusion.vision import is_vision_frame

FACE_STORE : FaceStore = {}

# 影响 get_many_faces / 缓存有效性的检测相关参数（含 override 白名单中的检测键）
_FACE_CACHE_PARAM_KEYS = (
	'face_detector_model',
	'face_detector_size',
	'face_detector_margin',
	'face_detector_angles',
	'face_detector_score',
	'face_landmarker_model',
	'face_landmarker_score'
)


def _build_param_fingerprint() -> str:
	try:
		from facefusion import state_manager

		payload = {}
		for key in _FACE_CACHE_PARAM_KEYS:
			value = state_manager.get_item(key)
			if isinstance(value, tuple):
				value = list(value)
			payload[key] = value
		return json.dumps(payload, sort_keys = True, default = str)
	except Exception:
		return ''


def create_vision_hash(vision_frame : VisionFrame) -> Optional[str]:
	if not is_vision_frame(vision_frame):
		return None
	frame_hash = create_hash(vision_frame.tobytes())
	param_hash = create_hash(_build_param_fingerprint().encode('utf-8'))
	return frame_hash + ':' + param_hash


def get_faces(vision_frame : VisionFrame) -> Optional[List[Face]]:
	vision_hash = create_vision_hash(vision_frame)
	if vision_hash and FACE_STORE.get(vision_hash):
		return FACE_STORE.get(vision_hash).get('faces')
	return None


def set_faces(vision_frame : VisionFrame, faces : List[Face]) -> None:
	vision_hash = create_vision_hash(vision_frame)
	if vision_hash:
		FACE_STORE.setdefault(vision_hash,
		{
			'lock': threading.Lock()
		})['faces'] = faces


def resolve_lock(vision_frame : VisionFrame) -> threading.Lock:
	vision_hash = create_vision_hash(vision_frame)
	if vision_hash:
		return FACE_STORE.setdefault(vision_hash,
		{
			'lock': threading.Lock()
		}).get('lock')
	return threading.Lock()


def clear_faces() -> None:
	FACE_STORE.clear()
