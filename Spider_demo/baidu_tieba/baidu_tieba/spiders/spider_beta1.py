#coding:utf-8
'''
Created on 2015/4/20

@author: MINUS
'''
import re
import time

from reportlab.lib.randomtext import subjects
from scrapy import Selector, responsetypes
from scrapy import log, signals
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import DropItem
from scrapy.mail import MailSender


from baidu_tieba.items import Thread_url_Item, MyItem
from scrapy.contrib import spiderstate
from scrapy.http import Request


class DmozSpider(CrawlSpider):
    name = "dd"
    allowed_domains = ["tieba.baidu.com"]
    
    start_urls = [
            'http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=0',
            'http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=50',
            'http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=150',
            'http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=200'
    ]
    def start_requests(self):
#         url = 'http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=0'
        llist = []
        for i in self.start_urls:
            yield Request(i,meta={'minus': "minus"})   #默认 parse()
#             yield (self.make_requests_from_url(i))
            
   
    '''
    def start_requests(self):
        return [scrapy.FormRequest('http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=0',callback=self.put_body),
                    scrapy.FormRequest('http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=50',callback=self.put_body),
                    scrapy.FormRequest('http://tieba.baidu.com/f?kw=%E5%BF%83%E7%90%86%E5%AD%A6&ie=utf-8&pn=150',callback=self.put_body)]
    
    def put_body(self,response):
        print response.body
        print response.url
        raw_input()
    '''   
        
    
#     rules = [Rule(SgmlLinkExtractor(allow=['/p/\d{10}\Z']), 'parse_torrent'),
#              ]
  
    def __init__(self,mailer):
        super(DmozSpider,self).__init__()
        self.dig_pattern = re.compile('(\d+)')
        self.postid_pattern = re.compile('/p/(\d{10})')
        self.mail=mailer
    
    def parse_html_content(self,str):
        sub_p_1 = re.compile('<[^<>]*?>|\r', re.S)
        str = re.sub(sub_p_1, '', str)    
        ustr = str
        return ustr
    
    def parse(self,response):
        mmm = response.meta[ 'minus' ]
        print mmm
        raw_input('minus:')
        for link in  SgmlLinkExtractor(allow=['/p/\d{10}\Z']).extract_links(response):
            yield scrapy.Request(link.url,callback=self.parse_torrent,meta={'minus': mmm})
    
    def parse_torrent(self,response):
        mmm = response.meta[ 'minus' ]
        print mmm
        print '+++++++++++++++++++++++++++++++++++++++'
        print 'Url : '+response.url
        sel = Selector(text=response.body, type="html")
        title = sel.xpath('//h1[re:test(@class,"core_title_txt")]/text()').extract() 
        print 'Topic : '+title[0]
        
        
        
        ####################################################################################################
        item_url = Thread_url_Item()
        item_url['thread_url']=response.url
        
        ####################################################################################################
        post_id = re.findall(self.postid_pattern,response.url)[0]
        item_url['thread_id'] = post_id
        
        ####################################################################################################
        scratch_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        item_url['scratch_time'] = scratch_time
        
        ##############################获取其他页面的url####################################################
        '''
        for link in  SgmlLinkExtractor(allow=['/p/\d{10}\?pn=\d+'],deny=['/p/\d{10}\?pn=1']).extract_links(response):
            yield scrapy.Request(link.url,callback=self.parse_torrent)
        '''   
        ####################################################################################################
        post_time = sel.xpath('//div[re:test(@class,"core_reply_tail\s*")]/ul/li/text()').extract()[0]
#         print post_time
        item_url['thread_post_time'] = post_time
        
        #####################################################################################################
        poster = sel.xpath('//a[re:test(@class,"p_author_name j_user_card")]/text()').extract()[0]
#         print poster
        item_url['thread_poster'] = poster
        
        #####################################################################################################
        reply = sel.xpath('//span[re:test(@class,"red")]/text()').extract()[0]
#         print reply
        item_url['thread_reply'] = reply
        
        #####################################################################################################
        title = sel.xpath('//head/title/text()').extract()[0]
#         print title
        item_url['thread_title']=title
        
        #####################################################################################################
        poster_image = sel.xpath('//a[re:test(@class,"p_author_face\s*")]/img/@src').extract()[0]
#         print poster_image
        item_url['thread_poster_image']=poster_image
        
        #####################################################################################################
        poster_id = sel.xpath('//li[re:test(@class,"^d_name$")]/@data-field').extract()[0]
        poster_id = re.findall(self.dig_pattern,poster_id)[0]
#         print poster_id
        item_url['thread_poster_id']=poster_id
        
        #####################################################################################################
        poster_homepage = sel.xpath('//a[re:test(@class,"p_author_face\s*")]/@href').extract()[0]
        poster_homepage = 'http://tieba.baidu.com'+poster_homepage
        item_url['thread_poster_homepage'] = poster_homepage
                                                                                                    
        
        #####################################################################################################
        
        url_all_list=sel.xpath('//div[re:test(@id, "post_content_\d+")]').extract()  
        pic_pattern = re.compile('src="(http://.*?)"')
        
        content=''
        pictures = ''
        pic_list= []
        for i,content in enumerate(url_all_list):
            item = MyItem()
#             print '-------------------------------the  '+ str(i+1) +'th  floor-----------------------------------'
            pics = re.findall(pic_pattern,content)
            con_item = self.parse_html_content(content.encode('utf-8','ignore')).strip()
            pic_list+=pics
            item['image_urls']=pics
            pictures+=','.join(pics)
            content+=con_item
        item_url['image_urls']= pic_list   
        item_url['thread_content']=content 
        item_url['thread_images'] = pictures
        
        
         
        return item_url
    
    @classmethod
    def from_crawler(cls,crawler): 
        mailer = MailSender.from_settings(crawler.settings)
        spider = cls(mailer)
        crawler.signals.connect(spider.spider_closed,signals.spider_closed)
        crawler.signals.connect(spider.spider_error,signals.spider_error)
        return spider
        
    def spider_closed(self,spider):   
        return self.mail.send(to=['1624727417@qq.com'],subject='scrapy_baidu_tieba',body='<h1>the spider is over </h1>',cc=[])      
    
    def spider_error(self,spider):
        return self.mail.send(to=['1624727417@qq.com'],subject='scrapy_baidu_tieba',body='<h1>the spider is error </h1>',cc=[])  
    
    
    
    