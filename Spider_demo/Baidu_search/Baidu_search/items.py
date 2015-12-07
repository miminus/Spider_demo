# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


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
    topic_id = scrapy.Field()
