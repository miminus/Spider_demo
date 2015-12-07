# -*- coding: utf-8 -*-
# 教育中国  - 数据量很少  - 列表类

import re
import time

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy

from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item
import MySQLdb as mdb,os
from .. import settings

class ChinaeduSpider(scrapy.Spider):
    name = "chinaedu"
    allowed_domains = ["china.com.cn"]
    start_urls = (
        'http://edu.china.com.cn/node_7088494.htm',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.site_id = 2
        
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
            yield scrapy.Request(url, meta={'topic_kws':topic_kws,'table_name':table_name})
        

    def parse(self, response):
        topic_kws = response.meta[ 'topic_kws' ]
        table_name = response.meta['table_name'] 
        sel = Selector(text=response.body, type="html")
        all_content = BeautifulSoup(response.body,'html5lib')
        
#         con_soup1 = all_content.find_all('tr',attrs={"class":"red_list"})
        posts = sel.xpath('//div[re:test(@id,"box1")]/div[re:test(@id,"box3")]/ul/li')
        
        for post in posts:
            topic_item = Topic_Item()
            content =  post.extract()
            content = BeautifulSoup(content,'html5lib')
            title = content.find('a').get_text()
#             print title
            
            url = 'http://edu.china.com.cn/' + content.find('a').get('href')
            print url
            
            topic_item['topic_url'] = url 
            topic_item['topic_title'] = title

            yield scrapy.Request(topic_item['topic_url'],callback=self.parse_torrent,meta={'topic_item':topic_item})
            
    def parse_torrent(self,response):
        time_pa = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2})')
        topic_item = response.meta['topic_item']
        
        topic_item['topic_board']=u'教育中国'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=0  
        
        topic_item['topic_author'] = ''
        topic_item['poster_id'] = 0 
        topic_item['homepage'] =''
        topic_item['poster_image'] = ''
        topic_item['topic_reply'] = 0        
        
        all_content = BeautifulSoup(response.body,'html5lib')
        
        topic_item['thread_content'] = response.body
        topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        post_time = re.findall(time_pa,response.body)[0]+':00'
#         print post_time
        
        try:
            paras = all_content.find_all('div',id='fontzoom')[0].find_all('p')
        except IndexError,e:
            paras = all_content.find_all('td',id='fontzoom')[0].find_all('p')
        topic_content = ''
        for para in paras:
            topic_content += para.get_text().strip()
        topic_item['topic_content'] = topic_content          
        
        topic_item['topic_post_time'] = post_time
        print post_time
        if self.sqldb.get_newest_time_item(topic_item) == True:
            print 'go ----'
            yield topic_item

        else:
            print '-----------------'
            

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
            
        
