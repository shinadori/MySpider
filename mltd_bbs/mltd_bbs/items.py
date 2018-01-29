# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, MapCompose

# item fields dict for query
itemFields = {
    # "itemName": {
    #   "fieldName": (datatype, acsii)
    #   add primary key
    #   "fieldName1": (datatype, acsii)
    #   "fieldName2": (datatype + ", PRIMARY KEY (`fieldName1`, `fieldName2`)", acsii)
    # }
    "PostItem": {
        "uid": ("VARCHAR(20)", False),
        "pid": ("INT", False),
        "date": ("DATE", False),
        "time": ("TIME, PRIMARY KEY (`uid`, `date`, `time`)", False),
        "content": ("MEDIUMTEXT", False),
        "title": ("VARCHAR(100)", False),
    },
}


def output_check(x):
    proc = TakeFirst()
    result = proc(x)
    # print (result)
    return result


class PostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    uid = scrapy.Field()
    pid = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    title = scrapy.Field()


class LFristLoader(ItemLoader):
    pass
    # default_output_processor = Compose(output_check, )
    # default_output_processor = TakeFirst()
    # fieldName1_in = Compose(lambda x: ["n/a"] if x == [""] else x, list)
    # fieldName2_in = Compose(lambda x: ["n/a"] if x == [""] else x, list)
    # fieldName3_in = Compose(lambda x: ["n/a"] if x == [""] else x, list)
    # fieldName4_in = Compose(lambda x: [0] if x == [] else x, list)
    # fieldName4_out = Compose(lambda x: x, list)
