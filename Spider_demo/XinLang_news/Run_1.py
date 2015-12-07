#coding:utf-8
'''
Created on 2015年9月8日

@author: MINUS
'''
from scrapy import log
from scrapy.crawler import Crawler , CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings
from XinLang_news.spiders.fudan import FudanSpider



# gundongnews = FudanSpider()
settings = get_project_settings()

# crawlerprocess = CrawlerProcess(settings)
# crawler = crawlerprocess.create_crawler()
# crawler.crawl(gundongnews)
# crawlerprocess.start()
##############################################################################
spname_list = ['jyb','tju']
# spname = 'jyb'
crawlerprocess = CrawlerProcess(settings)
for spname in spname_list:
    crawler = crawlerprocess.create_crawler(spname)
    spider = crawler.spiders.create(spname)
    crawler.crawl(spider)
crawlerprocess.start()
# crawlerprocess.start_reactor()

# log.start()
# reactor.run()





