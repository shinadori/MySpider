# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from settings import IMAGES_PIPELINE_ON


# item fields dict for query
itemFields = {
    # "itemName": {
    #   "fieldName": (datatype, acsii)
    #   "fieldName": (datatype + ", PRIMARY KEY (`fieldName`)", acsii)
    # }
    "MyPageItem": {
        "uid": ("INT, PRIMARY KEY (`uid`)", False),
        "alive": ("BIT", False),
        "ban": ("VARCHAR(255)", False),
        "uname": ("VARCHAR(50)", False),
        "novel": ("BIT", False),
        "follow": ("BIT", False),
        "rate": ("BIT", False),
        "mark": ("BIT", False),
    },
    "RateItem": {
        "uid": ("INT", False),
        "nid": ("VARCHAR(10), PRIMARY KEY (`uid`, `nid`)", False),
        "rate_ac": ("INT", False),
        "rate_st": ("INT", False),
        "date_f": ("VARCHAR(50)", False),
        "date_l": ("VARCHAR(50)", False),
    },
    "NovelItem": {
        "uid": ("INT", False),
        "nid": ("VARCHAR(10), PRIMARY KEY (`uid`, `nid`)", False),
        "ntitle": ("VARCHAR(255)", False),
        "genre": ("VARCHAR(50)", False),
        "type": ("VARCHAR(10)", False),
        "part": ("VARCHAR(10)", False),
        "words": ("VARCHAR(20)", False),
    },
    "MarkItem": {
        "uid": ("INT", False),
        "nid": ("VARCHAR(10), PRIMARY KEY (`uid`, `nid`)", False),
    },
    "FollowItem": {
        "uid": ("INT", False),
        "fid": ("INT, PRIMARY KEY (`uid`, `fid`)", False),
    },
    "Top5Item": {
        "top_page": ("VARCHAR(100)", False),
        "ranktype": ("VARCHAR(100)", False),
        "rank": ("DECIMAL(10,2)", True),
        "rk_genre": ("VARCHAR(100)", False),
        "title": ("VARCHAR(100)", False),
        "link": ("VARCHAR(100)", False),
        "author": ("VARCHAR(100)", False),
        "genre": ("VARCHAR(100)", False),
    },
    "Top5AuthorItem": {
        "author": ("VARCHAR(100)", False),
        "title_num": ("VARCHAR(100)", False),
    },
}


def ranksheet(num):
    ranksheet = {
            0: "day",
            1: "week",
            2: "month",
            3: "quarter",
            4: "year",
            5: "total"
            }
    return ranksheet[num]


class MyPageItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()
    alive = scrapy.Field()
    ban = scrapy.Field()
    uname = scrapy.Field()
    novel = scrapy.Field()
    follow = scrapy.Field()
    rate = scrapy.Field()
    mark = scrapy.Field()
    # for image downloads
    if IMAGES_PIPELINE_ON:
        images = scrapy.Field()
        image_urls = scrapy.Field()
        image_paths = scrapy.Field()
        itemFields["MyPageItem"]["image_paths"] = ("VARCHAR(255)", False)


class RateItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()
    nid = scrapy.Field()
    rate_ac = scrapy.Field()
    rate_st = scrapy.Field()
    date_f = scrapy.Field()
    date_l = scrapy.Field()


class NovelItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()
    nid = scrapy.Field()
    ntitle = scrapy.Field()
    genre = scrapy.Field()
    type = scrapy.Field()
    part = scrapy.Field()
    words = scrapy.Field()


class MarkItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()
    nid = scrapy.Field()


class FollowItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()
    fid = scrapy.Field()


class Top5Item(scrapy.Item):
    # define the fields for your item here like:
    top_page = scrapy.Field()
    ranktype = scrapy.Field(
            input_processor=MapCompose(ranksheet)
            )
    rank = scrapy.Field()
    rk_genre = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    author = scrapy.Field()
    genre = scrapy.Field()


class Top5AuthorItem(scrapy.Item):
    # define the fields for your item here like:
    author = scrapy.Field()
    title_num = scrapy.Field()


class LFristLoader(ItemLoader):
    pass
    # default_output_processor = TakeFirst()
