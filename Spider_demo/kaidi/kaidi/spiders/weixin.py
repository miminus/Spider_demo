#coding:utf-8
'''
Created on 2015/4/20

@author: MINUS
'''
import re
import time,os
import sys
import urllib

from scrapy import Selector, responsetypes
from scrapy import log, signals
import scrapy
from scrapy.contrib import spiderstate
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.mail import MailSender
from bs4 import BeautifulSoup
from scrapy_webdriver.http import WebdriverRequest

import MySQLdb as mdb
from kaidi.items import  Topic_Item


class WeixinDmozSpider(CrawlSpider):
    name = "wx"
#     allowed_domains = ["weixin.sogou.com"]
    
    start_urls = [
            'http://weixin.sogou.com/',
    ]
    def start_requests(self):
        db = mdb.connect(host="127.0.0.1",user="root",passwd="minus",db="yq",charset="utf8" )
        cur=db.cursor()
        cur.execute('select topic_id,topic_keywords from topic where topic_id in (select topic_id from site_topic where site_id=14)')
        topic_kws = cur.fetchall()
        kws_list=[]
        
        ##########################################################################################
        for topic_kw in topic_kws:
            topic_id = topic_kw[0]
            kws = topic_kw[1]
            kws_list = kws.split(',')
            for kw in kws_list:
                i='http://weixin.sogou.com/weixin?type=2&query=%s&page=1'% kw.encode('gbk')
                yield WebdriverRequest(i,meta={'topic_id': topic_id,'topic_kws': topic_kws})  
        
        '''
        for e in topic_kws:
            kws_list+=e[1].split(',')
        print kws_list
        
       
        for kw in kws_list:
            i='http://weixin.sogou.com/weixin?type=2&query=%s&page=1'% kw.encode('gbk')
            print kw.encode('gbk')
#             print i
#             raw_input('prompt')
            yield WebdriverRequest(i,meta={'topic_kws': topic_kws})   #默认 parse()
        '''    

  
    def __init__(self):
        super(WeixinDmozSpider,self).__init__()
        self.dig_pattern = re.compile('(\d+)')
        self.postid_pattern = re.compile('/p/(\d{10})')
      
    
    def parse_html_content(self,str):
        sub_p_1 = re.compile('<[^<>]*?>|\r', re.S)
        str = re.sub(sub_p_1, '', str)    
        ustr = str
        return ustr
    
    def parse(self,response):
        topic_kws = response.meta[ 'topic_kws' ]
        topic_id = response.meta['topic_id']
        sel = Selector(text=response.body, type="html")
        print "HTML",response.body
        with open('d:/1.html','wb') as f:
            f.write(response.body)
        response.url
#         raw_input('prompt')
        topic_lists = sel.xpath('//div[re:test(@class,"txt-box")]')
        print len(topic_lists)
        
        for topic in topic_lists:
            topic_item = Topic_Item()
            temp_sel = Selector(text=topic.extract())
            reply_num = 0
            topic_item['topic_reply']=reply_num
            
            title = temp_sel.xpath('//h4/a/text()').extract()[0]
            topic_item['topic_title']=title
            
            try:
                con = temp_sel.xpath('//p/text()').extract()[0]
            except IndexError,e:
                con=''    
            topic_item['topic_content']=con
            
             
            author = temp_sel.xpath('//div[re:test(@class,"s-p")]/a/@title').extract()[0]
            topic_item['topic_author'] = author
            
            
            post_time = temp_sel.xpath('//div[re:test(@class,"s-p")]/@t').extract()[0]
            post_time = int(post_time)
            post_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(post_time))
            topic_item['topic_post_time'] = post_time

            author_id = 0
            topic_item['poster_id'] = author_id

            thread_url = temp_sel.xpath('//h4/a/@href').extract()[0]
            print thread_url
            topic_item['topic_url'] = thread_url
            
            yield WebdriverRequest(thread_url,callback=self.parse_torrent,meta={'topic_kws': topic_kws,'topic_item':topic_item})
            
    
    def parse_torrent(self,response):
#         print raw_input('into>>>+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        topic_kws = response.meta[ 'topic_kws' ]
        topic_item = response.meta['topic_item']

        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']='微信'
        topic_item['site_id']=14
        topic_item['data_type']=0

        topic_item['thread_content'] = response.body
        topic_item['topic_db_message'] = topic_kws
        
        
        sel = Selector(text=response.body, type="html")
        poster_homepage = ''
        topic_item['homepage'] = poster_homepage
        
        try:
            con = sel.xpath('//div[re:test(@class,"rich_media_content")]').extract()[0]
            soup = BeautifulSoup(con, "html.parser")
            con = soup.get_text().strip()
        except IndexError,e:
            con=''  
        topic_item['topic_content']=con
        
        
        poster_image = ''
        topic_item['poster_image']=poster_image
        
        yield topic_item


    

    
    
    