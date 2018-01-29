# -*- coding: utf-8 -*-

# Scrapy settings for syosetu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html


BOT_NAME = 'taptap'

SPIDER_MODULES = [BOT_NAME + '.spiders']
NEWSPIDER_MODULE = BOT_NAME + '.spiders'

# configuration of MySQL
CONNECTION = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "port": 3306,
        "charset": "utf8"
        }
DB_NAME = "taptap"
SHEET_NAMES_TIMESTAMP = True
SHEET_NAMES = {
    # "sheet1": ("SheetName1", SHEET_NAMES_TIMESTAMP, "ItemName1"),
    "sheet1": ("rank", SHEET_NAMES_TIMESTAMP, "RankItem"),
}
INSERT_NUM = 30

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# pausing and resuming crawls
JOB_KEEP = {
    "ON": False,
    "DIR": "your/crawl/job/dir"
}

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Disable cookies (enabled by default)
COOKIES_ENABLED = True
#COOKIES_DEBUG = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Encoding': 'gzip, deflate, br',
   'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7,en;q=0.6',
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'syosetu.middlewares.SyosetuSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # proxy
    # BOT_NAME + '.middlewares_proxy.ProxyMiddleware': 350,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 351,
    # useragent
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    BOT_NAME + '.middlewares_ua.RandomUserAgentMiddleware': 400,
}

# proxies for download
if BOT_NAME + '.middlewares_proxy.ProxyMiddleware' in DOWNLOADER_MIDDLEWARES:
    PROXIES = [
            {"ip_port": "127.0.0.1:1080", "user_pass": ""},
    ]

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # pipeline for image download, the Number should be smaller than others
    # BOT_NAME + '.pipelines_image.ImagesPipeline': 100,
    # BOT_NAME + '.pipelines_json.JSONPipeline': 200,
    BOT_NAME + '.pipelines_mysql.SQLPipeline': 300
}

IMAGES_PIPELINE_ON = False
if BOT_NAME + '.pipelines_image.ImagesPipeline' in ITEM_PIPELINES:
    IMAGES_PIPELINE_ON = True
    IMAGES_STORE = 'C:/setting/your/dir/to/save/images'
    IMAGES_EXPIRES = 30


# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Disable Http Redirect (enabled by default)
# REDIRECT_ENABLED = False
# HTTPERROR_ALLOWED_CODES = [302,]

# Logging
import logging
LOG_LEVEL = logging.DEBUG

LOG_ENABLED = True
LOG_ENCODING = "utf-8"
# LOG_FILE = BOT_NAME + "-log.txt"
