# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
import sqlite3
import time
from scrapy import log

import MySQLdb.cursors
import scrapy
from scrapy.contrib import spiderstate
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi


class YulinPipeline(object):
    def process_item(self, item, spider):
        return item

class MyImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        image_name_pa = re.compile('(.*?(\.png|\.jpg))')
        url = request.url
        image_guid = url.split('/')[-1]
        image_guid = re.findall(image_name_pa,image_guid)[0]
        return 'full_/%s' % (image_guid) 

    def thumb_path(self, request, thumb_id, response=None, info=None):
        image_name_pa = re.compile('(.*?(\.png|\.jpg))')
        url = request.url
        image_guid = url.split('/')[-1]
        image_guid = re.findall(image_name_pa,image_guid)[0]
        return 'thumbs_/%s/%s' % (thumb_id,image_guid)
               
    
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item     

class Mysql_scrapy_pipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
                                    dbapiName='MySQLdb',
                                    host='127.0.0.1',
                                    db='yq',
                                    user='root',
                                    passwd='minus',
                                    cursorclass= MySQLdb.cursors.DictCursor,
                                    charset = 'utf8',
                                    use_unicode = False
                                    )

    def open_spider(self, spider):
        self.ids_seen = set()
        self.sx = sqlite3.connect("E:/test.db") 
        self.cu = self.sx.cursor() 
        try:
            self.cu.execute("CREATE TABLE history (time TEXT,result TEXT,spider_name TEXT)")
            last_time="2015-1-1 00:00:00"
        except:
            try:
                self.cu.execute('SELECT time FROM history where spider_name="'+spider.name+'"')
                last_time = self.cu.fetchone()[0]
                log.msg('************* '+last_time,level=log.WARNING)
            except:
                
                last_time="2015-1-1 00:00:00"
                log.msg('************* '+last_time,level=log.WARNING)
                
        self.last_time = time.strptime(last_time, '%Y-%m-%d %H:%M:%S')
        self.last_time_sec = time.mktime(self.last_time)
        self.item_max_time = "2015-1-1 00:00:00"
        self.item_max_id=''
        self.sqlite_flag = False
  
    def process_item(self,item,spider):
        
        
        if item['topic_url'] in self.ids_seen:
            raise DropItem('Duplicate item found: %s' % item)
        else:
            item_sec = time.mktime(time.strptime(item['topic_post_time'], '%Y-%m-%d %H:%M:%S'))
            if item_sec > self.last_time_sec:
                self.sqlite_flag = True
                if item_sec > time.mktime(time.strptime(self.item_max_time, '%Y-%m-%d %H:%M:%S')):
                    self.item_max_time = item['topic_post_time']
                    self.item_max_id = item['topic_url']
             
                                
                self.ids_seen.add(item['topic_url'])
                self.dbpool.runInteraction(self._conditional_insert,item)
                return item    

    def close_spider(self, spider):
        if self.sqlite_flag:
            try:
                log.msg('delete from history where spider_name='+spider.name,level=log.WARNING)
                self.cu.execute('delete from history where spider_name="'+spider.name+'"')
                self.sx.commit() 
            except sqlite3.OperationalError,e:
                log.msg('__________',level=log.WARNING)
                pass
                
            sql = "insert into history values(?,?,?)"
            params = (self.item_max_time,self.item_max_id,spider.name)
            self.cu.execute(sql,params)    
            self.sx.commit() 
        self.cu.close()
        self.sx.close()
        self.dbpool.close()

    def _conditional_insert(self,tx,item):  
        log.msg('MINUS+++++++++++++++++++++++++++++++++++  '+item['topic_post_time'],level=log.WARNING)
        sql = 'insert into post (id , url, board, site_id, data_type , title , content, post_time, scratch_time , poster_name,poster_id,poster_url,poster_pic_url, comment_num,language_type,thread_content) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE post_time=%s  '
        param = (item['topic_url'], item['topic_url'], item['topic_board'], item['site_id'],item['data_type'],item['topic_title'], item['topic_content'], item['topic_post_time'],item['scratch_time'], item['topic_author'],item['poster_id'] ,item['homepage'],item['poster_image'],item['topic_reply'],0,item['thread_content'],item['topic_post_time'])
        tx.execute(sql,param)   