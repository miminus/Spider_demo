from scrapy import log
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings

from baidu_tieba.spiders.kingsun import KingsunSpider
from baidu_tieba.spiders.kaoshi import DmozSpider_kaoshi  
from baidu_tieba.spiders.daan import DaanSpider
from baidu_tieba.spiders.lizong import LizongSpider


def  setup_crawler(spider_name):
    exec('spider = '+spider_name)
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    
for name in ['KingsunSpider()','DmozSpider_kaoshi()','DaanSpider()','LizongSpider()']:
    setup_crawler(name)
log.start()
reactor.run()




