"""
配置文件
"""

# ============= GeoIP 配置 =============

# GeoIP 服务提供商选择
# 可选: 'ip-api', 'ipapi', 'ipinfo'
from turtle import Turtle


GEOIP_PROVIDER = 'ip-api'

# GeoIP API 配置
GEOIP_APIS = {
    # ip-api.com - 免费，45次/分钟
    'ip-api': {
        'url': 'http://ip-api.com/json/{ip}?fields=status,countryCode',
        'rate_limit': 45,  # 每分钟请求数
        'timeout': 10,
    },
    
    # ipapi.co - 免费，1000次/天
    'ipapi': {
        'url': 'https://ipapi.co/{ip}/json/',
        'rate_limit': 30,
        'timeout': 10,
    },
    
    # ipinfo.io - 免费，50000次/月（需要注册获取 token）
    'ipinfo': {
        'url': 'https://ipinfo.io/{ip}/json',
        'rate_limit': 50,
        'timeout': 10,
        # 如果有 token，取消下面的注释
        # 'token': '你的_ipinfo_token',
    },
}

# 定义中国地区（仅中国大陆）
CHINA_REGIONS = ['CN']

# GeoIP 判定阈值：如果该比例的服务器在中国地区，则判定为中国提供商
CHINA_THRESHOLD = 0.5  # 50%

# 每个提供商检查的最大 URL 数量（避免速率限制）
MAX_URLS_PER_PROVIDER = 3

# ============= 数据源配置 =============

# curl wiki URL
CURL_WIKI_URL = "https://raw.githubusercontent.com/wiki/curl/curl/DNS-over-HTTPS.md"

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# ============= 输出配置 =============

# 输出目录
OUTPUT_DIR = "rules"

# 输出文件名
OUTPUT_FILES = {
    'foreign_yaml': 'doh_foreign.yaml',
    'china_yaml': 'doh_china.yaml',
    'foreign_list': 'doh_foreign.list',
    'china_list': 'doh_china.list',
    'classification_log': 'classification_log.txt',
}

# YAML 文件模板配置
YAML_CONFIG = {
    'indent': 2,
    'allow_unicode': True,
    'default_flow_style': False,
}

# ============= 调试配置 =============

# 是否启用详细日志
VERBOSE = True

# 是否启用 GeoIP 查询（设为 False 可快速测试）
ENABLE_GEOIP = True

# GeoIP 查询失败时的重试次数
GEOIP_RETRY = 5

# 请求间隔（秒）- 避免触发速率限制
REQUEST_DELAY = 1.5