# -*- coding: utf-8 -*-
from scrapy.settings.default_settings import LOG_LEVEL


# Scrapy settings for baidu_tieba project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
###################################################################################################
BOT_NAME = 'baidu_tieba'

SPIDER_MODULES = ['baidu_tieba.spiders']
NEWSPIDER_MODULE = 'baidu_tieba.spiders'


##################################设置下载图片信息##################################################
ITEM_PIPELINES = {'baidu_tieba.pipelines.Mysql_scrapy_pipeline':1,
#                   'baidu_tieba.pipelines.MyImagesPipeline':2
                  }
IMAGES_STORE = r'D:\Work_space\Java\Spider_demo\baidu_tieba\pictures'
IMAGES_EXPIRES = 10
IMAGES_THUMBS = {
            'small':(50,50),
            'big':(270,270), }
################################通过设置最小图片规格，可以过滤掉小图片###############################
# IMAGES_MIN_HEIGHT = 110
# IMAGES_MIN_WIDTH = 110
###################################################################################################

AUTOTHROTTLE_DEBUG=True
AUTOTHROTTLE_START_DELAY=2000
###################################################################################################

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'baidu_tieba (+http://www.yourdomain.com)'
BOT_NAME = 'tieba'


EXTENSIIONS_BASE = {
        'scrapy.telnet.TelnetConsole':0,
}

#######################################设置发件人信息################################################
MAIL_FROM='jdjisuanji06@163.com'
MAIL_USER='jdjisuanji06@163.com'
MAIL_HOST='smtp.163.com'
MAIL_PORT=25
MAIL_PASS='jisuanji06'
#####################################设置下载延迟####################################################
DOWNLOAD_DELAY=0.1

COMMANDS_MODULE = 'baidu_tieba.command'

# LOG_LEVEL='INFO' 
# LOG_STDOUT=True 
# LOG_ENABLED=True
# LOG_FILE='D:/3.log'   


