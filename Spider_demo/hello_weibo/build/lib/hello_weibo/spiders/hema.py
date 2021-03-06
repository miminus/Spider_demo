# -*- coding: utf-8 -*-
import re
import time
import urllib

from bs4 import BeautifulSoup
from scrapy import log
import scrapy
from scrapy.http import Request
from scrapy.selector.unified import Selector

import MySQLdb as mdb
from hello_weibo.items import Topic_Item


class HemaSpider(scrapy.Spider):
    name = "hema"
    allowed_domains = ["hebnews.cn"]
    start_urls = [
        'http://bbs.hebnews.cn/search.php?mod=forum&searchid=204&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw=%E9%AB%98%E8%80%83',
        'http://bbs.hebnews.cn/search.php?mod=forum&searchid=206&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw=%E7%AD%94%E6%A1%88',
        'http://bbs.hebnews.cn/search.php?mod=forum&searchid=207&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw=%E4%BD%9C%E5%BC%8A',
        'http://bbs.hebnews.cn/search.php?mod=forum&searchid=208&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw=QQ',
    ]
    def start_requests(self):
        db = mdb.connect(host="127.0.0.1",user="root",passwd="minus",db="yq",charset="utf8" )
        cur=db.cursor()
        cur.execute('select topic_id,topic_keywords from topic where topic_id in (select topic_id from site_topic where site_id=%s)' % self.site_id)
        topic_kws = cur.fetchall()
        for i in self.start_urls:
            yield Request(i,meta={'topic_kws': topic_kws})   #默认 parse()  

    def __init__(self,mailer=None):
        super(HemaSpider,self).__init__()
        log.start('d:/3.log', log.WARNING,logstdout=True)
        self.userid_pa = re.compile('uid-(\d+)')
        self.reply_pattern = re.compile('(\d+).*?(\d+)')
        self.post_time_pa = re.compile('</a>.*?(\d+-\d+-\d+).*?(\d+:\d+)',re.S)
        self.mail=mailer
        self.site_id=33

    def parse(self, response):
        topic_kws = response.meta[ 'topic_kws' ]

        all_content = BeautifulSoup(response.body,'html5lib')
        topic_lists = all_content.find_all('li',class_="pbw")
        for topic in topic_lists:
            topic_item = Topic_Item()
            topic_item['topic_db_message'] = topic_kws
            temp_sel = Selector(text=topic.prettify(), type="html")
            
                        
            title = topic.find_all("a")[0].get_text()
#             print title
            topic_item['topic_title']=title
            
            url = topic.find_all("a")[0].get('href')
            print url
            topic_item['topic_url']=url   
             
            topic_content = topic.find_all("p")[1].get_text()
            print topic_content
            topic_item['topic_content']=topic_content  
            
            post_time = temp_sel.xpath('//p/span/text()')[0].extract().strip()
            print post_time
            topic_item['topic_post_time']=post_time   
            
            author = temp_sel.xpath('//p/span/a/text()')[0].extract().strip()
#             print author
            topic_item['topic_author']=author  

            reply_msg = topic.find_all('p',class_='xg1')[0]
            msg = re.findall(self.reply_pattern,reply_msg.get_text())[0]
            print msg
            reply_num = msg[0]
            read_num = msg[1]
            topic_item['topic_reply']=reply_num    
            
            homepage = temp_sel.xpath('//p/span/a/@href').extract()[0]
            user_id = re.findall(self.userid_pa,homepage)[0]
            print user_id
            topic_item['poster_id']=user_id    
            
            topic_item['homepage'] = homepage 
            
            print '+++++++++++++++++++++++++++++++++++++++++'
            yield  scrapy.Request(url,callback=self.parse_torrent,meta={'topic_item':topic_item})  
            
    def parse_torrent(self,response):    
        topic_item=response.meta['topic_item']
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        topic_item['scratch_time'] = scratch_time        
        topic_item['topic_board']='河马论坛'
        topic_item['site_id']=self.site_id
        topic_item['data_type']=1
        log.msg('MINUS+++++++++++++++++++++++++++++++++++',level=log.WARNING)
        
        topic_item['thread_content'] = response.body
        print response.body
        yield topic_item
