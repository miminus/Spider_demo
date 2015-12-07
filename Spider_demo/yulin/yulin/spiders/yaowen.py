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

class YaowenSpider(scrapy.Spider):
    name = "yaowen"
    allowed_domains = ["sohu.com"]
    start_urls = (
        'http://news.sohu.com/1/0903/61/subject212846158.shtml',
    )

    def start_requests(self):
        for i in self.start_urls:
            print i
            yield Request(i)   #默认 parse()      

    def __init__(self):
        self.time_pa=re.compile('(\d+)/(\d+) (\d+):(\d+)')
        self.items_pa = re.compile('<a href=.*?<br/>',re.S)
        self.thread_url_pa = re.compile('href="(.*?)"',re.S)
        self.title_pa = re.compile('<a.*?>(.*?)</a>',re.S)
        self.timeori_pa = re.compile('<span>(.*?)</span>',re.S)
        self.time_pa=re.compile('\((\d+)/(\d+) (\d+):(\d+)\)')
        self.site_id=41
        
    def parse(self,response):
#         topic_kws = response.meta[ 'topic_kws' ]
        sel = Selector(text=response.body, type="html")
#         topic_lists = sel.xpath('//td[re:test(@class,"newsblue1")]/a')
#         print len(topic_lists)
        
        all_content = BeautifulSoup(response.body,'html5lib')
        all_content_new = all_content.find_all(class_=re.compile('newsblue'))[0]
        all_content_new = all_content_new.prettify()
        topic_items = re.findall(self.items_pa, all_content_new)
        
        for topic in topic_items:
            topic_item = Topic_Item()
            thread_url = re.findall(self.thread_url_pa,topic)[0]
            print thread_url
            
            title = re.findall(self.title_pa, topic)[0].strip()
            print title
            
            time_ori = re.findall(self.timeori_pa, topic)[0].strip()
#             print time_ori
            time_temp = re.findall(self.time_pa, time_ori)[0]
            post_time = str(datetime.datetime.now().year)+'-'+str(time_temp[0])+'-'+str(time_temp[1])+" "+str(time_temp[2])+':'+str(time_temp[3])+':00'
            print post_time
            
            yield scrapy.Request(thread_url,callback=self.parse_torrent,meta={'topic_item':topic_item})
              
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']='搜狐要闻'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=3

        topic_item['thread_content'] = response.body
            
#         return topic_item  
            
