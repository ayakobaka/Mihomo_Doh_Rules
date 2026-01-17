"""
规则文件生成模块
生成 Mihomo 格式的 YAML 规则文件
"""

import os
import yaml
from typing import Dict, List, Set
from datetime import datetime
from .config import OUTPUT_DIR, OUTPUT_FILES, YAML_CONFIG
from .parser import DoHTableParser


class RulesetGenerator:
    """规则文件生成器"""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ 创建输出目录: {self.output_dir}")
    
    def generate_all(self, 
                     china_providers: Dict[str, List[str]], 
                     foreign_providers: Dict[str, List[str]],
                     reasons: Dict[str, str]):
        """
        生成所有规则文件
        
        Args:
            china_providers: 中国 DoH 提供商
            foreign_providers: 境外 DoH 提供商
            reasons: 分类依据
        """
        print(f"\n📝 开始生成规则文件...")
        
        # 生成 YAML 格式（Mihomo 使用）
        foreign_count = self._generate_yaml(
            foreign_providers,
            OUTPUT_FILES['foreign_yaml'],
            "境外 DoH (建议代理)"
        )
        
        china_count = self._generate_yaml(
            china_providers,
            OUTPUT_FILES['china_yaml'],
            "国内 DoH (建议直连)"
        )
        
        # 生成 List 格式（备用）
        self._generate_list(
            foreign_providers,
            OUTPUT_FILES['foreign_list'],
            "境外 DoH (建议代理)"
        )
        
        self._generate_list(
            china_providers,
            OUTPUT_FILES['china_list'],
            "国内 DoH (建议直连)"
        )
        
        # 生成分类日志
        self._generate_classification_log(
            china_providers,
            foreign_providers,
            reasons
        )
        
        print(f"\n✅ 规则文件生成完成!")
        print(f"   境外 DoH: {foreign_count} 个域名")
        print(f"   国内 DoH: {china_count} 个域名")
    
    def _generate_yaml(self, 
                       providers: Dict[str, List[str]], 
                       filename: str,
                       title: str) -> int:
        """
        生成 YAML 格式规则文件（Mihomo rule-provider 格式）
        ，并按提供商分组添加注释。
        
        Returns:
            int: 域名数量
        """
        provider_domains, all_domains = self._group_domains_by_provider(providers)
        
        if not all_domains:
            print(f"⚠️  跳过 {filename}: 无数据")
            return 0
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # 写入注释
            f.write(f"# DoH Servers Ruleset - {title}\n")
            f.write(f"# Auto-generated from curl/curl wiki\n")
            f.write(f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total domains: {len(all_domains)}\n")
            f.write(f"# Format: Mihomo rule-provider (behavior: domain)\n\n")
            
            # 写入分组后的 payload
            f.write("payload:\n")
            for provider in sorted(provider_domains.keys()):
                domains = sorted(provider_domains[provider])
                if not domains:
                    continue
                f.write(f"  # {provider}\n")
                for domain in domains:
                    f.write(f"  - {domain}\n")
        
        print(f"✓ {filename}: {len(all_domains)} 个域名")
        return len(all_domains)
    
    def _generate_list(self,
                       providers: Dict[str, List[str]],
                       filename: str,
                       title: str):
        """生成 List 格式规则文件（DOMAIN-SUFFIX），按提供商分组并添加注释"""
        provider_domains, all_domains = self._group_domains_by_provider(providers)
        
        if not all_domains:
            return
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# DoH Servers Ruleset - {title}\n")
            f.write(f"# Auto-generated from curl/curl wiki\n")
            f.write(f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total rules: {len(all_domains)}\n\n")
            
            for provider in sorted(provider_domains.keys()):
                domains = sorted(provider_domains[provider])
                if not domains:
                    continue
                f.write(f"# {provider}\n")
                for domain in domains:
                    f.write(f"DOMAIN-SUFFIX,{domain}\n")
                f.write("\n")
        
        print(f"✓ {filename}: {len(all_domains)} 条规则")
    
    def _generate_classification_log(self,
                                     china_providers: Dict[str, List[str]],
                                     foreign_providers: Dict[str, List[str]],
                                     reasons: Dict[str, str]):
        """生成分类日志"""
        filepath = os.path.join(self.output_dir, OUTPUT_FILES['classification_log'])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("DoH 提供商分类日志\n")
            f.write("=" * 70 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"分类方法: GeoIP\n\n")
            
            # 中国提供商
            f.write(f"🇨🇳 中国 DoH 提供商 ({len(china_providers)} 个)\n")
            f.write("-" * 70 + "\n\n")
            
            for provider in sorted(china_providers.keys()):
                f.write(f"[{provider}]\n")
                f.write(f"分类依据: {reasons.get(provider, '未知')}\n")
                f.write(f"URL 数量: {len(china_providers[provider])}\n")
                f.write("URLs:\n")
                for url in china_providers[provider]:
                    f.write(f"  - {url}\n")
                f.write("\n")
            
            # 境外提供商（只显示前20个）
            f.write(f"\n🌍 境外 DoH 提供商 ({len(foreign_providers)} 个)\n")
            f.write("-" * 70 + "\n\n")
            
            for provider in sorted(foreign_providers.keys())[:20]:
                f.write(f"[{provider}]\n")
                f.write(f"分类依据: {reasons.get(provider, '未知')}\n")
                f.write(f"URL 数量: {len(foreign_providers[provider])}\n")
                for url in foreign_providers[provider][:2]:
                    f.write(f"  - {url}\n")
                f.write("\n")
            
            if len(foreign_providers) > 20:
                f.write(f"... 还有 {len(foreign_providers) - 20} 个境外提供商\n")
        
        print(f"✓ {OUTPUT_FILES['classification_log']}: 分类日志")
    
    def _group_domains_by_provider(self, providers: Dict[str, List[str]]):
        """按提供商分组域名，同时保证全局域名不重复"""
        provider_domains: Dict[str, List[str]] = {}
        all_domains: Set[str] = set()
        
        for provider, urls in providers.items():
            for url in urls:
                domain = DoHTableParser.extract_domain(url)
                if not domain or domain in all_domains:
                    continue
                all_domains.add(domain)
                if provider not in provider_domains:
                    provider_domains[provider] = []
                provider_domains[provider].append(domain)
        
        return provider_domains, all_domains