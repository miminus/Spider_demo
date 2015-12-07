# -*- coding: utf-8 -*-

# Scrapy settings for Tie_Bas project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'Tie_Bas'

SPIDER_MODULES = ['Tie_Bas.spiders']
NEWSPIDER_MODULE = 'Tie_Bas.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Tie_Bas (+http://www.yourdomain.com)'
#####################################设置下载延迟###################################################
DOWNLOAD_DELAY=0.5

##################################设置下载图片信息##################################################
ITEM_PIPELINES = {'Tie_Bas.pipelines.Mysql_scrapy_pipeline':1,
#                   'baidu_tieba.pipelines.MyImagesPipeline':2
                  }

DB_HOST = '127.0.0.1'
DB_NAME = 'root'
DB_PASSWD = 'minus'
DB = 'yuqing'

Sqlite_File = "D:/Work_space/Java/Spider_demo/Tie_Bas/test.db"

LOG_LEVEL='INFO' 
LOG_STDOUT = False 
LOG_ENABLED=True
LOG_FILE= None
