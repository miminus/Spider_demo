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

class SaishangfengSpider(scrapy.Spider):
    name = "saishangfeng"
    allowed_domains = ["ssfeng.com"]
    start_urls = (
        'http://bbs.ssfeng.com/forum.php?mod=forumdisplay&fid=14',
    )
    
    def start_requests(self):
        for i in self.start_urls:
            print i
            yield Request(i)   #默认 parse()   

    def __init__(self):
        self.site_id=42

    def parse(self, response):
        all_content = BeautifulSoup(response.body,'html5lib')
        all_content_new = all_content.find_all('tbody',attrs={'id':re.compile('normalthread_\d+')})
        print len(all_content_new)
        for topic in all_content_new:
            topic_item = Topic_Item()
            title = topic.find_all(class_='xst')[0].get_text()
            
            url_part = topic.find_all(class_='xst')[0].get('href')
            thread_url = 'http://bbs.ssfeng.com/'+url_part
            print thread_url
            
            poster_content = topic.find_all('cite')[0]
            poster_url = poster_content.a.get('href')
            poster_url = 'http://bbs.ssfeng.com/'+poster_url
            print poster_url
            
            poster_name = poster_content.a.get_text().strip()
            print poster_name
            
            post_time = topic.find_all('span')[0].get_text().strip()
            print post_time
            
            
            num_con = topic.find_all(class_='num')[0]
            reply_num = num_con.a.get_text().strip()
            print reply_num
            
            read_num = num_con.em.get_text().strip()
            print read_num
            
            yield scrapy.Request(thread_url,callback=self.parse_torrent,meta={'topic_item':topic_item})
            
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']='塞上风论坛'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=3

        topic_item['thread_content'] = response.body
            
#         return topic_item  
            
            
            
            
