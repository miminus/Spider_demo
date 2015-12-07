# -*- coding: utf-8 -*-
import selenium.webdriver
from scrapy.settings.default_settings import DOWNLOAD_HANDLERS,\
    SPIDER_MIDDLEWARES

# Scrapy settings for kaidi project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'kaidi'

SPIDER_MODULES = ['kaidi.spiders']
NEWSPIDER_MODULE = 'kaidi.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'kaidi (+http://www.yourdomain.com)'
##################################设置下载图片信息##################################################
ITEM_PIPELINES = {'kaidi.pipelines.Mysql_scrapy_pipeline':1,
#                   'baidu_tieba.pipelines.MyImagesPipeline':2
                  }
#####################################设置下载延迟####################################################
DOWNLOAD_DELAY=0.5

USER_AGENT="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"
# AUTOTHROTTLE_ENABLED=True

###################################设置下载中间件########################################################
DOWNLOAD_HANDLERS = {
    'http': 'scrapy_webdriver.download.WebdriverDownloadHandler',
    'https': 'scrapy_webdriver.download.WebdriverDownloadHandler',
}

SPIDER_MIDDLEWARES = {
    'scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
}

WEBDRIVER_BROWSER = 'PhantomJS' # Or any other from selenium.webdriver
                                 # or 'your_package.CustomWebdriverClass'
                                 # or an actual class instead of a string.
# Optional passing of parameters to the webdriver
# WEBDRIVER_OPTIONS = {
#     'service_args': ['--debug=true', '--load-images=false', '--webdriver-loglevel=debug']
# }
#########################################################################################################
#####################################设置下载延迟####################################################
DOWNLOAD_DELAY=3

LOG_FILE=None
# LOG_LEVEL='WARNING'
LOG_LEVEL = 'DEBUG'