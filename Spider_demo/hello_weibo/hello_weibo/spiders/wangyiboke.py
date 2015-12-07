# -*- coding: utf-8 -*-
import datetime
import re
import time
import urllib

import scrapy
from scrapy.selector.unified import Selector

import MySQLdb as mdb
from hello_weibo.items import Topic_Item


class WangyibokeSpider(scrapy.Spider):
    name = "wangyiboke"
#     allowed_domains = ["yodao.com"]
    start_urls = (
        'http://www.yodao.com/',
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
                    page_num = page*10
                    search_url = 'http://news.yodao.com/search?q='+wd_code+'&start='+str(page_num)+'&length=10&s=pdate&tl&tr=no_range&keyfrom=search.page'
                    print search_url
                    yield scrapy.FormRequest(search_url,meta={'topic_id': topic_id})

    def __init__(self,mailer=None):
        super(WangyibokeSpider,self).__init__()
        self.dig_pattern = re.compile('(\d+)')
        self.time_2_pa = re.compile('(\d+).*?')
        self.time_1_pa = re.compile('(\d+).*?(\d+).*?(\d+)')
        self.postid_pattern = re.compile('/p/(\d{10})')
        self.post_time_pa = re.compile('</a>.*?(\d+-\d+-\d+).*?(\d+:\d+)',re.S)
        self.mail=mailer
        self.page_all=3
        self.site_id= 35
        
    def parse_html_content(self,str):
        sub_p_1 = re.compile('<[^<>]*?>|\r', re.S)
        str = re.sub(sub_p_1, '', str)    
        ustr = str
        return ustr        
        
    def parse(self, response):
        topic_id = response.meta[ 'topic_id' ]
        sel = Selector(text=response.body, type="html")
        print 'starting'
        topic_lists = sel.xpath('//ul[re:test(@id,"results")]/li')
        for topic in topic_lists:
            topic_item = Topic_Item()
            temp_sel = Selector(text=topic.extract())
            topic_item['topic_id'] = topic_id
    
            title = temp_sel.xpath('//h3/a')[0].extract()
            title = self.parse_html_content(title)
            print title
            topic_item['topic_title']=title
            
            content = temp_sel.xpath('//p')[0].extract()
            content = self.parse_html_content(content).strip()
            print type(content)
            print content.encode('gbk','ignore')
            topic_item['topic_content']=content
    
            ttime = temp_sel.xpath('//span[re:test(@class,"green stat")]/text()').extract()[0]
            tt = ttime.split()[1].__repr__()
            print tt
            now = datetime.datetime.now()
            if '5e74' in tt:
                time_pa = re.findall(self.time_1_pa,ttime.split()[1])[0]
                new_time = str(time_pa[0])+'-'+str(time_pa[1])+'-'+str(time_pa[2])+' '+'00:00:00'
                print time_pa
            elif '5206' in tt:
                time_pa = re.findall(self.time_2_pa,ttime.split()[1])[0]
                new_time = now - datetime.timedelta(minutes=int(time_pa))
                print time_pa
            elif '5c0f' in tt:
                time_pa = re.findall(self.time_2_pa,ttime.split()[1])[0]
                new_time = now - datetime.timedelta(hours=int(time_pa))
                print time_pa
            print new_time    
            topic_item['topic_post_time']= new_time  
            poster =  ttime.split()[0]
            topic_item['topic_author'] = poster
            
            url = temp_sel.xpath('//h3/a/@href').extract()[0]
            print url
            topic_item['topic_url']=url
            yield  scrapy.Request(url,callback=self.parse_torrent,meta={'topic_item':topic_item})            
            

            print '++++++++++++++++++++++++++++++'
    def parse_torrent(self,response):    
        topic_item=response.meta['topic_item']
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time        
        topic_item['topic_board']='网易博客'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=1
        
        topic_item['thread_content'] = response.body
        yield topic_item
