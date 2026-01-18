#!/usr/bin/env python3
"""
Geosite DAT 文件生成器
将 .list 格式的域名规则转换为 Mihomo 可用的 geosite.dat 格式（Protocol Buffers）
"""

import os
from typing import List, Set
from datetime import datetime


class GeositeGenerator:
    """Geosite DAT 生成器（Protocol Buffers 实现）"""
    
    def __init__(self, input_dir: str = "rules", output_dir: str = "rules"):
        self.input_dir = input_dir
        self.output_dir = output_dir
    
    def read_list_file(self, list_file: str) -> Set[str]:
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
                    
                    # 提取域名
                    if line.startswith('DOMAIN-SUFFIX,'):
                        domain = line.replace('DOMAIN-SUFFIX,', '').strip()
                        if domain:
                            domains.add(domain)
                    elif line.startswith('DOMAIN,'):
                        domain = line.replace('DOMAIN,', '').strip()
                        if domain:
                            # DOMAIN 完整匹配，使用 full: 前缀
                            domains.add(f"full:{domain}")
        
        except FileNotFoundError:
            print(f"❌ 文件不存在: {filepath}")
            return set()
        except Exception as e:
            print(f"❌ 读取文件失败 {filepath}: {e}")
            return set()
        
        return domains
    
    def write_protobuf_varint(self, value: int) -> bytes:
        """写入 Protocol Buffers 变长整数"""
        result = bytearray()
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    def write_protobuf_string(self, field_number: int, value: str) -> bytes:
        """写入 Protocol Buffers 字符串字段"""
        data = value.encode('utf-8')
        result = bytearray()
        # Tag: (field_number << 3) | wire_type(2=string)
        result.extend(self.write_protobuf_varint((field_number << 3) | 2))
        # Length
        result.extend(self.write_protobuf_varint(len(data)))
        # Data
        result.extend(data)
        return bytes(result)
    
    def encode_domain(self, domain: str, field_number: int = 2) -> bytes:
        """编码单个域名为 Protocol Buffers 格式"""
        result = bytearray()
        
        # 判断域名类型
        if domain.startswith('full:'):
            domain_type = 3
            domain_value = domain[5:]
        elif domain.startswith('regexp:'):
            domain_type = 1
            domain_value = domain[7:]
        elif domain.startswith('keyword:'):
            domain_type = 0
            domain_value = domain[8:]
        else:
            # Plain (默认，相当于 DOMAIN-SUFFIX)
            domain_type = 0
            domain_value = domain
        
        # Domain 消息
        domain_message = bytearray()
        
        # Field 1: type (varint)
        domain_message.extend(self.write_protobuf_varint((1 << 3) | 0))
        domain_message.extend(self.write_protobuf_varint(domain_type))
        
        # Field 2: value (string)
        domain_message.extend(self.write_protobuf_string(2, domain_value))
        
        # 包装为嵌套消息
        result.extend(self.write_protobuf_varint((field_number << 3) | 2))
        result.extend(self.write_protobuf_varint(len(domain_message)))
        result.extend(domain_message)
        
        return bytes(result)
    
    def encode_geosite_entry(self, category_name: str, domains: List[str]) -> bytes:
        """编码一个 geosite 条目为 Protocol Buffers 格式"""
        entry_data = bytearray()
        
        # Field 1: tag (category name)
        entry_data.extend(self.write_protobuf_string(1, category_name))
        
        # Field 2: domains (repeated)
        for domain in sorted(domains):
            entry_data.extend(self.encode_domain(domain, 2))
        
        return bytes(entry_data)
    
    def generate_dat_file(self, category_name: str, domains: Set[str], output_file: str):
        """生成 geosite.dat 文件"""
        if not domains:
            print(f"⚠️  {category_name} 没有域名，跳过生成")
            return
        
        print(f"\n📝 生成 {output_file}...")
        print(f"   分类: {category_name}")
        print(f"   域名数: {len(domains)}")
        
        try:
            # 编码 SiteGroup
            entry_bytes = self.encode_geosite_entry(category_name, list(domains))
            
            # 包装为 GeoSiteList
            result = bytearray()
            result.extend(self.write_protobuf_varint((1 << 3) | 2))
            result.extend(self.write_protobuf_varint(len(entry_bytes)))
            result.extend(entry_bytes)
            
            # 确保输出目录存在
            os.makedirs(self.output_dir, exist_ok=True)
            
            # 写入文件
            filepath = os.path.join(self.output_dir, output_file)
            print(f"   写入文件: {filepath}")
            
            with open(filepath, 'wb') as f:
                f.write(result)
            
            # 验证文件是否创建
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"✓ 生成完成: {output_file} ({file_size} 字节)")
            else:
                print(f"❌ 文件创建失败: {filepath}")
                
        except Exception as e:
            print(f"❌ 生成 {output_file} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_text_info(self, category_name: str, domains: Set[str], output_file: str):
        """生成文本格式的信息文件（便于查看）"""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            filepath = os.path.join(self.output_dir, output_file)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Geosite: {category_name}\n")
                f.write(f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total domains: {len(domains)}\n")
                f.write(f"# Format: Protocol Buffers binary (.dat)\n\n")
                
                f.write("Domains (first 20):\n")
                for domain in sorted(domains)[:20]:
                    f.write(f"  {domain}\n")
                
                if len(domains) > 20:
                    f.write(f"  ... and {len(domains) - 20} more domains\n")
            
            if os.path.exists(filepath):
                print(f"✓ 生成信息文件: {output_file}")
            else:
                print(f"❌ 信息文件创建失败: {filepath}")
                
        except Exception as e:
            print(f"❌ 生成信息文件 {output_file} 时出错: {e}")
    
    def convert_all(self):
        """转换所有 .list 文件为 .dat"""
        print("=" * 70)
        print("Geosite DAT Generator")
        print("将 .list 规则转换为 Mihomo geosite.dat 格式")
        print("=" * 70)
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ 创建输出目录: {self.output_dir}")
        
        # 转换境外 DoH
        print("\n[1/2] 处理境外 DoH...")
        foreign_list = os.path.join(self.input_dir, 'doh_foreign.list')
        print(f"   读取文件: {foreign_list}")
        
        if not os.path.exists(foreign_list):
            print(f"   ⚠️  文件不存在: {foreign_list}")
        else:
            print(f"   ✓ 文件存在")
            foreign_domains = self.read_list_file('doh_foreign.list')
            print(f"   提取到 {len(foreign_domains)} 个域名")
            
            if foreign_domains:
                self.generate_dat_file('doh-foreign', foreign_domains, 'doh_foreign.dat')
                self.generate_text_info('doh-foreign', foreign_domains, 'doh_foreign_info.txt')
            else:
                print(f"   ⚠️  没有提取到任何域名")
        
        # 转换国内 DoH
        print("\n[2/2] 处理国内 DoH...")
        china_list = os.path.join(self.input_dir, 'doh_china.list')
        print(f"   读取文件: {china_list}")
        
        if not os.path.exists(china_list):
            print(f"   ⚠️  文件不存在: {china_list}")
        else:
            print(f"   ✓ 文件存在")
            china_domains = self.read_list_file('doh_china.list')
            print(f"   提取到 {len(china_domains)} 个域名")
            
            if china_domains:
                self.generate_dat_file('doh-china', china_domains, 'doh_china.dat')
                self.generate_text_info('doh-china', china_domains, 'doh_china_info.txt')
            else:
                print(f"   ⚠️  没有提取到任何域名")
        
        print("\n" + "=" * 70)
        print("✅ 转换完成!")
        print("=" * 70)


def main():
    """主函数"""
    generator = GeositeGenerator()
    generator.convert_all()


if __name__ == "__main__":
    main()
