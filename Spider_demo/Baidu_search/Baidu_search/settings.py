# -*- coding: utf-8 -*-

# Scrapy settings for Baidu_search project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'Baidu_search'

EXTENSIIONS_BASE = {
        'scrapy.telnet.TelnetConsole':0,
}

SPIDER_MODULES = ['Baidu_search.spiders']
NEWSPIDER_MODULE = 'Baidu_search.spiders'


ITEM_PIPELINES = {'Baidu_search.pipelines.Mysql_scrapy_pipeline':0}

###################################################################################################

AUTOTHROTTLE_DEBUG=True
AUTOTHROTTLE_START_DELAY=2000
DOWNLOAD_TIMEOUT = 5
#####################################设置下载延迟####################################################
DOWNLOAD_DELAY=1

# CONCURRENT_REQUESTS_PER_SPIDER=1

LOG_LEVEL='WARNING'
Sqlite_File = "D:/Work_space/Java/Spider_demo/Baidu_search/test.db"

