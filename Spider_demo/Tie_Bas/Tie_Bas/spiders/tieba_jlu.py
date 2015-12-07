# -*- coding: utf-8 -*-
#   吉林大学贴吧-  解析different
#   实现了翻页功能
import re
import time,os

from bs4 import BeautifulSoup
from scrapy import Selector, signals
import scrapy
from Sqlite_DB import SqliteTime
from Tie_Bas.items import  Topic_Item
import MySQLdb as mdb

class TiebaJluSpider(scrapy.Spider):
    name = "tieba_jlu"
    allowed_domains = ["baidu.com"]
    start_urls = (
        'http://tieba.baidu.com/f?ie=utf-8&kw=%E5%90%89%E6%9E%97%E5%A4%A7%E5%AD%A6',
    )

    def __init__(self, *args, **kwargs):
        super(scrapy.Spider,self).__init__(*args, **kwargs)
        self.dig_pattern = re.compile('(\d+)')
        self.postid_pattern = re.compile('/p/(\d{10})')
        self.site_id=322
        self.Flag_List = []
        self.Maxpage_List = [] 
        self.MAX_PAGE_NUM = 10

    def start_requests(self):
        db = mdb.connect(host="127.0.0.1",user="root",passwd="minus",db="yuqing",charset="utf8" )
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
        topic_lists = sel.xpath('//li[re:test(@class,"^\s*j_thread_list clearfix")]')
#         topic_lists = sel.xpath('//li[contains(@class,"j_thread_list clearfix")]')
        print len(topic_lists)
        item_list = []
        for topic in topic_lists:
            topic_item = Topic_Item()
            temp_sel = Selector(text=topic.extract())
            try:
                reply_num = temp_sel.xpath('//div[re:test(@class,"threadlist_rep_num.*?")]/text()').extract()[0]
            except IndexError,e:
                reply_num = temp_sel.xpath('//span[re:test(@class,"threadlist_rep_num.*?")]/text()').extract()[0]
            print reply_num
            topic_item['topic_reply']=reply_num
            
            title = temp_sel.xpath('//a[re:test(@class,"j_th_tit")]/text()').extract()[0]
            topic_item['topic_title']=title
            
            try:
                con = temp_sel.xpath('//div[re:test(@class,"threadlist_abs threadlist_abs_onlyline")]/text()').extract()[0]
            except IndexError,e:
                con=''    
            topic_item['topic_content']=con
            
             
            author = temp_sel.xpath('//span[re:test(@class,"tb_icon_author\s*")]/a[re:test(@class,"j_user_card\s*")]/text()').extract()[0]
            print author
            topic_item['topic_author'] = author
            
            try:
                post_time = temp_sel.xpath('//span[re:test(@class,"threadlist_reply_date j_reply_data")]/text()').extract()[0]
            except IndexError,e:
                post_time = temp_sel.xpath('//span[re:test(@class,"threadlist_reply_date pull_right j_reply_data")]/text()').extract()[0]
            if ':' in post_time:
                today = time.strftime('%Y-%m-%d',time.localtime())
                post_time = today+' '+post_time.strip()+":00"
            elif '-' in post_time:
                post_time = str(time.localtime().tm_year) + '-' + post_time.strip() + ' 00:00:00'
            topic_item['topic_post_time'] = post_time

            author_id = temp_sel.xpath('//span[re:test(@class,"tb_icon_author\s*")]/@data-field').extract()[0]
            author_id = re.findall(self.dig_pattern,author_id)[0]
#             print author_id
            topic_item['poster_id'] = author_id

            thread_url = temp_sel.xpath('//a[re:test(@class,"j_th_tit")]/@href').extract()[0]
            domain = 'http://tieba.baidu.com'
            thread_url = domain+thread_url
            print thread_url
            topic_item['topic_url'] = thread_url
            topic_item['topic_db_message'] = topic_kws
            item_list.append(topic_item)
            
        res_items = self.sqldb.get_newest_time(item_list)
        for item in res_items:
            yield scrapy.Request(item['topic_url'],callback=self.parse_torrent,meta={'topic_item':item})    
            
        if len(item_list) != len(res_items):
            self.Flag_List[index] = False             
            
        if self.Flag_List[index] and self.Maxpage_List[index]>0:
            nextpage_url = self.start_urls[0] + '&ie=utf-8&pn=' + str((self.MAX_PAGE_NUM - self.Maxpage_List[index])*50)
            '''
            try:
                nextpage_url = all_content.find_all("a", class_=re.compile('next'))[0].get('href')
            except IndexError,e:
                nextpage_url = all_content.find_all("a", class_=re.compile('next.*?'))[0].get('href')
            if 'http:' not in nextpage_url:
                nextpage_url = 'http://tieba.baidu.com'+nextpage_url
            '''
            print nextpage_url
            raw_input('--')
            yield scrapy.Request(nextpage_url,meta={'index':index,'topic_kws': topic_kws,'table_name':table_name})   
            
    def parse_torrent(self,response):
        topic_item = response.meta['topic_item']

        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time
        topic_item['topic_board']=u'吉林大学贴吧'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=3

        topic_item['thread_content'] = response.body
        
        sel = Selector(text=response.body, type="html")
        try:
            poster_homepage = sel.xpath('//li[re:test(@class,"d_name")]/a/@href').extract()[0]
        except:
            return
        poster_homepage = 'http://tieba.baidu.com'+poster_homepage
        topic_item['homepage'] = poster_homepage
        
        poster_image = sel.xpath('//a[re:test(@class,"p_author_face\s*")]/img/@src').extract()[0]
        topic_item['poster_image']=poster_image
        
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


