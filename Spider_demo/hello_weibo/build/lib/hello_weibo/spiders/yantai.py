# -*- coding: utf-8 -*-
import re
import time
import urllib

import scrapy
from scrapy.selector.unified import Selector

import MySQLdb as mdb
from hello_weibo.items import Topic_Item

class YantaiSpider(scrapy.Spider):
    name = "yantai"
#     allowed_domains = ["baidu.com"]
    
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
                    search_url = 'http://zhannei.baidu.com/cse/search?q='+wd_code+'&p='+str(page_num)+'&s=4181236417596806577&srt=cse_createTime&nsid=0'
                    yield scrapy.FormRequest(search_url,meta={'topic_id': topic_id})    

    def __init__(self,mailer=None):
        super(YantaiSpider,self).__init__()
        self.dig_pattern = re.compile('(\d+)')
        self.postid_pattern = re.compile('/p/(\d{10})')
        self.post_pa = re.compile('(\d+-\d+-\d+)')
        self.post_time_pa = re.compile('</a>.*?(\d+-\d+-\d+).*?(\d+:\d+)',re.S)
        self.mail=mailer
        self.page_all=3
        self.site_id=34

    def parse(self, response):
        topic_id = response.meta[ 'topic_id' ]
        sel = Selector(text=response.body, type="html")
        
        topic_lists = sel.xpath('//div[re:test(@class,"result f s3")]')
        for topic in topic_lists:
            topic_item = Topic_Item()
            temp_sel = Selector(text=topic.extract())
        
            title = temp_sel.xpath('//h3[re:test(@class,"c-title")]/a/text()').extract()[0].strip()
#             print title
            topic_item['topic_title']=title
            
            content = temp_sel.xpath('//div[re:test(@class,"c-abstract")]/text()').extract()[0].strip()
            print content
            topic_item['topic_content']=content
            
            post_time = temp_sel.xpath('//div[re:test(@class,"c-summary-1")]/span')[2].extract()
            post_time = re.findall(self.post_pa,post_time)[0]+' 00:00:00'
            print post_time
            topic_item['topic_post_time']=post_time
            
            author = temp_sel.xpath('//div[re:test(@class,"c-summary-1")]/span/text()')[1].extract()
            print author
            topic_item['topic_author']=author
            
            url = temp_sel.xpath('//h3[re:test(@class,"c-title")]/a/@href').extract()[0]
            print url
            topic_item['topic_url']=url
            topic_item['topic_reply']=0
            
            print '+++++++++++++++++++++++++++++++++++++'
            yield  scrapy.Request(url,callback=self.parse_torrent,meta={'topic_item':topic_item})  
            
    def parse_torrent(self,response):    
        topic_item=response.meta['topic_item']
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time        
        topic_item['topic_board']='烟台论坛'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=1
        
        topic_item['thread_content'] = response.body
        print response.body
        yield topic_item
            
