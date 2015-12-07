# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

'''
class Mysql_scrapy_pipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
                                    dbapiName='MySQLdb',
                                    host=settings.DB_HOST,
                                    db=settings.DB,
                                    user=settings.DB_NAME,
                                    passwd=settings.DB_PASSWD,
                                    cursorclass= MySQLdb.cursors.DictCursor,
                                    charset = 'utf8',
                                    use_unicode = False
                                    )
        
    def process_item(self,item,spider):
        self.dbpool.runInteraction(self._conditional_insert,item)

        return item    
        
    def _conditional_insert(self,tx,item):  
#         if item['topic_url']
#         raw_input('input:____________________________________1')
#         sql = 'insert into post (id , url , board , title , post_time, scratch_time ,language_type, content ,thread_content) values (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE post_time=%s  '
#         param = (item['topic_url'], item['topic_url'], item['topic_channel'] ,item['topic_title'], item['topic_post_time'],item['scratch_time'] ,0,item['topic_content'],item['thread_content'],item['topic_post_time'])
        sql = 'insert into post (id , url , title , post_time, scratch_time ,language_type, content ,thread_content) values (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE post_time=%s  '
        param = (item['topic_url'], item['topic_url'],item['topic_title'], item['topic_post_time'],item['scratch_time'] ,0,item['topic_content'],item['thread_content'],item['topic_post_time'])
        tx.execute(sql,param) 
        print '_________________________________________2'
        
'''
# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb.cursors
from scrapy import log
import scrapy
from scrapy.contrib import spiderstate
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi

import settings, time


class BaiduTiebaPipeline(object):
    def process_item(self, item, spider):
        return item
         

class Mysql_scrapy_pipeline(object):
    def __init__(self):
        
        self.dbpool = adbapi.ConnectionPool(
                                    dbapiName='MySQLdb',
                                    host='127.0.0.1',
                                    db='yuqing',
                                    user='root',
                                    passwd='minus',
                                    cursorclass= MySQLdb.cursors.DictCursor,
                                    charset = 'utf8',
                                    use_unicode = False
                                    )
                                    
    def process_item(self,item,spider):               
        self.dbpool.runInteraction(self._conditional_insert_,item)
        return item  

    def _conditional_insert_(self,tx,item):  
        log.msg('MINUS+++++ : '+str(item['site_id'])+':'+item['topic_post_time'],level=log.WARNING)              
        ############################################## write into post_topic table ##########################################################################
        content = item['topic_title']+item['topic_content']
        flag=0
        # topic_list=[]
        for topic_tuple in item['topic_db_message']:
            topic_id = topic_tuple[0]
            topic_kws = topic_tuple[1]
            # print topic_kws
            # topic_list.append(topic_id)
            kws_list = topic_kws.split(',')
            
            while 1:
                try:
                    kws_list.remove('')
                except ValueError ,e:
                    break
                
            # print '__'
            for kw in kws_list:
                # print kw+' :'
                if kw in content:
                    # print kw+'>',len(kw)
                    # print 'got one '+':'+content
                    flag=1
                    query=u"insert ignore into post_topic(post_id, topic_id) values (%s, %s)"
                    param=(item['topic_url'],topic_id)
                    tx.execute(query,param) 
                    # print item['topic_url']
                    print '+++++++++++++++++++++++'
                    # raw_input('mi:')
                    break
            if flag==1:
                break   
                    
                    
        if flag==0: 
            print '_____________________2'
        sql = 'insert into '+item['table_name']+' (id , url, board, site_id, data_type , title , content, post_time, scratch_time , poster_name,poster_id,poster_url,poster_pic_url, comment_num,language_type,thread_content) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE post_time=%s ,scratch_time=%s ,thread_content=%s '
        param = (item['topic_url'], item['topic_url'], item['topic_board'], item['site_id'],item['data_type'],item['topic_title'], item['topic_content'], item['topic_post_time'],item['scratch_time'], item['topic_author'],item['poster_id'] ,item['homepage'],item['poster_image'],item['topic_reply'],0,item['thread_content'],item['topic_post_time'],item['scratch_time'],item['thread_content'])
        tx.execute(sql,param)  
        print '++++++++++++++++++++++mm ++++++++++++++++++++'
              
        
        
