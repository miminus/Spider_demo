# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YulinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Thread_url_Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    thread_url = scrapy.Field()
    thread_content = scrapy.Field()
    thread_post_time = scrapy.Field()
    thread_poster= scrapy.Field()
    thread_reply = scrapy.Field()
    thread_title = scrapy.Field()
    thread_poster_image = scrapy.Field()
    thread_poster_id = scrapy.Field()
    thread_id = scrapy.Field()
    scratch_time = scrapy.Field()
    thread_images = scrapy.Field() 
    thread_poster_homepage = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths= scrapy.Field()

class Topic_Item(scrapy.Item):
    topic_url = scrapy.Field()
    topic_content = scrapy.Field()
    topic_post_time = scrapy.Field()
    scratch_time = scrapy.Field()
    topic_reply = scrapy.Field()
    topic_title = scrapy.Field()
    topic_author = scrapy.Field()
    thread_content = scrapy.Field()
    topic_db_message = scrapy.Field()
    poster_id = scrapy.Field()
    homepage = scrapy.Field()
    poster_image = scrapy.Field()
    topic_board = scrapy.Field()
    site_id = scrapy.Field()
    data_type = scrapy.Field()