"""
GeoIP 分类模块
使用 GeoIP 查询判断 DoH 服务器是否位于中国
"""

import socket
import requests
import time
from typing import Dict, List, Tuple, Optional
from .config import (
    GEOIP_PROVIDER, GEOIP_APIS, CHINA_REGIONS, 
    CHINA_THRESHOLD, MAX_URLS_PER_PROVIDER,
    ENABLE_GEOIP, GEOIP_RETRY, REQUEST_DELAY, VERBOSE
)
from .parser import DoHTableParser


class GeoIPClassifier:
    """基于 GeoIP 的 DoH 提供商分类器"""
    
    def __init__(self):
        self.geoip_config = GEOIP_APIS.get(GEOIP_PROVIDER)
        if not self.geoip_config:
            raise ValueError(f"未知的 GeoIP 提供商: {GEOIP_PROVIDER}")
        
        self.cache = {}  # 缓存 GeoIP 查询结果
        self.china_providers = {}
        self.foreign_providers = {}
        self.classification_reasons = {}
    
    def classify(self, provider_urls: Dict[str, List[str]]) -> Tuple[Dict, Dict, Dict]:
        """
        分类 DoH 提供商
        
        Args:
            provider_urls: {提供商名称: [DoH URLs]}
        
        Returns:
            (china_providers, foreign_providers, reasons)
        """
        if not ENABLE_GEOIP:
            print("\n⚠️  GeoIP 查询已禁用，所有提供商将被归类为境外")
            return {}, provider_urls, {}
        
        print(f"\n🌍 开始 GeoIP 分类 (使用 {GEOIP_PROVIDER})...")
        print(f"   速率限制: {self.geoip_config['rate_limit']} 请求/分钟")
        print(f"   中国地区: {', '.join(CHINA_REGIONS)}")
        print(f"   判定阈值: {CHINA_THRESHOLD * 100}%\n")
        
        total = len(provider_urls)
        
        for idx, (provider, urls) in enumerate(provider_urls.items(), 1):
            print(f"  [{idx}/{total}] 正在分类: {provider}...", end=' ')
            
            is_china, reason = self._classify_provider(provider, urls)
            self.classification_reasons[provider] = reason
            
            if is_china:
                self.china_providers[provider] = urls
                print(f"🇨🇳 中国")
            else:
                self.foreign_providers[provider] = urls
                print(f"🌍 境外")
            
            if VERBOSE:
                print(f"      {reason}")
            
            # 速率限制
            time.sleep(REQUEST_DELAY)
        
        china_count = len(self.china_providers)
        foreign_count = len(self.foreign_providers)
        
        print(f"\n✓ 分类完成:")
        print(f"  中国 DoH: {china_count} 个提供商")
        print(f"  境外 DoH: {foreign_count} 个提供商")
        
        return self.china_providers, self.foreign_providers, self.classification_reasons
    
    def _classify_provider(self, provider: str, urls: List[str]) -> Tuple[bool, str]:
        """分类单个提供商"""
        # 检查的 URL 数量限制
        check_urls = urls[:MAX_URLS_PER_PROVIDER]
        
        china_count = 0
        total_checked = 0
        details = []
        
        for url in check_urls:
            domain = DoHTableParser.extract_domain(url)
            if not domain:
                continue
            
            country = self._query_geoip(domain)
            
            if country:
                total_checked += 1
                if country in CHINA_REGIONS:
                    china_count += 1
                    details.append(f"{domain}→{country}")
        
        # 判定逻辑
        if total_checked == 0:
            return False, "GeoIP 查询失败"
        
        ratio = china_count / total_checked
        
        if ratio >= CHINA_THRESHOLD:
            reason = f"GeoIP: {china_count}/{total_checked} 在中国地区 ({', '.join(details)})"
            return True, reason
        else:
            reason = f"GeoIP: {china_count}/{total_checked} 在中国地区 (比例 {ratio:.0%} < {CHINA_THRESHOLD:.0%})"
            return False, reason
    
    def _query_geoip(self, domain: str) -> Optional[str]:
        """
        查询域名的国家代码
        
        Returns:
            str: 国家代码 (如 'CN', 'US')，失败返回 None
        """
        # 检查缓存
        if domain in self.cache:
            return self.cache[domain]
        
        # 解析域名到 IP
        try:
            ip = socket.gethostbyname(domain)
        except socket.gaierror:
            if VERBOSE:
                print(f"\n      ⚠️  DNS 解析失败: {domain}")
            self.cache[domain] = None
            return None
        
        # 查询 GeoIP
        country = self._query_geoip_api(ip)
        self.cache[domain] = country
        
        return country
    
    def _query_geoip_api(self, ip: str) -> Optional[str]:
        """调用 GeoIP API 查询"""
        for attempt in range(GEOIP_RETRY):
            try:
                url = self.geoip_config['url'].format(ip=ip)
                timeout = self.geoip_config['timeout']
                
                # 添加 token（如果配置了）
                headers = {}
                if 'token' in self.geoip_config:
                    headers['Authorization'] = f"Bearer {self.geoip_config['token']}"
                
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                
                data = response.json()
                
                # 根据不同的 API 提取国家代码
                country_code = self._extract_country_code(data)
                
                return country_code
                
            except Exception as e:
                if attempt < GEOIP_RETRY - 1:
                    time.sleep(1)
                    continue
                else:
                    if VERBOSE:
                        print(f"\n      ⚠️  GeoIP 查询失败 ({ip}): {e}")
                    return None
    
    def _extract_country_code(self, data: dict) -> Optional[str]:
        """从不同 API 的响应中提取国家代码"""
        if GEOIP_PROVIDER == 'ip-api':
            if data.get('status') == 'success':
                return data.get('countryCode')
        
        elif GEOIP_PROVIDER == 'ipapi':
            return data.get('country_code')
        
        elif GEOIP_PROVIDER == 'ipinfo':
            return data.get('country')
        
        return None