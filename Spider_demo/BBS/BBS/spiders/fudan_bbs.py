# -*- coding: utf-8 -*-
#  复旦大学日月光华  -  全 站 十 大 话 题 （一天内）
#  无翻页
import re
import time, os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import MySQLdb as mdb
from BBS.items import  Topic_Item
from .. import settings

class FudanBbsSpider(scrapy.Spider):
    name = "fudan_bbs"
    allowed_domains = ["fudan.edu.cn"]
    start_urls = (
        'http://bbs.fudan.edu.cn/bbs/top10',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.max_page = 10
        self.site_id=1

    def start_requests(self):
        db = mdb.connect(host = settings.DB_HOST, user = settings.DB_NAME, passwd = settings.DB_PASSWD,db = settings.DB,charset="utf8" )        
        cur=db.cursor()
        cur.execute('select topic_id,topic_keywords from topic where topic_id in (select topic_id from site_topic where site_id=%d)' % self.site_id)
        topic_kws = cur.fetchall()
        #####################################################################################
        now = time.strftime('%Y%m%d', time.localtime())
        cur.execute('show tables from yq like "post_%s"' % str(now))
        db.commit()
        tables = cur.fetchone()
        cur.close()
        db.close()
        # print tables
        if tables == None or len(tables)==0:
            os.system("python D:\Work_space\Java\Spider_demo\XinLang_news\create_db.py %s"%('post_' + now))
        table_name = 'post_' + now
        #####################################################################################
        for url in (self.start_urls):
            yield scrapy.Request(url,meta={'topic_kws': topic_kws,'table_name':table_name}) 
            
    def parse(self, response):
        topic_kws = response.meta[ 'topic_kws' ]
        table_name = response.meta['table_name']    
              
        sel = Selector(text=response.body, type="html")
        all_content = BeautifulSoup(response.body,'html5lib')
        con_soup1 = all_content.select('item')

        print len(con_soup1)
        item_list = []
        
        for con_soup2 in con_soup1:
            topic_item = Topic_Item() 
            
            
            
            
            