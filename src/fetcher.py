"""
数据获取模块
负责从 curl wiki 获取 DoH 服务器列表
"""

import requests
from typing import Optional
from .config import CURL_WIKI_URL, REQUEST_TIMEOUT


class WikiFetcher:
    """Wiki 内容获取器"""
    
    def __init__(self):
        self.url = CURL_WIKI_URL
        self.timeout = REQUEST_TIMEOUT
    
    def fetch(self) -> Optional[str]:
        """
        获取 curl wiki 内容
        
        Returns:
            str: wiki 内容，失败返回 None
        """
        try:
            print(f"📥 正在获取 curl wiki: {self.url}")
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            
            content = response.text
            print(f"✓ 成功获取内容 ({len(content)} 字符)")
            return content
            
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时 ({self.timeout}秒)")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None
        
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return None