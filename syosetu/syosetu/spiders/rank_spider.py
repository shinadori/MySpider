# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 11:11:28 2017

@author: pkk
@version: 1.2
"""


import scrapy
from items import Top5Item
from items import Top5AuthorItem
from items import LFristLoader
from urllib.parse import urljoin


class Top5Spider(scrapy.Spider):
    name = 'rank_spider'
    domain = 'https://yomou.syosetu.com'

    @classmethod
    def __init__(cls):
        # data of different top page
        top = {"page": "top",
               "max_rank": 5,
               "type_num": 1,
               "group_by_genre": False,
               "rank_genre": False}
        isekaitop = {"page": "isekaitop",
                     "max_rank": 5,
                     "type_num": 3,
                     "group_by_genre": False,
                     "rank_genre": True}
        genretop = {"page": "genretop",
                    "max_rank": 5,
                    "type_num": 19,
                    "group_by_genre": True,
                    "rank_genre": True}
        cls.page_data = {"top": top,
                         "isekaitop": isekaitop,
                         "genretop": genretop}

    def start_requests(self):
        urls = [
            'rank/top/',
            'rank/isekaitop/',
            'rank/genretop/'
        ]
        for i in range(3):
            yield scrapy.Request(url=urljoin(SyosetuSpider.domain, urls[i]),
                                 callback=self.parse_rank,
                                 meta=SyosetuSpider.page_data[
                                         urls[i][urls[i].find("/") + 1:
                                                 urls[i].find("/", 5)]
                                         ])

    def parse_rank(self, response):
        sst_num = len(response.xpath('//a[@class="tl"]/text()').
                      extract())
        page = response.meta["page"]
        max_rank = response.meta["max_rank"]
        type_num = response.meta["type_num"]
        group_by_genre = response.meta["group_by_genre"]
        rank_genre = response.meta["rank_genre"]

        for i in range(int(sst_num/max_rank/type_num)):
            for j in range(type_num):
                for k in range(max_rank):
                    catch_no = k + j * max_rank + i * max_rank * type_num

                    sstloader = LFristLoader(item=Top5Item(),
                                             response=response)
                    sstloader.add_value('top_page', page)
                    sstloader.add_value('ranktype', i)
                    sstloader.add_value('rank', k + 1)
                    sstloader.add_xpath('title', '//a[@class="tl"]/text()',
                                        lambda l: l[catch_no])
                    sstloader.add_xpath('link', '//a[@class="tl"]/@href',
                                        lambda l: l[catch_no])

                    # scrape for data of the author and genre
                    if group_by_genre:
                        sstloader.add_xpath(
                                'author',
                                '//span[@class="name"]/a/text()',
                                lambda l: l[catch_no])
                        sstloader.add_xpath(
                                'genre',
                                '//h3[@class="ranking_genre"]/text()',
                                lambda l: l[j])
                    else:
                        sstloader.add_xpath(
                                'author',
                                '//span[@class="name_genre"]/a/text()',
                                lambda l: l[catch_no * 2])
                        sstloader.add_xpath(
                                'genre',
                                '//span[@class="name_genre"]/a/text()',
                                lambda l: l[catch_no * 2 + 1])

                    # scrape for rank_genre data
                    if rank_genre:
                        sstloader.add_xpath(
                                'rk_genre',
                                '//h3[@class="ranking_genre"]/text()',
                                lambda l: l[j])
                    else:
                        sstloader.add_xpath(
                                'rk_genre',
                                '//span[@class="name_genre"]/a/text()',
                                lambda l: l[catch_no * 2 + 1])
                    yield sstloader.load_item()

        # scrapy for author
        if group_by_genre:
            author_links = response\
                .xpath('//span[@class="name"]/a/@href')\
                .extract()
        else:
            author_links = response\
                .xpath('//span[@class="name_genre"]/a/@href')\
                .extract()[::2]
        for url in author_links:
            yield scrapy.Request(url=url,
                                 callback=self.parse_author)

    def parse_author(self, response):
        authorloader = LFristLoader(item=Top5AuthorItem(),
                                    response=response)
        authorloader.add_value('author', response.xpath(
                                u'//div[@id="anotheruser_info"]/h1/text()'
                                ).extract())
        authorloader.add_value('title_num', response.xpath(
                                u'//span[@class="allnovel"]/text()'
                                ).extract())
        yield authorloader.load_item()
