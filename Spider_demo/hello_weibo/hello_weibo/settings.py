# -*- coding: utf-8 -*-
from scrapy.settings.default_settings import LOG_STDOUT, LOG_ENABLED,LOG_FILE

# Scrapy settings for hello_weibo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'hello_weibo'

SPIDER_MODULES = ['hello_weibo.spiders']
NEWSPIDER_MODULE = 'hello_weibo.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hello_weibo (+http://www.yourdomain.com)'
###################################设置下载中间件########################################################
DOWNLOAD_HANDLERS = {
    'http': 'scrapy_webdriver.download.WebdriverDownloadHandler',
    'https': 'scrapy_webdriver.download.WebdriverDownloadHandler',
}

SPIDER_MIDDLEWARES = {
    'scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
}

WEBDRIVER_BROWSER = 'Firefox' # Or any other from selenium.webdriver
                                 # or 'your_package.CustomWebdriverClass'
                                 # or an actual class instead of a string.
# Optional passing of parameters to the webdriver
# WEBDRIVER_OPTIONS = {
#     'service_args': ['--debug=true', '--load-images=false', '--webdriver-loglevel=debug']
# }
###############################################################################################

ITEM_PIPELINES = {'hello_weibo.pipelines.Mysql_scrapy_pipeline':0}

#####################################设置下载延迟####################################################
DOWNLOAD_DELAY=2

# LOG_LEVEL='WARNING'
# LOG_STDOUT=True
# LOG_ENABLED=True
# LOG_FILE='D:/3.log'