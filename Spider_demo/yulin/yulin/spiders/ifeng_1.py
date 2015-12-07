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


class Ifeng1Spider(scrapy.Spider):
    name = "ifeng_1"
    allowed_domains = ["ifeng.com"]
    start_urls=('http://sn.ifeng.com/zixun/jinrishanxi/list_0/1.shtml',
                'http://sn.ifeng.com/shanxidifangzixun/yulin/energy/list_0/1.shtml',
                'http://sn.ifeng.com/shanxidifangzixun/yulin/green/list_0/1.shtml')

    def start_requests(self):
        for i in self.start_urls:
            print i
            yield Request(i)   #默认 parse()      
            
    def __init__(self):
        self.time_pa=re.compile('(\d+)/(\d+) (\d+):(\d+)')
        self.site_id=40
     
    def parse(self,response):
        # with open('d:/page.html','wb') as f:
            # f.write(response.body)
        print response.body
        
#         topic_kws = response.meta[ 'topic_kws' ]
        sel = Selector(text=response.body, type="html")
        topic_lists = sel.xpath('//div[re:test(@class,"newsList")]/ul/li')
        
        # topic_lists = sel.xpath('//div[re:test(@class,"left")]/div[re:test(@class,"blockA")]/ul/li').extract()
        # print len(topic_lists)
        
        # sel.xpath('//td[re:test(@class,"margin-left")]/table[3]/tbody/tr').extract()
        
          for topic in topic_lists:
            topic_item = Topic_Item()
            temp_sel = Selector(text=topic.extract())
            time_ori= temp_sel.xpath('//h4').extract()[0]
            time_ll = re.findall(self.time_pa,time_ori)[0]
            
            post_time=str(datetime.datetime.now().year)+'-'+str(time_ll[0])+'-'+str(time_ll[2])+' '+str(time_ll[2])+':'+str(time_ll[3])
            print post_time
            
            title = temp_sel.xpath('//a/text()').extract()[0]
            print title
            
            thread_url = temp_sel.xpath('//a/@href').extract()[0]
            print thread_url
            topic_item['topic_url'] = thread_url
            
            yield scrapy.Request(thread_url,callback=self.parse_torrent,meta={'topic_item':topic_item})
              
    def parse_torrent(self,response):
        time_pa = re.compile('(\d+).*?(\d+).*?(\d+).*? (\d+):(\d+)')
        
        topic_item = response.meta['topic_item']
        
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']='凤观陕西'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=3

        topic_item['thread_content'] = response.body
           
        sel = Selector(text=response.body, type="html")   
        try:
            time_temp = sel.xpath('//span[re:test(@class,"ss01")]/text()')[0].extract()
            time_list = re.findall(time_pa,time_temp)[0]
            post_time_head = '-'.join(time_list[:3])
            post_time_end = ':'.join(time_list[3:5])
            post_time = post_time_head+' '+post_time_end+':00'
            print post_time
        except:
            return 
            
            
#         return topic_item     

        
