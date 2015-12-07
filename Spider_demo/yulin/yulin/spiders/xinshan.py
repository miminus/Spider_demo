# -*- coding: utf-8 -*-
import datetime
import re
import time

from bs4 import BeautifulSoup
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

import MySQLdb as mdb
from yulin.items import  Topic_Item
import chardet

class XinshanSpider(scrapy.Spider):
    name = "xinshan"
    allowed_domains = ["sina.com.cn"]
    start_urls = (
        'http://sx.sina.com.cn/yulin/focus/list.html',
    )

    def start_requests(self):
        for i in self.start_urls:
            print i
            yield Request(i)   #默认 parse()  
            
    def __init__(self):
        self.site_id = 43

    def parse(self, response):
        all_content = BeautifulSoup(response.body,'html5lib')
        main_content = all_content.find_all('ul',attrs={'id':'pagecontent'})[0]
      
        all_content_new = main_content.find_all('li')
#         print len(all_content_new)
     
        for cnt,topic in enumerate(all_content_new):
            if cnt>60:
                break
            topic_item = Topic_Item()
            
            time_con = topic.span.get_text().strip()
            print time_con
            cnt+=1
            
            title = topic.find_all('a')[0].get_text()
            print title.encode('gbk','ignore')
            
            url_part = topic.find_all('a')[0].get('href')
            thread_url ='http://sx.sina.com.cn/'+url_part
            print thread_url
            
            time_part = topic.span.get_text().strip()
            post_time = str(datetime.datetime.now().year)+'-'+time_part
            print post_time
            
            yield scrapy.Request(thread_url,callback=self.parse_torrent,meta={'topic_item':topic_item})
      
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']='新浪陕西'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=3

        topic_item['thread_content'] = response.body     
#         return topic_item  
        
        
