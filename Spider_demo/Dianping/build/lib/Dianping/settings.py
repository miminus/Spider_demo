# -*- coding: utf-8 -*-

# Scrapy settings for Dianping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = "Dianping"

SPIDER_MODULES = ['Dianping.spiders']
NEWSPIDER_MODULE = 'Dianping.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Dianping (+http://www.yourdomain.com)'
USER_AGENT = 'http://www.scrapy.org'
###################################设置下载中间件########################################################
DOWNLOAD_HANDLERS = {
    'http': 'scrapy_webdriver.download.WebdriverDownloadHandler',
    'https': 'scrapy_webdriver.download.WebdriverDownloadHandler',
}

SPIDER_MIDDLEWARES = {
    'scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
}

WEBDRIVER_BROWSER = 'PhantomJS'   #PhantomJS