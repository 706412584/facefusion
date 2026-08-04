import itertools
import os
import shutil
from typing import List

from facefusion import metadata
from facefusion.types import Command


def run(commands : List[Command]) -> List[Command]:
	user_agent = metadata.get('name') + '/' + metadata.get('version')
	base_commands = [ shutil.which('curl'), '--user-agent', user_agent, '--location', '--silent', '--ssl-no-revoke' ]
	
	# 自动添加代理支持
	proxy = get_proxy()
	if proxy:
		base_commands.extend(['--proxy', proxy])
	
	return base_commands + commands


def get_proxy() -> str:
	"""获取代理设置"""
	# 检查环境变量
	for env_var in ['HTTPS_PROXY', 'HTTP_PROXY', 'https_proxy', 'http_proxy']:
		proxy = os.environ.get(env_var)
		if proxy:
			return proxy
	return None


def chain(*commands : List[Command]) -> List[Command]:
	return list(itertools.chain(*commands))


def ping(url : str) -> List[Command]:
	return [ '-I', url ]


def download(url : str, download_file_path : str) -> List[Command]:
	return [ '--create-dirs', '--continue-at', '-', '--output', download_file_path, url ]


def set_timeout(timeout : int) -> List[Command]:
	return [ '--connect-timeout', str(timeout) ]


def set_retry(retry : int) -> List[Command]:
	return [ '--retry', str(retry) ]
