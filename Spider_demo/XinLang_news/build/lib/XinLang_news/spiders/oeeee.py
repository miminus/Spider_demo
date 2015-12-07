# -*- coding: utf-8 -*-
#  南都网 - 及时发、国内版
#   没有数据  - 没有翻页
import re
import time, os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import json
import MySQLdb as mdb, os
from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item
import unicode_normal
from .. import settings

class OeeeeSpider(scrapy.Spider):
    name = "oeeee"
    allowed_domains = ["oeeee.com"]
    start_urls = (
        'http://news.oeeee.com/api/channel.php?m=Js4channelNews&a=latest&cid=226&page=1&row=100&callback=newsMoreTpl&_=1446800676985',
        'http://news.oeeee.com/api/channel.php?m=Js4channelNews&a=latest&cid=164&page=1&row=100&callback=newsMoreTpl&_=1446803641895',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.dict_pa = re.compile('{.*?}',re.S)
        self.site_id = 4
        
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
            yield scrapy.Request(url,meta={'topic_kws': topic_kws,'table_name':table_name})           

    def parse(self, response):
        topic_kws = response.meta[ 'topic_kws' ]
        table_name = response.meta['table_name']  
        
        all_content = unicode_normal.main_get(response.body.encode('utf-8','ignore'))
        
#         json_content = json.loads(all_content.strip()[13:-3])
        dicts_str = all_content.strip()[13:-3]
#         with open('d:/1.txt','wb') as f:
#             f.write(all_content.strip()[13:-3])
        dicts = re.findall(self.dict_pa,dicts_str)
        
        item_list = []
        for dict in dicts:
            topic_item = Topic_Item()
            try:
                dd = json.loads(dict)
            except:
                print dict
                raw_input()
                continue
            topic_item['topic_url'] = dd['linkurl'] 
            topic_item['topic_title'] = dd['title']
            topic_item['topic_post_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(dd['time'])))  
            print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(dd['time'])))
            
            
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
        topic_content = all_content.find_all('div',class_='content content2')[0].get_text().strip()
        topic_item['topic_content'] = topic_content     
        topic_item['topic_board']=u'南都网'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=0  
        
        topic_item['topic_author'] = ''
        topic_item['poster_id'] = 0 
        topic_item['homepage'] =''
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
