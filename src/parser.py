"""
DoH 表格解析模块
负责从 Markdown 表格中提取 DoH 服务器信息
"""

import re
from typing import Dict, List
from urllib.parse import urlparse


class DoHTableParser:
    """DoH 服务器表格解析器"""
    
    def __init__(self, content: str):
        self.content = content
        self.provider_urls = {}
    
    def parse(self) -> Dict[str, List[str]]:
        """
        解析 DoH 服务器表格
        
        表格格式:
        | Who runs it | Base URL | Working*| Comment** |
        
        Returns:
            Dict[str, List[str]]: {提供商名称: [DoH URLs]}
        """
        print("\n📋 开始解析 DoH 表格...")
        
        lines = self.content.split('\n')
        current_provider = None
        in_table = False
        
        for line in lines:
            # 检测表格开始
            if '| Who runs it | Base URL |' in line:
                in_table = True
                continue
            
            # 检测表格结束
            if in_table and (not line.strip() or line.startswith('#')):
                in_table = False
                continue
            
            # 跳过表头分隔线
            if in_table and '|---' in line:
                continue
            
            # 解析表格行
            if in_table and line.strip().startswith('|'):
                self._parse_table_row(line, current_provider)
                
                # 更新当前提供商
                provider = self._extract_provider_name(line)
                if provider:
                    current_provider = provider
        
        total_providers = len(self.provider_urls)
        total_urls = sum(len(urls) for urls in self.provider_urls.values())
        
        print(f"✓ 解析完成: {total_providers} 个提供商, {total_urls} 个 DoH URL")
        
        return self.provider_urls
    
    def _parse_table_row(self, line: str, current_provider: str):
        """解析单行表格"""
        columns = [col.strip() for col in line.split('|')]
        
        if len(columns) < 4:
            return
        
        base_url_col = columns[2]  # Base URL 列
        
        # 提取 DoH URLs
        if base_url_col.strip() and current_provider:
            urls = self._extract_doh_urls(base_url_col)
            
            if urls:
                if current_provider not in self.provider_urls:
                    self.provider_urls[current_provider] = []
                
                self.provider_urls[current_provider].extend(urls)
    
    def _extract_provider_name(self, line: str) -> str:
        """从表格行中提取提供商名称"""
        columns = [col.strip() for col in line.split('|')]
        
        if len(columns) < 2:
            return None
        
        who_runs_it = columns[1]
        
        # 跳过分类行（如 **A**, **B**）
        if who_runs_it.strip().startswith('**') and len(who_runs_it.strip()) <= 5:
            return None
        
        if not who_runs_it.strip():
            return None
        
        # 提取提供商名称（去除 Markdown 链接）
        provider_match = re.search(r'\[([^\]]+)\]', who_runs_it)
        if provider_match:
            return provider_match.group(1).strip()
        else:
            return who_runs_it.strip()
    
    def _extract_doh_urls(self, text: str) -> List[str]:
        """从文本中提取 DoH URLs"""
        # 查找所有 https:// 开头的 URL
        urls = re.findall(r'https://[^\s<>|)]+', text)
        
        valid_urls = []
        for url in urls:
            # 清理 URL
            url = url.rstrip(')')
            
            # 确保是 DoH URL（包含常见的 DoH 路径）
            if self._is_doh_url(url):
                valid_urls.append(url)
        
        return valid_urls
    
    def _is_doh_url(self, url: str) -> bool:
        """判断是否为有效的 DoH URL"""
        doh_patterns = [
            '/dns-query',
            '/dns',
            '/doh',
            '/query',
            'dns.',
            'doh.',
        ]
        
        return any(pattern in url.lower() for pattern in doh_patterns)
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """从 URL 提取域名"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None