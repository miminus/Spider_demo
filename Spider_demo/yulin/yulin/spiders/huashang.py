# -*- coding: utf-8 -*-
import datetime
import os
import re
import time

from bs4 import BeautifulSoup
import chardet
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


class HuashangSpider(scrapy.Spider):
    name = "huashang"
    allowed_domains = ["hsw.cn"]
    start_urls = (
        'http://bbs.hsw.cn/thread-htm-fid-300.html',
    )
    
    def start_requests(self):
        for i in self.start_urls:
            print i
            yield Request(i)   #默认 parse()  
            
    def __init__(self):
        self.num_pa = re.compile('(\d+)/(\d+)')
        self.con_pa = re.compile('(<a class="subject_t f14".*?>.*?</a>)',re.S)
        self.site_id = 44 
        
    def parse_html_content(self,str):
        sub_p_1 = re.compile('<[^<>]*?>|\r', re.S)
        str = re.sub(sub_p_1, '', str)    
        str = str.replace('\n', '')
        str = str.replace('\r\n', '')
        str = str.replace(os.linesep, '')
        ustr = str
        return ustr        

    def parse(self, response):
        all_content = BeautifulSoup(response.body,'html5lib')
        main_content = all_content.find_all('tbody',attrs={'id':'threadlist'})[0]
        

        main_content = main_content.find_all('tr',class_="tr3")
        print len(main_content)
        f=open('d:/loog.txt','wb')
        for topic in main_content:
            topic_item = Topic_Item()
            
            title = topic.find_all('a')[1].get_text()
            f.write(title+os.linesep)
#             print title
            
            url_part = topic.find_all(class_='subject_t f14')[0].get('href')
            thread_url = 'http://bbs.hsw.cn/'+url_part
            print thread_url
            
            author = topic.find_all(class_='author')[0].a.get_text()
            print author
            
            time_part = topic.find_all(class_='author')[0].p.get_text()
            print time_part
            
            num_part = topic.find_all(class_='num')[0].get_text()
            nums = re.findall(self.num_pa,num_part)[0]
            print nums
            reply_num = nums[0]
            read_num = nums[1]
            
            content = re.findall(self.con_pa,topic.prettify())[0]
#             print self.parse_html_content(content).strip()

            poster_id =topic.find_all(class_='author')[0].a.get('href')
            print poster_id
            
            yield scrapy.Request(thread_url,callback=self.parse_torrent,meta={'topic_item':topic_item})
            
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']='华商论坛'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=3

        topic_item['thread_content'] = response.body
        # yield topic_item  
        
        
        
