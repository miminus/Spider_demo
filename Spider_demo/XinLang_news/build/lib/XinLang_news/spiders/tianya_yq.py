# -*- coding: utf-8 -*-
#   天涯舆情- 
#   实现了翻页功能
import re
import time

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import MySQLdb as mdb, os
from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item

class TianyaYqSpider(scrapy.Spider):
    name = "tianya_yq"
    allowed_domains = ["tianya.cn"]
    start_urls = (
        'http://yuqing.tianya.cn/2014/mrbb/list_1.shtml',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.site_id=36
        self.Flag_List = []
        self.Maxpage_List = [] 
        self.MAX_PAGE_NUM = 5

    def start_requests(self):
        for index, url in enumerate(self.start_urls):
            self.Flag_List.append(True)
            self.Maxpage_List.append(self.MAX_PAGE_NUM)
            yield scrapy.Request(url,meta={'index':index})
        
    def parse(self, response):
        index = response.meta['index']
        self.Maxpage_List[index] -= 1  
        
        sel = Selector(text=response.body, type="html")
        all_content = BeautifulSoup(response.body,'html5lib')
        
        
        
        
        
        
        
