# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule

class WeiboCurlSpider(CrawlSpider):
    name = "weibo_curl"
    allowed_domains = ["weibo.com"]
    start_urls = (
        'http://www.weibo.com/',
    )

    def parse(self, response):
        pass
