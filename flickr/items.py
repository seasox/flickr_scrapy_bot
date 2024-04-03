# -*- coding: utf-8 -*-
import scrapy

from pprint import pformat

class FlickrPhotoset(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    photos = scrapy.Field()
    

class FlickrImage(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    tags = scrapy.Field()
    description = scrapy.Field()
    photopage = scrapy.Field()
