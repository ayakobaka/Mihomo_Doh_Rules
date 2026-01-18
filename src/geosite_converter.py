#!/usr/bin/env python3
"""
Geosite 转换器
将 .list 格式的域名规则转换为 Mihomo geosite 格式
"""

import os
import json
from typing import List, Dict, Set
from datetime import datetime


class GeositeConverter:
    """Geosite 格式转换器"""
    
    def __init__(self, input_dir: str = "rules", output_dir: str = "rules"):
        self.input_dir = input_dir
        self.output_dir = output_dir
    
    def convert_list_to_geosite(self, list_file: str, category_name: str) -> Dict:
        """
        将 .list 文件转换为 geosite 格式
        
        Args:
            list_file: .list 文件路径
            category_name: geosite 分类名称（如 'doh-foreign'）
        
        Returns:
            geosite 数据结构
        """
        domains = self._read_list_file(list_file)
        
        if not domains:
            print(f"⚠️  {list_file} 中没有域名")
            return None
        
        # 构建 geosite 数据结构
        geosite_entry = {
            "name": category_name,
            "domain": self._convert_domains_to_geosite_format(domains)
        }
        
        return geosite_entry
    
    def _read_list_file(self, list_file: str) -> Set[str]:
        """读取 .list 文件，提取域名"""
        domains = set()
        filepath = os.path.join(self.input_dir, list_file)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    
                    # 提取域名（格式: DOMAIN-SUFFIX,example.com）
                    if line.startswith('DOMAIN-SUFFIX,'):
                        domain = line.replace('DOMAIN-SUFFIX,', '').strip()
                        if domain:
                            domains.add(domain)
                    elif line.startswith('DOMAIN,'):
                        domain = line.replace('DOMAIN,', '').strip()
                        if domain:
                            domains.add(domain)
        
        except FileNotFoundError:
            print(f"❌ 文件不存在: {filepath}")
            return set()
        except Exception as e:
            print(f"❌ 读取文件失败 {filepath}: {e}")
            return set()
        
        return domains
    
    def _convert_domains_to_geosite_format(self, domains: Set[str]) -> List[str]:
        """
        将域名列表转换为 geosite 格式
        
        Mihomo geosite 格式支持:
        - domain:example.com (完整匹配)
        - full:example.com (完整匹配，同上)
        - keyword:example (关键词匹配)
        - regexp:^.*\.example\.com$ (正则匹配)
        
        对于 DOMAIN-SUFFIX,example.com，我们使用 domain: 前缀
        """
        geosite_domains = []
        
        for domain in sorted(domains):
            # DOMAIN-SUFFIX 在 geosite 中使用 domain: 前缀
            # 这会匹配该域名及其所有子域名
            geosite_domains.append(f"domain:{domain}")
        
        return geosite_domains
    
    def generate_geosite_dat(self, entries: List[Dict], output_file: str = "geosite.dat"):
        """
        生成 geosite.dat 文件（JSON 格式）
        
        注意: 真正的 geosite.dat 是 Protocol Buffers 二进制格式
        这里生成的是 JSON 格式，可以被某些工具转换为 .dat
        """
        geosite_data = {
            "version": 1,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "geosite": entries
        }
        
        filepath = os.path.join(self.output_dir, output_file)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(geosite_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 生成 {output_file}: {len(entries)} 个分类")
        return filepath
    
    def generate_text_format(self, entries: List[Dict], output_file: str = "geosite.txt"):
        """
        生成文本格式的 geosite 规则（便于查看和调试）
        """
        filepath = os.path.join(self.output_dir, output_file)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Geosite Rules (Text Format)\n")
            f.write(f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total categories: {len(entries)}\n\n")
            
            for entry in entries:
                f.write(f"# Category: {entry['name']}\n")
                f.write(f"# Domains: {len(entry['domain'])}\n")
                f.write("-" * 70 + "\n")
                
                for domain in entry['domain'][:10]:  # 只显示前10个
                    f.write(f"{domain}\n")
                
                if len(entry['domain']) > 10:
                    f.write(f"... and {len(entry['domain']) - 10} more domains\n")
                
                f.write("\n")
        
        print(f"✓ 生成 {output_file} (文本格式)")
        return filepath
    
    def convert_all(self):
        """转换所有 .list 文件"""
        print("\n🔄 开始转换 .list 规则为 geosite 格式...\n")
        
        entries = []
        
        # 转换境外 DoH
        foreign_entry = self.convert_list_to_geosite(
            'doh_foreign.list',
            'doh-foreign'
        )
        if foreign_entry:
            entries.append(foreign_entry)
            print(f"✓ doh-foreign: {len(foreign_entry['domain'])} 个域名")
        
        # 转换国内 DoH
        china_entry = self.convert_list_to_geosite(
            'doh_china.list',
            'doh-china'
        )
        if china_entry:
            entries.append(china_entry)
            print(f"✓ doh-china: {len(china_entry['domain'])} 个域名")
        
        if not entries:
            print("❌ 没有可转换的规则")
            return
        
        # 生成 JSON 格式的 geosite 文件
        print("\n📝 生成 geosite 文件...")
        self.generate_geosite_dat(entries, "geosite_doh.json")
        self.generate_text_format(entries, "geosite_doh.txt")
        
        print("\n✅ 转换完成!")


def main():
    """主函数"""
    converter = GeositeConverter()
    converter.convert_all()


if __name__ == "__main__":
    main()
