# -*- coding: utf-8 -*-
#    文汇报 - 没有翻页
import re
import time

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import MySQLdb as mdb, os
from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item
from .. import settings

class News365Spider(scrapy.Spider):
    name = "news365"
    allowed_domains = ["news365.com.cn"]
    start_urls = (
        'http://whb.news365.com.cn/whshx/',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.pa = re.compile('(<a.*?<br/>)',re.S)
        self.time_pa = re.compile('(\d{4}-\d{2}-\d{2})')
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
        all_content = BeautifulSoup(response.body,'html5lib')
        
        con_soup1 = all_content.find_all("td", class_="nieislie")[0]
        ori_con = con_soup1.prettify()
        posts_list = re.findall(self.pa, ori_con)
        item_list = []
        for post in posts_list:
            topic_item = Topic_Item()
            con_soup2 = BeautifulSoup(post,'html5lib')
            title = con_soup2.find('a').get_text().strip()
            url = 'http://whb.news365.com.cn/whshx'+  con_soup2.find('a').get('href')[1:]
            post_time =  re.findall(self.time_pa,post)[0] + ' 00:00:00'
            topic_item['topic_url'] = url 
            topic_item['topic_title'] = title
            topic_item['topic_post_time'] = post_time
            
            print title,url,post_time
            topic_item['table_name']=table_name
            topic_item['topic_db_message'] = topic_kws              
            item_list.append(topic_item)
        
        res_items = self.sqldb.get_newest_time(item_list)
        for item in res_items:
            yield scrapy.Request(item['topic_url'],callback=self.parse_torrent,meta={'topic_item':item})
        
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        topic_item['thread_content'] = response.body
        topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        
        all_content = BeautifulSoup(response.body,'html5lib')
        paras = all_content.find_all('p')
        topic_content = ''
        for para in paras:
            topic_content += para.get_text().strip()
            
        topic_item['topic_content'] = topic_content   
        topic_item['topic_board']=u'文汇报'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=0  
        topic_item['poster_id'] = 0 
        topic_item['poster_image'] = '' 
        topic_item['topic_reply'] = 0
        topic_item['topic_author'] = ''
        topic_item['homepage'] =''        
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