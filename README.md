# DoH Ruleset Generator for Mihomo

自动从 [curl/curl wiki](https://github.com/curl/curl/wiki/DNS-over-HTTPS) 抓取 DoH 服务器列表，使用 GeoIP 分类国内外服务器，生成 Mihomo 格式的规则集。

## ✨ 特性

- 🌍 **GeoIP 自动分类** - 精准识别国内外 DoH 服务器
- 🤖 **GitHub Actions 自动更新** - 每天自动同步最新 DoH 列表
- 📦 **Mihomo 原生格式** - 直接支持 rule-provider
- 🔍 **详细分类日志** - 方便审查和调试
- 🛠️ **模块化设计** - 易于修改和扩展

## 📂 项目结构

```
doh-ruleset-generator/
├── .github/workflows/
│   └── update-doh-rules.yml      # GitHub Actions 自动化
├── src/
│   ├── config.py                  # 配置文件
│   ├── fetcher.py                 # 数据获取
│   ├── parser.py                  # 表格解析
│   ├── classifier.py              # GeoIP 分类
│   └── generator.py               # 规则生成
├── rules/                         # 输出目录
├── main.py                        # 主程序
└── requirements.txt               # 依赖
```

## 🚀 快速开始

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/doh-ruleset-generator.git
cd doh-ruleset-generator

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行生成器
python main.py
```

### GitHub Actions 自动化

1. **Fork 本仓库**
2. **启用 GitHub Actions**
3. **等待自动运行** (每天 UTC 00:00)
4. **手动触发**: Actions → Update DoH Rules → Run workflow

## 📝 配置说明

编辑 `src/config.py` 自定义配置：

```python
# GeoIP 服务提供商
GEOIP_PROVIDER = 'ip-api'  # 可选: 'ip-api', 'ipapi', 'ipinfo'

# 中国地区定义
CHINA_REGIONS = ['CN', 'HK', 'MO', 'TW']

# 判定阈值
CHINA_THRESHOLD = 0.5  # 50% 的服务器在中国地区则判定为国内

# 启用/禁用 GeoIP
ENABLE_GEOIP = True

# 请求延迟 (避免触发速率限制)
REQUEST_DELAY = 1.5  # 秒
```

## 📤 输出文件

### `doh_foreign.yaml` - 境外 DoH (Mihomo 格式)

```yaml
# DoH Servers Ruleset - 境外 DoH (建议代理)
# Generated at: 2026-01-17 12:00:00
# Total domains: 350

payload:
  - dns.google
  - cloudflare-dns.com
  - dns.quad9.net
  # ... 更多域名
```

### `doh_china.yaml` - 国内 DoH (Mihomo 格式)

```yaml
# DoH Servers Ruleset - 国内 DoH (建议直连)
# Generated at: 2026-01-17 12:00:00
# Total domains: 5

payload:
  - dns.alidns.com
  - dns.pub
  # ... 更多域名
```

### `classification_log.txt` - 分类详情

记录每个提供商的分类依据和 GeoIP 查询结果。

## 🔗 在 Mihomo 中使用

### 方式 1: 使用 GitHub Raw

```yaml
rule-providers:
  doh-foreign:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/你的用户名/你的仓库/main/rules/doh_foreign.yaml"
    path: ./ruleset/doh_foreign.yaml
    interval: 86400

rules:
  - RULE-SET,doh-foreign,🚀 节点选择
  - GEOIP,CN,DIRECT
  - MATCH,🚀 节点选择
```

### 方式 2: 使用 jsDelivr CDN (推荐)

```yaml
rule-providers:
  doh-foreign:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/你的用户名/你的仓库@main/rules/doh_foreign.yaml"
    path: ./ruleset/doh_foreign.yaml
    interval: 86400
```

### 方式 3: 使用 Ghproxy

```yaml
rule-providers:
  doh-foreign:
    type: http
    behavior: domain
    url: "https://ghproxy.com/https://raw.githubusercontent.com/你的用户名/你的仓库/main/rules/doh_foreign.yaml"
    path: ./ruleset/doh_foreign.yaml
    interval: 86400
```

## 🛠️ 开发指南

### 修改配置

所有配置都在 `src/config.py` 中，包括：
- GeoIP 服务商选择
- 速率限制设置
- 中国地区定义
- 输出文件配置

### 切换 GeoIP 服务商

```python
# src/config.py

# 使用 ip-api (免费，45次/分钟)
GEOIP_PROVIDER = 'ip-api'

# 使用 ipapi.co (免费，1000次/天)
GEOIP_PROVIDER = 'ipapi'

# 使用 ipinfo.io (需要 token)
GEOIP_PROVIDER = 'ipinfo'
GEOIP_APIS['ipinfo']['token'] = '你的_token'
```

### 禁用 GeoIP (快速测试)

```python
# src/config.py
ENABLE_GEOIP = False  # 所有提供商将被归类为境外
```

## 📊 统计信息

查看 GitHub Actions 运行日志获取最新统计：
- 总提供商数
- 总 DoH URL 数
- 国内/境外 DoH 分类结果

## ⚠️ 注意事项

1. **GeoIP 速率限制**
   - ip-api.com: 45次/分钟
   - 如果提供商很多，运行可能需要几分钟

2. **Anycast 网络**
   - 某些 DoH 服务器使用 Anycast (如 Cloudflare)
   - GeoIP 可能解析到中国 IP，但实际是全球服务
   - 建议查看 `classification_log.txt` 确认分类准确性

3. **DNS 解析失败**
   - 某些域名可能无法解析
   - 这些域名会跳过 GeoIP 查询

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 🔗 相关链接

- [curl/curl DoH Wiki](https://github.com/curl/curl/wiki/DNS-over-HTTPS)
- [Mihomo (Clash Meta)](https://github.com/MetaCubeX/mihomo)
- [ip-api.com](https://ip-api.com/)