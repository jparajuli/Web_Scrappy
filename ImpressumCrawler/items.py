# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImpressumcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    urls = scrapy.Field()
    comp_names = scrapy.Field()
    emails = scrapy.Field()
    fax = scrapy.Field()
    telephone = scrapy.Field()
    address = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    pass
