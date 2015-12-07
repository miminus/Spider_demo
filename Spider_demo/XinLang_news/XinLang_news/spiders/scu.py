# -*- coding: utf-8 -*-
#    四川大学网
#    实现了翻页和最大页设置  - 采用拼凑url
import re
import time, os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import MySQLdb as mdb, os
from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item
from .. import settings

class ScuSpider(scrapy.Spider):
    name = "scu"
    allowed_domains = ["scu.edu.cn"]
    start_urls = (
#         'http://news.scu.edu.cn/news2012/ztxw/rcpy/I020201index_1.htm',
        'http://news.scu.edu.cn/news2012/cdzx/I0201index_1.htm',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
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
            yield scrapy.Request(url,meta={'index':index,'topic_kws': topic_kws,'table_name':table_name}) 
        
    def parse(self, response):
        topic_kws = response.meta[ 'topic_kws' ]
        table_name = response.meta['table_name']          
        index = response.meta['index']
        self.Maxpage_List[index] -= 1 
        
        sel = Selector(text=response.body, type="html")
        all_content = BeautifulSoup(response.body,'html5lib')
#         con_soup1 = all_content.find_all('table',attrs={"class":"pcenter_t19"})[0].find_all('ul')
        con_soup1 = all_content.select('.pcenter_t19 table table')[1:]
        print len(con_soup1)
        item_list = []
        for con_soup2 in con_soup1:
            topic_item = Topic_Item()
            title = con_soup2.find('a').get_text().strip()
            print title.encode('utf-8')
            
            url = 'http://news.scu.edu.cn' + con_soup2.find('a').get('href')
            print url
            
            post_time = con_soup2.find('font').get_text().strip()[1:-1] + ' 00:00:00'
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
            new_page = 'index_' + str(self.MAX_PAGE_NUM-self.Maxpage_List[index]+1) 
            nextpage_url = re.sub('index_\d+', new_page,response.url)
            print nextpage_url
#             raw_input('--')
            yield scrapy.Request(nextpage_url,meta={'topic_kws': topic_kws,'table_name':table_name,'index':index})          
            
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        topic_item['thread_content'] = response.body
        topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())            
            
        all_content = BeautifulSoup(response.body,'html5lib')
        topic_content = all_content.find_all('div',id='BodyLabel')[0].get_text().strip()
            
        topic_item['topic_content'] = topic_content   
        topic_item['topic_board']=u'四川大学主页'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=0  
        
        topic_item['topic_author'] = ''
        topic_item['poster_id'] = 0 
        topic_item['homepage'] =''
        topic_item['poster_image'] = ''
        topic_item['topic_reply'] = 0
        print 'got one' 
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
                
                
                
