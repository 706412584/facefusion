#!/usr/bin/env python3
"""
自动检测和配置代理
支持 HTTP/HTTPS/SOCKS5 代理
"""

import os
import socket
import urllib.request
from typing import Optional, Tuple


def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def detect_proxy() -> Optional[Tuple[str, int]]:
    """自动检测代理"""
    # 1. 检查环境变量
    for env_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy']:
        proxy = os.environ.get(env_var)
        if proxy:
            return parse_proxy_url(proxy)
    
    # 2. 检查常见代理端口
    common_ports = [7890, 7891, 7892, 7887, 1080, 10808, 10809, 8080, 8118]
    
    for port in common_ports:
        if check_port('127.0.0.1', port):
            return ('127.0.0.1', port)
    
    return None


def parse_proxy_url(proxy_url: str) -> Optional[Tuple[str, int]]:
    """解析代理 URL"""
    try:
        # 移除协议前缀
        for prefix in ['http://', 'https://', 'socks5://', 'socks5h://']:
            if proxy_url.startswith(prefix):
                proxy_url = proxy_url[len(prefix):]
        
        # 解析主机和端口
        if ':' in proxy_url:
            host, port = proxy_url.split(':')
            return (host, int(port))
        
        return None
    except:
        return None


def setup_proxy(host: str = None, port: int = None) -> bool:
    """设置代理"""
    if host is None or port is None:
        proxy_info = detect_proxy()
        if proxy_info:
            host, port = proxy_info
        else:
            return False
    
    proxy_url = f"http://{host}:{port}"
    
    # 设置环境变量
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    
    print(f"\n✓ 代理已设置: {proxy_url}")
    
    # 测试代理
    if test_proxy(proxy_url):
        print("✓ 代理测试成功")
        return True
    else:
        print("✗ 代理测试失败")
        return False


def test_proxy(proxy_url: str, timeout: float = 5.0) -> bool:
    """测试代理连接"""
    try:
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy_url,
            'https': proxy_url
        })
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        
        # 测试连接到 Google
        response = opener.open('http://www.google.com', timeout=timeout)
        return response.status == 200
    except:
        return False


def clear_proxy():
    """清除代理设置"""
    for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
        if var in os.environ:
            del os.environ[var]
    print("✓ 代理设置已清除")


def get_proxy_info() -> dict:
    """获取当前代理信息"""
    return {
        'HTTP_PROXY': os.environ.get('HTTP_PROXY'),
        'HTTPS_PROXY': os.environ.get('HTTPS_PROXY'),
        'http_proxy': os.environ.get('http_proxy'),
        'https_proxy': os.environ.get('https_proxy'),
    }


def main():
    """主函数"""
    print("=" * 60)
    print("FaceFusion 代理检测和配置工具")
    print("=" * 60)
    
    # 检测并设置代理
    if setup_proxy():
        print("\n当前代理配置:")
        for key, value in get_proxy_info().items():
            if value:
                print(f"  {key}: {value}")
    else:
        print("\n未配置代理，将使用直连")


if __name__ == '__main__':
    main()
