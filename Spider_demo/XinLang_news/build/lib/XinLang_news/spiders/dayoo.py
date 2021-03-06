# -*- coding: utf-8 -*-
#  大洋网  -  搜索类
#  实现了翻页，最大翻页10页
import re
import time, os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
import MySQLdb as mdb
from Sqlite_DB import SqliteTime
from XinLang_news.items import  Topic_Item
from .. import settings

class DayooSpider(scrapy.Spider):
    name = "dayoo"
#     allowed_domains = ["dayoo.com"]
    start_urls = (
        'http://zhannei.baidu.com/cse/search?q=%E5%8C%97%E4%BA%AC&p=0&s=12590748706517226876&sti=1440&nsid=1',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.max_page = 10
        self.site_id=1
        self.time_pa = re.compile(u'(\d+-\d+-\d+)')

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
        con_soup1 = all_content.find_all('div',id='results')[0].find_all('div',class_='result f s0')

        print len(con_soup1)
        item_list = []
        
        for con_soup2 in con_soup1:
            topic_item = Topic_Item()
            
            title = con_soup2.find('a').get_text().strip()
            
            url = con_soup2.find('a').get('href')
            
            content = con_soup2.find('div',class_='c-abstract').get_text().strip().encode('utf-8')
            
            time_con = con_soup2.find('span',class_='c-showurl').get_text()
            post_time = re.findall(self.time_pa,time_con)[0]
            today = '-'.join([ str(i) for i in time.localtime()[:3]])
            if not post_time== today:
                continue
            
            post_time = post_time + ' 00:00:00'
            
            topic_item['topic_url'] = url 
            topic_item['topic_title'] = title
            topic_item['topic_post_time'] = post_time
            topic_item['table_name']=table_name
            topic_item['topic_db_message'] = topic_kws             

            yield scrapy.Request(topic_item['topic_url'],callback=self.parse_torrent,meta={'topic_item':topic_item})
        
        
        #由于显示的就是本日的帖子，所以不用Flag控制
        if self.max_page > 0:
            self.max_page -= 1
            try:    
                nextpage_url = 'http://zhannei.baidu.com/cse/' + all_content.find('a',class_='pager-next-foot n').get('href')
                print nextpage_url
#                 raw_input('**')
                yield scrapy.Request(nextpage_url,meta={'topic_kws': topic_kws,'table_name':table_name}) 
            except IndexError,e:
                return
                print '+++++++++++++++++++++++'
        

    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']
        topic_item['thread_content'] = response.body
        topic_item['scratch_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())            
            
        all_content = BeautifulSoup(response.body,'html5lib')
        topic_content = all_content.find_all('div',id='text_content')[0].get_text().strip()
            
        topic_item['topic_content'] = topic_content  
        topic_item['topic_board']=u'大洋网'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=0  
        
        topic_item['topic_author'] = ''
        topic_item['poster_id'] = 0 
        topic_item['homepage'] =''
        topic_item['poster_image'] = ''
        topic_item['topic_reply'] = 0
        return topic_item  
 
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
        