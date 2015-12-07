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

import MySQLdb as mdb
from baidu_tieba.items import  Topic_Item

class XueshengSpider(scrapy.Spider):
    name = "xuesheng"
    start_urls = [
            'http://tieba.baidu.com/f?kw=%E5%AD%A6%E7%94%9F&ie=utf-8&pn=0',
            'http://tieba.baidu.com/f?kw=%E5%AD%A6%E7%94%9F&ie=utf-8&pn=50',
            'http://tieba.baidu.com/f?kw=%E5%AD%A6%E7%94%9F&ie=utf-8&pn=100',
     
    ]
    def start_requests(self):
        db = mdb.connect(host="127.0.0.1",user="root",passwd="minus",db="yq",charset="utf8" )
        cur=db.cursor()
        cur.execute('select topic_id,topic_keywords from topic where topic_id in (select topic_id from site_topic where site_id=22)')
        topic_kws = cur.fetchall()
        for i in self.start_urls:
            yield Request(i,meta={'topic_kws': topic_kws})   #默认 parse()        

    def __init__(self,mailer=None):
        super(XueshengSpider,self).__init__()
        self.dig_pattern = re.compile('(\d+)')
        self.postid_pattern = re.compile('/p/(\d{10})')
        self.mail=mailer

    def parse_html_content(self,str):
        sub_p_1 = re.compile('<[^<>]*?>|\r', re.S)
        str = re.sub(sub_p_1, '', str)    
        ustr = str
        return ustr
    
    def parse(self,response):
        topic_kws = response.meta[ 'topic_kws' ]
        sel = Selector(text=response.body, type="html")
        topic_lists = sel.xpath('//li[re:test(@class,"j_thread_list clearfix")]')
        for topic in topic_lists:
            topic_item = Topic_Item()
            temp_sel = Selector(text=topic.extract())
            reply_num = temp_sel.xpath('//span[re:test(@class,"threadlist_rep_num.*?")]/text()').extract()[0]
            print reply_num
            topic_item['topic_reply']=reply_num
            
            title = temp_sel.xpath('//a[re:test(@class,"j_th_tit")]/text()').extract()[0]
            topic_item['topic_title']=title
            
            try:
                con = temp_sel.xpath('//div[re:test(@class,"threadlist_abs threadlist_abs_onlyline")]/text()').extract()[0]
            except IndexError,e:
                con=''    
            topic_item['topic_content']=con
            
             
            author = temp_sel.xpath('//span[re:test(@class,"tb_icon_author\s*")]/a[re:test(@class,"j_user_card\s*")]/text()').extract()[0]
#             print author
            topic_item['topic_author'] = author
            
            post_time = temp_sel.xpath('//span[re:test(@class,"threadlist_reply_date pull_right j_reply_data")]/text()').extract()[0]
            if '-' in post_time.strip():
                year = time.strftime('%Y',time.localtime())
                post_time = year+'-'+post_time.strip()+' 00:00:00'
            else:    
                today = time.strftime('%Y-%m-%d',time.localtime())
                post_time = today+' '+post_time.strip()+":00"
#             print post_time
            topic_item['topic_post_time'] = post_time

            author_id = temp_sel.xpath('//span[re:test(@class,"tb_icon_author\s*")]/@data-field').extract()[0]
            author_id = re.findall(self.dig_pattern,author_id)[0]
#             print author_id
            topic_item['poster_id'] = author_id

            thread_url = temp_sel.xpath('//a[re:test(@class,"j_th_tit")]/@href').extract()[0]
            domain = 'http://tieba.baidu.com'
            thread_url = domain+thread_url
            print thread_url
            topic_item['topic_url'] = thread_url
            yield scrapy.Request(thread_url,callback=self.parse_torrent,meta={'topic_kws': topic_kws,'topic_item':topic_item})
            
    def parse_torrent(self,response):
        topic_kws = response.meta[ 'topic_kws' ]
        topic_item = response.meta['topic_item']

        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']='学生贴吧'
        topic_item['site_id']=22
        topic_item['data_type']=3

        topic_item['thread_content'] = response.body
        topic_item['topic_db_message'] = topic_kws
        
        
        sel = Selector(text=response.body, type="html")
        poster_homepage = sel.xpath('//li[re:test(@class,"d_name")]/a/@href').extract()[0]
        poster_homepage = 'http://tieba.baidu.com'+poster_homepage
        topic_item['homepage'] = poster_homepage
        
        poster_image = sel.xpath('//a[re:test(@class,"p_author_face\s*")]/img/@src').extract()[0]
        topic_item['poster_image']=poster_image
        
        return topic_item        