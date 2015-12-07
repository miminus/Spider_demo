# -*- coding: utf-8 -*-
import os
import re
import time

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy

from Dianping.items import  DianpingItem


class DianpingSpider(scrapy.Spider):
    name = "dianping"
    allowed_domains = ["dianping.com"]

    
    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.headers={
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Language' : 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
              'Connection' : 'keep-alive',
              'Cache-Control' : 'max-age=0',
              'DNT' : '1',
              'Host' : 'www.dianping.com',
              'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
              }
        self.MAX_PAGE = 25
        self.start_urls=[]
        for i in range(self.MAX_PAGE):
            self.start_urls.append('http://www.dianping.com/search/keyword/1/0_%E5%86%9C%E8%B4%B8%E5%B8%82%E5%9C%BA/p' + str(i+1) + '?aid=a3ce9b00cd3c762525e9cbbb5ca2bb254f4c116646b528da483d7c54faf8545462a6bbaedb2bb483a1a2993e91b6603f18c740d456faca0508b1fa4f8f25cc4b')
        

# http://t.dianping.com/movie/xian    http://t.dianping.com/movie/xian

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,headers=self.headers)

    def parse(self, response):

        all_content = BeautifulSoup(response.body,'html5lib')
        
        con_soup1 = all_content.select('div#shop-all-list li')
        print len(con_soup1)
        for con_soup2 in con_soup1:
            name = con_soup2.find('h4').get_text()
            
            addr1 = con_soup2.select('div.tag-addr a')[1].get_text().encode('utf-8')
            addr2 = con_soup2.select('div.tag-addr > span')[0].get_text().encode('utf-8')
            with open('123.txt','a+') as f:
                f.write(name+' , '+addr1+addr2+'\n')
            print '______________'
            
            
            
            
            
            
