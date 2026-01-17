#!/usr/bin/env python3
"""
DoH Ruleset Generator
从 curl wiki 自动生成 Mihomo DoH 规则集
"""

import sys
from src.fetcher import WikiFetcher
from src.parser import DoHTableParser
from src.classifier import GeoIPClassifier
from src.generator import RulesetGenerator


def main():
    """主程序流程"""
    print("=" * 70)
    print("DoH Ruleset Generator - Mihomo 版本")
    print("使用 GeoIP 自动分类国内外 DoH 服务器")
    print("=" * 70)
    
    # 步骤 1: 获取 wiki 内容
    print("\n[1/4] 获取数据源...")
    fetcher = WikiFetcher()
    wiki_content = fetcher.fetch()
    
    if not wiki_content:
        print("❌ 无法获取 wiki 内容，程序退出")
        sys.exit(1)
    
    # 步骤 2: 解析 DoH 表格
    print("\n[2/4] 解析 DoH 表格...")
    parser = DoHTableParser(wiki_content)
    provider_urls = parser.parse()
    
    if not provider_urls:
        print("❌ 未解析到任何 DoH 提供商，程序退出")
        sys.exit(1)
    
    # 步骤 3: GeoIP 分类
    print("\n[3/4] 开始 GeoIP 分类...")
    classifier = GeoIPClassifier()
    china_providers, foreign_providers, reasons = classifier.classify(provider_urls)
    
    # 步骤 4: 生成规则文件
    print("\n[4/4] 生成规则文件...")
    generator = RulesetGenerator()
    generator.generate_all(china_providers, foreign_providers, reasons)
    
    # 完成
    print("\n" + "=" * 70)
    print("✅ 所有任务完成!")
    print("=" * 70)
    print(f"\n📂 输出目录: rules/")
    print(f"   - doh_foreign.yaml  (境外 DoH，用于代理)")
    print(f"   - doh_china.yaml    (国内 DoH，用于直连)")
    print(f"   - classification_log.txt (分类详情)")
    print(f"\n💡 在 Mihomo 中使用:")
    print(f"   rule-providers:")
    print(f"     doh-foreign:")
    print(f"       type: http")
    print(f"       behavior: domain")
    print(f"       url: \"https://raw.githubusercontent.com/你的用户名/仓库/main/rules/doh_foreign.yaml\"")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)