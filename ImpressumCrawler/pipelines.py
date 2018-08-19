# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
class ImpressumcrawlerPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
                    settings['MONGODB_SERVER'],
                    settings['MONGODB_PORT']
                     )

        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

        #clean up previous one before new crawling
        self.collection.remove({})

    def process_item(self, item, spider):
        valid = True
        if valid:
            self.collection.insert(dict(item))
        else:
            raise(DropItem("No valid item"))
        return item
