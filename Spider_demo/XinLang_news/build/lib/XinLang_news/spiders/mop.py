# -*- coding: utf-8 -*-
#  猫扑网 - 最新回复版 - ajax POST方法
#    实现了翻页和最大页设置  - 更改post的页面参数即可

import re
import time, os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy

import MySQLdb as mdb, os
from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item
from .. import settings

class MopSpider(scrapy.Spider):
    name = "mop"
    allowed_domains = ["mop.com"]
    start_urls = (
        'http://dzh.mop.com/ajax/page/subList',
    )
    
    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.post_url = 'http://dzh.mop.com/ajax/page/subList'
        self.formdata = {'mainPlateId':'1','pageIndex':'1','subKind':'2','subPlateId':'0','targetDiv':'newestPostDiv'}
        
        self.Flag_List = []
        self.Maxpage_List = [] 
        self.MAX_PAGE_NUM = 5
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
        for index, url in enumerate(self.start_urls):
            self.Flag_List.append(True)
            self.Maxpage_List.append(self.MAX_PAGE_NUM)      
            yield scrapy.FormRequest(url,
                                    formdata=self.formdata,
                                    callback=self.parse,
                                    method='POST',
                                    meta={'index':index,'topic_kws': topic_kws,'table_name':table_name},
                                    )
    
    def parse(self, response):
        topic_kws = response.meta[ 'topic_kws' ]
        table_name = response.meta['table_name']        
        index = response.meta['index']
        self.Maxpage_List[index] -= 1       
        
        all_content = BeautifulSoup(response.body,'html5lib')
        con_soup1 = all_content.select('ul > li')
        print len(con_soup1)
        item_list = [] 
        for con_soup2 in con_soup1:
            topic_item = Topic_Item()
            
            title = con_soup2.find('a').get_text().strip()
#             print title.encode('utf-8')
            
            url = 'http://dzh.mop.com' + con_soup2.find('a').get('href')
#             print url
            
            author = con_soup2.find_all('div',class_='uname fl ml5')[0].get_text().strip()
            topic_item['topic_author'] = author
            print author
            
            try:
                homepage = con_soup2.find_all('div',class_='info oh mt10')[0].find('a').get('href')
            except AttributeError,e:
                homepage = ''
            topic_item['homepage'] = homepage
            print homepage
            
            
            post_time = con_soup2.find('div',class_='time fl ml20 c999').get_text().strip()
            if len(post_time)  == 10:
                post_time = post_time + ' 00:00:00'
            print post_time
            
            topic_item['topic_url'] = url 
            topic_item['topic_title'] = title
            topic_item['topic_post_time'] = post_time
            topic_item['table_name']=table_name
            topic_item['topic_db_message'] = topic_kws              
            
            item_list.append(topic_item)
        
        res_items = self.sqldb.get_newest_time(item_list)
        for item in res_items:
            yield scrapy.Request(item['topic_url'],callback=self.parse_torrent,meta={'topic_item':item}) 
        if len(item_list) != len(res_items):
            self.Flag_List[index] = False 
        
        if self.Flag_List[index] and self.Maxpage_List[index]>0:
            self.formdata['pageIndex'] = str(self.MAX_PAGE_NUM - self.Maxpage_List[index]+1) 
            yield scrapy.FormRequest(self.post_url,
                                        formdata=self.formdata,
                                        callback=self.parse,
                                        method='POST',
                                        meta={'topic_kws': topic_kws,'table_name':table_name,'index':index},
                                        )   
            raw_input('--') 
            
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        topic_item['thread_content'] = response.body
        topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())            
            
        all_content = BeautifulSoup(response.body,'html5lib')
        topic_content = all_content.find_all('div',class_='article-cont p20 c666')[0].get_text().strip()
        topic_item['topic_content'] = topic_content   
        topic_item['topic_board']=u'猫扑'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=0  
        topic_item['poster_id'] = 0 
        topic_item['poster_image'] = ''
        topic_item['topic_reply'] = 0
        yield topic_item 
 
    @classmethod   
    def from_crawler(cls,crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        crawler.signals.connect(spider.spider_closed,signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        return spider
        
    def spider_closed(self,spider):
        self.sqldb.insert_new_time()   
     
     
        
    def spider_opened(self,spider):
        self.sqldb = SqliteTime(spider.name)      

       