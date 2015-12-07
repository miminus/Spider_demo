# -*- coding: utf-8 -*-
import datetime
import re
import time
import urllib

import scrapy
from scrapy.selector.unified import Selector

import MySQLdb as mdb
from hello_weibo.items import Topic_Item


class MoshouSpider(scrapy.Spider):
    name = "moshou"
    allowed_domains = ["battlenet.com.cn"]
    start_urls = (
        'http://www.battlenet.com.cn/',
    )

    def start_requests(self):
        db = mdb.connect(host="127.0.0.1",user="root",passwd="minus",db="yq",charset="utf8" )
        cur=db.cursor()
        cur.execute('select topic_id,topic_keywords from topic where topic_id in (select topic_id from site_topic where site_id=%d)' % self.site_id)
        topic_kws = cur.fetchall()
        for topic_kw in topic_kws:
            topic_id = topic_kw[0]
            kws = topic_kw[1]
            kws_list = kws.split(',')
            for kw in kws_list:
                wd_code = urllib.quote(kw.encode('utf-8'))
                for page in xrange(self.page_all):
                    page_num = page*1
                    search_url = 'http://www.battlenet.com.cn/wow/zh/search?f=post&sort=time&dir=d&q='+wd_code+'&page='+str(page_num)
                    yield scrapy.FormRequest(search_url,meta={'topic_id': topic_id})

    def __init__(self,mailer=None):
        super(MoshouSpider,self).__init__()
        self.dig_pattern = re.compile('(\d+)')
        self.postid_pattern = re.compile('/p/(\d{10})')
        self.post_time_pa = re.compile('</a>.*?(\d+-\d+-\d+) (.*?)(\d+:\d+)',re.S)
        self.mail=mailer
        self.page_all=3
        self.site_id=18

    def time_to_datetime(self,_time):  #time must be the type of struct_time 
        new_datetime=datetime.datetime(_time[0],_time[1],_time[2],_time[3],_time[4],_time[5])  #参数是年月日（h m s）等数字参数 
        return new_datetime

    def parse(self, response):
        topic_id = response.meta[ 'topic_id' ]
        sel = Selector(text=response.body, type="html")
        
        topic_lists = sel.xpath('//div[re:test(@class,"result.*?")]')
        for topic in topic_lists:
            topic_item = Topic_Item()
            temp_sel = Selector(text=topic.extract())
            
            title = temp_sel.xpath('//h3[re:test(@class,"subheader-3")]/a/text()')[0].extract()
            print title
            topic_item['topic_title']=title
            
            board = temp_sel.xpath('//div[re:test(@class,"meta")]/a/text()')[0].extract()
            print board
            poster = temp_sel.xpath('//div[re:test(@class,"meta")]/a/text()')[1].extract().strip()
            print poster
            topic_item['topic_author']=poster
            
            main_con = temp_sel.xpath('//div[re:test(@class,"meta")]')[0].extract().strip()
            post_time_ = re.findall(self.post_time_pa,main_con)[0]
            post_time_str = '20'+post_time_[0]+' '+post_time_[2]+':00'
            post_time = time.strptime(post_time_str, '%Y-%m-%d %H:%M:%S')
#             print post_time
            
            if '4e0b' in post_time_[1].__repr__():
                print u'下午'
                post_time = self.time_to_datetime(post_time)+ datetime.timedelta(hours=12)
            elif '4e0a' in post_time_[1].__repr__():
                print u'上午'
                post_time = post_time_str
            
            print post_time
            topic_item['topic_post_time']=post_time
            
            content = temp_sel.xpath('//div[re:test(@class,"content")]/text()')[0].extract().strip()
            print content
            topic_item['topic_content']=content
            
            url = temp_sel.xpath('//h3[re:test(@class,"subheader-3")]/a/@href').extract()[0]
            url = 'http://www.battlenet.com.cn'+url
            print url
            topic_item['topic_url']=url
            
            reply_num = temp_sel.xpath('//h3[re:test(@class,"subheader-3")]/span[re:test(@class,"small")]/text()').extract()
            reply_num = reply_num[len(reply_num)-1]
            reply_num = re.findall(self.dig_pattern,reply_num)[0]
            print reply_num
            topic_item['topic_reply']=reply_num
            
            print '+++++++++++++++++++++++++++++++++++++'
            yield  scrapy.Request(url,callback=self.parse_torrent,meta={'topic_item':topic_item})  
            
    def parse_torrent(self,response):    
        topic_item=response.meta['topic_item']
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time        
        topic_item['topic_board']='魔兽世界'
        topic_item['site_id']=18
        topic_item['data_type']=1
        
        topic_item['thread_content'] = response.body
        print response.body
        yield topic_item
