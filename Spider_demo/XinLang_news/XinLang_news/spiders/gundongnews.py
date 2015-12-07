# -*- coding: utf-8 -*-
import re
import time

from bs4 import BeautifulSoup
from chardet import detect
from scrapy import Selector
import scrapy
from scrapy.contrib import spiderstate
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import DropItem
from scrapy.http import Request

from XinLang_news.items import  Topic_Item



class GundongnewsSpider(scrapy.Spider):
    name = "gundongnews"
#     allowed_domains = ["sina.com.cn"]
    start_urls = (
        'http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=89&spec=&type=&ch=&k=&offset_page=0&offset_num=0&num=60&asc=&page=1&r=0.4799186997836631',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.topic_pa = re.compile('{channel : (.*?,time : \d+})',re.S)
        self.channel_pa = re.compile('{title : "(.*?)"')
        self.title_pa = re.compile(',title : "(.*?)"', re.S)
        self.url_pa = re.compile(r'"(http://.*?)",',re.S)
        self.time_pa = re.compile(r'time : (\d+)')

    def start_requests(self):
        for i in self.start_urls:
            yield Request(i)

    def parse_html_content(self,str):
        sub_p_1 = re.compile('<[^<>]*?>|\r', re.S)
        str = re.sub(sub_p_1, '', str)  
        str = str.replace(' ','')
        str = str.replace('\n','')
        ustr = str
        return ustr

    def parse(self, response):
#         with open('d:/page.txt','wb') as f:
#             f.write(response.body)
        all_content = response.body
        topics = re.findall(self.topic_pa, all_content)
#         print len(topics)
        for topic in topics:
            topic_item = Topic_Item()
            channel = re.findall(self.channel_pa, topic)[0]
            # topic_item['topic_channel'] = channel.decode('gbk','ignore')
            
            title = re.findall(self.title_pa, topic)[0]
            topic_item['topic_title'] = title.decode('gbk','ignore')
#             print detect(title)
            
            url = re.findall(self.url_pa, topic)[0]
            topic_item['topic_url'] = url
            
            post_time_str = re.findall(self.time_pa, topic)[0]
            post_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(post_time_str)))
            topic_item['topic_post_time'] = post_time
            
            yield scrapy.Request(url,callback=self.parse_torrent,meta={'topic_item':topic_item})
        
    def parse_torrent(self,response): 
       topic_item = response.meta['topic_item']
       all_content = BeautifulSoup(response.body,'html5lib')
#        from scrapy.shell import inspect_response
#        inspect_response(response, self)
       try:
           thread_content = all_content.find_all("div",attrs={"id":"artibody"})[0].prettify()
       except IndexError:
           thread_content='Video'    

       sel = Selector(text=all_content.prettify(), type="html")
#        print all_content

       topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
     
       topic_item['topic_content']  = self.parse_html_content(thread_content)
       
       topic_item['thread_content'] = response.body
      
       
       yield topic
       _item
            
            
