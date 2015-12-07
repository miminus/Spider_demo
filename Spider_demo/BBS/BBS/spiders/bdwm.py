# -*- coding: utf-8 -*-
#  北大未名  -  全 站 十 大 话 题 （一天内）
#  无翻页
import re
import time, os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import MySQLdb as mdb
from BBS.items import  Topic_Item
from .. import settings

class BdwmSpider(scrapy.Spider):
    name = "bdwm"
    allowed_domains = ["bdwm.net"]
    start_urls = (
        'http://www.bdwm.net/bbs/ListPostTops.php?halfLife=180',
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
        con_soup1 = all_content.select('tr')[1:]

        print len(con_soup1)
        item_list = []
        
        for con_soup2 in con_soup1:
            topic_item = Topic_Item()   
            print len(con_soup2.select('td'))      
            
            board = con_soup2.select('td')[2].get_text()    
            print board
            
            author = con_soup2.select('td')[4].get_text()
            print author
            
            time_ori = con_soup2.select('td')[5].get_text().strip()
            post_time = str(time.localtime().tm_year) + '-' + time_ori
            print post_time
            
            title = con_soup2.select('td')[6].find('a').get_text().strip()
            print title
            
            url = 'http://www.bdwm.net/bbs/' + con_soup2.select('td')[6].find('a').get('href')
            print url
            
            topic_item['topic_url'] = url 
            topic_item['topic_title'] = title
            topic_item['topic_post_time'] = post_time
            topic_item['table_name']=table_name
            topic_item['topic_db_message'] = topic_kws  
            topic_item['topic_author'] = author 
            
            yield scrapy.Request(topic_item['topic_url'],callback=self.parse_torrent,meta={'topic_item':topic_item})
            
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        topic_item['thread_content'] = response.body
        topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())            
            
        topic_item['topic_board']=u'北大未名'
        topic_item['topic_content'] = ''
        topic_item['site_id']=self.site_id
        topic_item['data_type']=0  
        topic_item['poster_id'] = 0 
        topic_item['homepage'] =''
        topic_item['poster_image'] = ''
        topic_item['topic_reply'] = 0
        return topic_item  
            
            
            
            