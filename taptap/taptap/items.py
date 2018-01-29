# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose
from settings import IMAGES_PIPELINE_ON

# item fields dict for query
itemFields = {
    # "itemName": {
    #       "fieldName": (datatype, acsii)
    #   }
    "RankItem": {
        "rankpage": ("VARCHAR(100)", False),
        "rank": ("INT", False),
        "product": ("VARCHAR(100)", False),
        "rate": ("DECIMAL(8,2)", True),
        "issuer": ("VARCHAR(100)", False),
        "tag1": ("VARCHAR(20)", False),
        "tag2": ("VARCHAR(20)", False),
        "tag3": ("VARCHAR(20)", False),
    }
}


def output_check(x):
    proc = TakeFirst()
    result = proc(x)
    return result


class RankItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    rankpage = scrapy.Field()
    rank = scrapy.Field()
    product = scrapy.Field()
    rate = scrapy.Field()
    issuer = scrapy.Field()
    tag1 = scrapy.Field()
    tag2 = scrapy.Field()
    tag3 = scrapy.Field()
    # for image downloads
    if IMAGES_PIPELINE_ON:
        images = scrapy.Field()
        image_urls = scrapy.Field()
        image_paths = scrapy.Field()
        itemFields[k]["image_paths"] = ("VARCHAR(255)", False)


class LFristLoader(ItemLoader):
    # default_output_processor = Compose(output_check, )
    tag1_in = Compose(lambda x: ["n/a"] if x == [""] else x, list)
    tag2_in = Compose(lambda x: ["n/a"] if x == [""] else x, list)
    tag3_in = Compose(lambda x: ["n/a"] if x == [""] else x, list)
    issuer_in = Compose(lambda x: ["n/a"] if x == [] else x, list)
    rate_in = Compose(lambda x: [0] if x == [] else x, list)
    image_urls_out = Compose(lambda x: x, list)
