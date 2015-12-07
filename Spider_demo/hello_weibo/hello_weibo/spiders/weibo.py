# -*- coding: utf-8 -*-
import re
import time

from scrapy import Selector, responsetypes
from scrapy import log, signals
import scrapy
from scrapy.contrib import spiderstate
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.mail import MailSender
from bs4 import BeautifulSoup
from scrapy_webdriver.http import WebdriverRequest

import MySQLdb as mdb
# from hello_weibo.items import  Topic_Item


class WeiboSpider(scrapy.Spider):
    name = "weibo"
    allowed_domains = ["weibo.com"]
    start_urls = (
        'http://weibo.com/u/3105241737',
    )

    def start_requests(self):
        for i in self.start_urls:
            yield WebdriverRequest(i)   #默认 parse()

    def parse(self, response):
        print response.body
        with open('d:/1.html','wb') as f:
            f.write(response.body)
        print response.url
