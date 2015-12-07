# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb.cursors
import scrapy
from scrapy.contrib import spiderstate
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi

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
        
    def process_item(self,item,spider):
        self.dbpool.runInteraction(self._conditional_insert,item)

        return item    
        
    def _conditional_insert(self,tx,item):  
#         raw_input('input:____________________________________')
        sql = 'insert into post (id , url, board, site_id, data_type , title , content, post_time, scratch_time , poster_name,poster_id,poster_url, comment_num,language_type,thread_content) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE post_time=%s  '
        param = (item['topic_url'], item['topic_url'], item['topic_board'], item['site_id'],item['data_type'],item['topic_title'], item['topic_content'], item['topic_post_time'],item['scratch_time'], item['topic_author'],item['poster_id'] ,item['homepage'],item['topic_reply'],0,item['thread_content'],item['topic_post_time'])
        tx.execute(sql,param)  
