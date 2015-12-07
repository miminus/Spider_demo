# -*- coding: utf-8 -*-
#  香港科技大学网   -  列表类
#  只有一页，所以不用翻页
import time,os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import MySQLdb as mdb
from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item
from .. import settings

class CuhkSpider(scrapy.Spider):
    name = "cuhk"
    allowed_domains = ["cuhk.edu.hk"]
    start_urls = (
        'http://www.cpr.cuhk.edu.hk/tc/press.php',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.num = {u'一':1,u'二':2,u'三':3,u'四':4,u'五':5,u'六':6,u'七':7,u'八':8,u'九':9,u'零':0,u'十':10}
        self.site_id = 3

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

    def chinese_to_digit(self,str):
        form = 1
        mon_ = 1
        for index,i in enumerate(str):
            if len(str) == 1:
                mon_ = self.num[i]
                break
            if index == 0:
                if i != u'十':
                   form = self.num[i]
                else:
                    mon_ = form*10
            else:
                if i != u'十':
                    mon_ += self.num[i]
                else:
                    mon_ = form*10  
        return mon_    

    def parse(self, response):
        topic_kws = response.meta[ 'topic_kws' ]
        table_name = response.meta['table_name'] 
                
        sel = Selector(text=response.body, type="html")
        all_content = BeautifulSoup(response.body,'html5lib')
        con_soup1 = all_content.select('#list_column')[0].find_all('div',class_='date_text')
        con_soup2 = all_content.select('#list_column')[0].find_all('div',class_='list_item')
        print len(con_soup1),len(con_soup2)
        item_list = []
        
        for index in range(len(con_soup1)):
            topic_item = Topic_Item()
            
            title = con_soup2[index].find('a').get_text().encode('utf-8')
            print title
            
            url = 'http://www.cpr.cuhk.edu.hk/tc/' + con_soup2[index].find('a').get('href')
            print url
             
            post_time = con_soup1[index].get_text()
            print post_time
            post_time_ = []
            index1 = post_time.find('年')
            index2 = post_time.find('月')
            index3 = post_time.find('日')
            year =  post_time[:index1]
            mon =  post_time[index1+1:index2]
            day =  post_time[index2+1:index3]
            year__ = ''
            for i in year:
                year__ += str(self.num[i])
            post_time_.append(str(year__))  
             
            mon_ = self.chinese_to_digit(mon)
            post_time_.append(str(mon_))   
            
            day_ = self.chinese_to_digit(day)
            post_time_.append(str(day_))  
            
            post_time =  '-'.join(post_time_) + ' 00:00:00'
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
            
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        topic_item['thread_content'] = response.body
        topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())   
        
        topic_item['topic_author'] = ''
        topic_item['poster_id'] = 0 
        topic_item['homepage'] =''
        topic_item['poster_image'] = ''
        topic_item['topic_reply'] = 0
            
        all_content = BeautifulSoup(response.body,'html5lib')
        topic_content = all_content.find_all('div',class_='press_detail_text')[0].get_text().strip()
            
        topic_item['topic_content'] = topic_content   
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
            
            
            
            
            
             