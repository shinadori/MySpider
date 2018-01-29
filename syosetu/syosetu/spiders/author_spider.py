#!/usr/bin/env python

# -*- coding: utf-8 -*-


import scrapy
import re
from items import MyPageItem
from items import RateItem
from items import NovelItem
from items import MarkItem
from items import FollowItem
from items import LFristLoader
from urllib.parse import urljoin


novel_url = "https://mypage.syosetu.com/mypage/novellist/userid/"
follow_url = "https://mypage.syosetu.com/mypagefavuser/list/userid/"
mark_url = "https://mypage.syosetu.com/mypagefavnovelmain/list/userid/"
rate_url = "https://mypage.syosetu.com/mypagenovelhyoka/list/userid/"


class MyPageSpider(scrapy.Spider):
    name = 'mypage_spider'
    domain = 'https://mypage.syosetu.com'

    def start_requests(self):
        for i in range(100, 200):
            yield scrapy.Request(url=urljoin(MyPageSpider.domain, str(i)),
                                 callback=self.parse_mypage,
                                 meta={"uid": i})

    def parse_mypage(self, response):
        # top
        # all: https://mypage.syosetu.com/3/
        # null: https://mypage.syosetu.com/5/
        # error-cancel: https://mypage.syosetu.com/198208/
        # error-illegal: https://mypage.syosetu.com/123732/
        uid = response.meta["uid"]

        alive_or_not = response.xpath('//div[@class="info_message_error"]/p/text()').extract()
        if alive_or_not:
            # dead user
            mypage_loader = LFristLoader(item=MyPageItem(),
                                         response=response)
            mypage_loader.add_value("uid", uid)

            mypage_loader.add_value("alive", False)
            mypage_loader.add_value("ban", alive_or_not)
            mypage_loader.add_value("uname", "N/A")
            mypage_loader.add_value("novel", False)
            mypage_loader.add_value("follow", False)
            mypage_loader.add_value("rate", False)
            mypage_loader.add_value("mark", False)
            yield mypage_loader.load_item()
        else:
            # alive user
            mypage_dict = {
                "uid": uid,
                "alive": True,
                "ban": "N/A", }

            # name
            uname = response.xpath('//dl[@class="profile"]/dd/text()').extract()
            mypage_dict["uname"] = uname[1]

            # novel
            novel = response.xpath('//div[@id="novellist_top"]/h3/text()').extract()
            if novel:
                mypage_dict["novel"] = True
                yield scrapy.Request(url=urljoin(novel_url, str(uid)),
                                     callback=self.parse_novel,
                                     meta={"uid": uid})
            else:
                mypage_dict["novel"] = False

            # favuserlist_top
            follow = response.xpath('//div[@id="favuserlist_top"]/h3/text()').extract()
            if follow:
                mypage_dict["follow"] = True
                yield scrapy.Request(url=urljoin(follow_url, str(uid)),
                                     callback=self.parse_follow,
                                     meta={"uid": uid})
            else:
                mypage_dict["follow"] = False

            # favnovel
            mark = response.xpath('//div[@id="favnovel"]/h3/text()').extract()
            if mark:
                mypage_dict["mark"] = True
                yield scrapy.Request(url=urljoin(mark_url, str(uid)),
                                     callback=self.parse_mark,
                                     meta={"uid": uid,
                                           "category": False})
            else:
                mypage_dict["mark"] = False

            # rate
            yield scrapy.Request(url=urljoin(rate_url, str(uid)),
                                 callback=self.parse_rate,
                                 meta={"from": "mypage", "mypage_dict": mypage_dict})

    def parse_rate(self, response):
        # rate
        # none: https://mypage.syosetu.com/mypagenovelhyoka/list/userid/372556/
        # one page: https://mypage.syosetu.com/mypagenovelhyoka/list/userid/738145/
        # more pages: https://mypage.syosetu.com/mypagenovelhyoka/list/userid/288399/

        # rate
        rate_null = response.xpath('//div[@class="info_message_nothin"]/text()').extract()
        if rate_null:
            # not exist
            mypage_loader = LFristLoader(item=MyPageItem(), response=response)
            mypage_loader.add_value(None, response.meta["mypage_dict"])
            mypage_loader.add_value("rate", False)
            yield mypage_loader.load_item()
        else:
            # exist
            # for first time
            if "from" in response.meta:
                mypage_loader = LFristLoader(item=MyPageItem(), response=response)
                mypage_loader.add_value(None, response.meta["mypage_dict"])
                mypage_loader.add_value("rate", True)
                yield mypage_loader.load_item()

            # scrapy for rating data
            if "from" in response.meta:
                uid = response.meta["mypage_dict"]["uid"]
            else:
                uid = response.meta["uid"]

            novel_link = response.xpath('//div[@id="novelpointlist"]/ul/li/a/@href').extract()
            rate_date = response.xpath('//p[@class="hyouka_hi"]/text()').extract()
            rate = response.xpath('//p[@class="hyouka"]/text()').extract()

            date_dif_max = len(rate_date) - len(novel_link)
            date_dif_now = 0

            rate_loader = LFristLoader(item=RateItem(), response=response)
            for i in range(len(novel_link)):
                rate_loader.add_value("uid", uid)

                # nid: https://ncode.syosetu.com/n4830bu/
                novel_id = re.search(".com/.+/", novel_link[i]).group()
                rate_loader.add_value("nid", novel_id[5:-1])

                # date_f: "\n初回評価日：2017年12月9日\n"
                # date_l: "最終評価日：2014年7月1日"
                if date_dif_now < date_dif_max:
                    if rate_date[i + date_dif_now + 1][0:2] == "最終":
                        # the last date next to the first date
                        date = re.search("評価日：.+", rate_date[i + date_dif_now + 1]).group()
                        rate_loader.add_value("date_l", date[4:])
                        date = re.search("評価日：.+", rate_date[i + date_dif_now]).group()

                        date_dif_now += 1
                    else:
                        # N/A
                        rate_loader.add_value("date_l", "N/A")
                        date = re.search("評価日：.+", rate_date[i + date_dif_now]).group()
                else:
                    # N/A
                    rate_loader.add_value("date_l", "N/A")
                    date = re.search("評価日：.+", rate_date[i + date_dif_max]).group()
                rate_loader.add_value("date_f", date[4:])

                # rate_st: "ストーリー評価：5pt"
                # rate_ac: "文章評価：5pt"
                rate_st = rate[i * 2][8]
                rate_ac = rate[i * 2 + 1][5]
                rate_loader.add_value("rate_st", rate_st)
                rate_loader.add_value("rate_ac", rate_ac)

            yield rate_loader.load_item()

            # more_pages
            next_page = response.xpath('//div[@class="pager_idou"]/a[@title="次のページ"]/@href').extract()
            # next_page = ["?p=2", "?p=2"]
            if next_page:
                yield scrapy.Request(url=urljoin(rate_url + str(uid) + "/", next_page[0]),
                                     callback=self.parse_rate,
                                     meta={"uid": uid})

    def parse_novel(self, response):
        # novel
        # none: https://mypage.syosetu.com/mypage/novellist/userid/1/
        # one page: https://mypage.syosetu.com/mypage/novellist/userid/372556/
        # more pages: https://mypage.syosetu.com/mypage/novellist/userid/288399/

        uid = response.meta["uid"]

        # scrapy for novel data
        novel_link = response.xpath('//div[@id="novellist"]/ul/li[@class="title"]/a/@href').extract()
        novel_title = response.xpath('//div[@id="novellist"]/ul/li[@class="title"]/a/text()').extract()
        genre = response.xpath('//span[@class="genre"]/text()').extract()
        type = response.xpath('//li[@class="date1"]/span[@class="type"]/text()').extract()
        part = response.xpath('//li[@class="date1"]/text()').extract()
        amount = response.xpath('//li[@class="date"]/text()').extract()

        ss_num_now = 0

        novel_loader = LFristLoader(item=NovelItem(), response=response)

        for i in range(len(novel_link)):
            novel_loader.add_value("uid", uid)

            # novel
            # id: https://ncode.syosetu.com/n4830bu/
            # title: 無職転生　- 蛇足編 -
            novel_id = re.search(".com/.+/", novel_link[i]).group()
            novel_loader.add_value("nid", novel_id[5:-1])
            novel_loader.add_value("ntitle", novel_title[i])

            # genre: ハイファンタジー[ファンタジー]
            novel_loader.add_value("genre", genre[i])

            # type: "完結済：", "連載：", "短編"
            # part: 全32部分
            if type[i] == "短編":
                ss_num_now += 1
                novel_loader.add_value("type", type[i])
                novel_loader.add_value("part", "1")
            else:
                novel_loader.add_value("type", type[i][:-1])
                novel_loader.add_value("part", part[2 + i * 4 - ss_num_now][1:-2])

            # amount: 読了時間：約636分（317,854文字）
            words = re.search("分（.+文字）", amount[i]).group()
            novel_loader.add_value("words", words[2:-3])

        yield novel_loader.load_item()

        # more_pages
        next_page = response.xpath('//div[@class="pager_idou"]/a[@title="next page"]/@href').extract()
        # next_page = ["index.php?all=1&all2=1&all3=1&all4=1&p=2", "index.php?all=1&all2=1&all3=1&all4=1&p=2"]
        if next_page:
            yield scrapy.Request(url=urljoin(novel_url + str(uid) + "/", next_page[0]),
                                 callback=self.parse_novel,
                                 meta={"uid": uid})

    def parse_mark(self, response):
        # mark
        # none: https://mypage.syosetu.com/mypagefavnovelmain/list/userid/2/
        # one page: https://mypage.syosetu.com/mypagefavnovelmain/list/userid/1/
        # more pages: https://mypage.syosetu.com/mypagefavnovelmain/list/userid/288399/
        # more pages & categories: https://mypage.syosetu.com/mypagefavnovelmain/list/userid/282121/?nowcategory=2

        uid = response.meta["uid"]
        category = response.meta["category"]

        # scrapy for mark data
        novel_link = response.xpath('//div[@id="novellist"]/ul/li[@class="title"]/a/@href').extract()

        mark_loader = LFristLoader(item=MarkItem(), response=response)
        for i in range(len(novel_link)):

            mark_loader.add_value("uid", uid)

            # mark_link: https://ncode.syosetu.com/n0083dl/
            novel_id = re.search(".com/.+/", novel_link[i]).group()
            mark_loader.add_value("nid", novel_id[5:-1])

        yield mark_loader.load_item()

        # more_pages
        next_page = response.xpath('//div[@class="pager_idou"]/a[@title="next page"]/@href').extract()
        # next_page = ["index.php?p=2", "index.php?p=2"]
        if next_page:
            yield scrapy.Request(url=urljoin(mark_url + str(uid) + "/", next_page[0]),
                                 callback=self.parse_mark,
                                 meta={"uid": uid,
                                       "category": True})

        # more_category
        next_category = response.xpath('//div[@id="bkm_category"]/ul/li/a/@href').extract()
        # next_category = ["/mypagefavnovelmain/list/userid/282121/?nowcategory=2",
        #                  "/mypagefavnovelmain/list/userid/282121/?nowcategory=3"]
        if category is False and next_category:
            for i in next_category:
                yield scrapy.Request(url=urljoin(mark_url + str(uid) + "/", i),
                                     callback=self.parse_mark,
                                     meta={"uid": uid,
                                           "category": True})

    def parse_follow(self, response):
        # follow
        # none: https://mypage.syosetu.com/mypagefavuser/list/userid/1/
        # one page: https://mypage.syosetu.com/mypagefavuser/list/userid/738145/
        # more pages: https://mypage.syosetu.com/mypagefavuser/list/userid/288399/

        uid = response.meta["uid"]

        # scrapy for folllow data
        favuser_link = response.xpath('//div[@id="favuser"]/ul/li/a/@href').extract()

        follow_loader = LFristLoader(item=FollowItem(), response=response)
        for i in range(len(favuser_link)):

            follow_loader.add_value("uid", uid)

            # followee id: /373780/
            follow_loader.add_value("fid", favuser_link[i][1:-1])

        yield follow_loader.load_item()

        # more_pages
        next_page = response.xpath('//div[@class="pager_idou"]/a[@title="next page"]/@href').extract()
        # next_page = ["index.php?p=2", "index.php?p=2"]
        if next_page:
            yield scrapy.Request(url=urljoin(follow_url + str(uid) + "/", next_page[0]),
                                 callback=self.parse_follow,
                                 meta={"uid": uid})
