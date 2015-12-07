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
    allowed_domains = ["weixin.sogou.com"]
    
    start_urls = [
            'http://weixin.sogou.com/',
    ]
    def start_requests(self):
        db = mdb.connect(host="127.0.0.1",user="root",passwd="minus",db="yq",charset="utf8" )
        cur=db.cursor()
        cur.execute('select topic_id,topic_keywords from topic where topic_id in (select topic_id from site_topic where site_id=14)')
        topic_kws = cur.fetchall()
        kws_list=[]
        for e in topic_kws:
            kws_list+=e[1].split(',')
        print kws_list
        for kw in kws_list:
            i='http://weixin.sogou.com/weixin?type=2&query=%s&page=1'% kw.encode('gbk')
            print kw.encode('gbk')
            print i
            raw_input('prompt')
            yield WebdriverRequest(i,meta={'topic_kws': topic_kws})   #默认 parse()

  
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
        sel = Selector(text=response.body, type="html")
        print "HTML",response.body
        with open('d:/1.html','wb') as f:
            f.write(response.body)
        response.url
        raw_input('prompt')
        topic_lists = sel.xpath('//div[re:test(@class,"txt-box")]')
        print len(topic_lists)
        
        


    

    
    
    