# -*- coding: utf-8 -*-
import re
import time,os

from bs4 import BeautifulSoup
import chardet
from scrapy import Selector, responsetypes
from scrapy import log, signals
import scrapy
import scrapy
from scrapy.contrib import spiderstate
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.mail import MailSender

import MySQLdb as mdb
from kaidi.items import  Topic_Item


class KaidySpider(scrapy.Spider):
    name = "kaidy"
    allowed_domains = ["kdnet.net"]
    start_urls = (
        'http://club.kdnet.net/list.asp?t=0&boardid=40&selTimeLimit=0&action=&topicmode=0&s=&page=1',
        'http://club.kdnet.net/list.asp?t=0&boardid=101&selTimeLimit=0&action=&topicmode=0&s=&page=1',
        'http://club.kdnet.net/list.asp?t=0&boardid=55&selTimeLimit=0&action=&topicmode=0&s=&page=1',
        'http://club.kdnet.net/list.asp?t=0&boardid=56&selTimeLimit=0&action=&topicmode=0&s=&page=1',
    )
    def start_requests(self):
        db = mdb.connect(host="127.0.0.1",user="root",passwd="minus",db="yq",charset="utf8" )
        cur=db.cursor()
        cur.execute('select topic_id,topic_keywords from topic where topic_id in (select topic_id from site_topic where site_id=%d)' % self.site_id)
        topic_kws = cur.fetchall()
       
        for i in self.start_urls:
            yield Request(i,meta={'topic_kws': topic_kws})
    
    def __init__(self):
        self.site_id =8
        self.post_time_pa = re.compile('(\d{4})[/-](\d*)[/-](\d*) (\d{2}):(\d{2})')
        self.reply_pa = re.compile('(\d*)/(\d*)')
        self.urser_id_pa = re.compile('userid=(\d+)')
#         self.post_time_pa = re.compile('\d{4}\/\d*\/\d* \d{2}:\d{2}')
        
        
    def parse_html_content(self,str):
        sub_p_1 = re.compile('<[^<>]*?>|\r', re.S)
        str = re.sub(sub_p_1, '', str)    
        ustr = str
        return ustr

    def parse(self, response):
        print '&*&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
        topic_kws = response.meta[ 'topic_kws' ]
        sel = Selector(text=response.body, type="html")
        all_content = BeautifulSoup(response.body,'html5lib')

            
        content_splits = all_content.find_all('tr',attrs={"name":re.compile("showreply_.*?")})
        for topic in content_splits:
            topic_item = Topic_Item()
            topic_item['topic_db_message'] = topic_kws
            topic_ = Selector(text=topic.prettify(), type="html")
#             with open('d:/1.txt','wb') as f:
#                 f.write(topic_.extract())
        
            reply_click = topic_.xpath('//td[re:test(@class,"statistics clearfix")]/text()').extract()[0].strip() 
            print reply_click
            reply_click = re.findall(self.reply_pa,reply_click)[0]
            print reply_click[0],reply_click[1]
            topic_item['topic_reply'] = reply_click[0]
            
            
            topic_title = topic.find_all('span',class_='f14px')[0].get_text().strip()
#             topic_title = self.parse_html_content(topic_title.get_text())
            print topic_title
            topic_item['topic_title']=topic_title
            topic_item['topic_content'] = topic_title
            
            url = topic_.xpath('//span[re:test(@class,"f14px")]/a/@href').extract()[0].strip() 
            url = 'http://club.kdnet.net/'+url
            print url 
            topic_item['topic_url'] = url       
            
            topic_author = topic.find_all('td',class_='author')[0].get_text().strip()
#             topic_title = self.parse_html_content(topic_title.get_text())
            print topic_author
            topic_item['topic_author']=topic_author
            
            post_time = topic_.xpath('//td[re:test(@class,"lastupdate")]/text()').extract()[0].strip()
            post_time = re.findall(self.post_time_pa,post_time)[0] 
            post_time = post_time[0]+'-'+post_time[1]+'-'+post_time[2]+' '+post_time[3]+':'+post_time[4]+':'+'00'
            print post_time  
            topic_item['topic_post_time'] = post_time   
            
            
            yield scrapy.Request(url,callback=self.parse_torrent,meta={'topic_item':topic_item})
 
    def parse_torrent(self,response):  
        all_content = BeautifulSoup(response.body,'html5lib')
        sel = Selector(text=all_content.prettify(), type="html")
        topic_item = response.meta['topic_item']
        topic_item['thread_content'] = response.body
        
        topic_item['topic_board']='凯迪社区'
        print '+++++++++++++++++++'
        try:
            homepage = sel.xpath('//div[re:test(@class,"postspecific")]//span[re:test(@class,"c-main")]/a/@href').extract()[0].strip()
            topic_item['homepage'] = homepage 
            
            user_id = re.findall(self.urser_id_pa,homepage)[0]
            topic_item['poster_id'] = user_id
        except:
            topic_item['homepage'] = '' 
            topic_item['poster_id'] = '111'
        
        topic_item['data_type']=2
        topic_item['site_id']=8        
        
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time    
            
            
        return topic_item
 
