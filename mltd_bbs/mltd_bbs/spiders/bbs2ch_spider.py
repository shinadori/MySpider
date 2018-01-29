#!/usr/bin/env python

# -*- coding: utf-8 -*-


import scrapy
import json
import re
from mltd_bbs.items import PostItem
from mltd_bbs.items import LFristLoader
from urllib.parse import urljoin
from mltd_bbs.scrapy_shell import scrapy_shell_called
from mltd_bbs.settings import INSERT_NUM

# target: (screenshot)
# 【GREE】アイドルマスターミリオンライブ!PART1673 (1001)
# https://2ch.vet/re_anago_sns_1516070414_a_0


class BBS2chSpider(scrapy.Spider):
    name = 'bbs2ch_spider'
    domain = 'https://2ch.vet'
    regular_search_response = 're_anago_sns_([0-9]+)_a_0.+:\s(.+\))\s+<B'
    # start_page = "https://2ch.vet/index.php"

    def start_requests(self):
        # search sample:【GREE】アイドルマスターミリオンライブ!Part1674 (184)
        search_keyword = "【GREE】アイドルマスターミリオンライブ"
        part_keyword = "!PART"
        for part_num in range(1601, 1675):
            search_term = search_keyword + part_keyword + str(part_num)
            yield scrapy.http.FormRequest(url=urljoin(BBS2chSpider.domain, "find.php"),
                                          callback=self.parse_posturl,
                                          formdata={"search_term": search_term},
                                          meta={"search_term": search_term})

    def parse_posturl(self, response):
        post_url = response.xpath('//a/@href').extract()
        if post_url:
            # (post_id, post_title)
            search_response = re.findall(BBS2chSpider.regular_search_response, response.text)

            # find the max post_url num
            if len(search_response) == 1:
                max_index = 0
            else:
                max_index = 0
                for i in range(len(search_response) - 1):
                    if search_response[i][0] < search_response[i + 1][0]:
                        max_index = i + 1

            # move to target post (max)
            yield scrapy.Request(url=urljoin(BBS2chSpider.domain, post_url[max_index]),
                                 callback=self.parse_posturl_all)

            # post duplicate
            if len(search_response) != 1:
                same_index = -1
                search_response.sort()
                # check whether there are same titles
                for i in range(len(search_response) - 1):
                    if search_response[i][1] == search_response[i + 1][1]:
                        same_index = i
                # if exist, index the same title in post_url
                if same_index != -1:
                    same_id = search_response[-2][0]
                    for i in range(len(post_url)):
                        if same_id in post_url[i]:
                            same_index = i
                yield scrapy.Request(url=urljoin(BBS2chSpider.domain, post_url[same_index]),
                                     callback=self.parse_posturl_all)
        else:
            print ("WARNING.")
            print ("Not exist such post: " + response.meta["search_term"])

    def parse_posturl_all(self, response):
        post_urls = response.xpath('//div[@class="btn-group"]/a/@href').extract()
        if post_urls:
            # move to target post
            yield scrapy.Request(url=urljoin(BBS2chSpider.domain, post_urls[-1]),
                                 callback=self.parse_post)
        else:
            print ("WARNING.")
            print ("Not exist all_page button.")
            print ("Error url: " + response.url)


    def parse_post(self, response):
        # title = response.xpath('//div[@class="panel-heading"]/h4/text()').extract()

        # re for search data
        regular_title = '<h4>\s+(\【.+\))(\s+</h4>)'

        regular_meta = '">([0-9]+?)\s(.+?)<br>' \
                       '([0-9]+\/[0-9]+\/[0-9]+)\(.\)\s' \
                       '([0-9]+:[0-9]+:[0-9]+\.[0-9]+)'
        # regular_pid = '">([0-9]+?)\s(.+?)<br>'
        # regular_date = '([0-9]+\/[0-9]+\/[0-9]+)\(.\)'
        # regular_time = '([0-9]+:[0-9]+:[0-9]+\.[0-9]+)'
        regular_uid = '([0-9]+:[0-9]+:[0-9]+\.[0-9]+)\s+(ID:)?([^\s]+)?\s+<br>  <br></font></b>'
        regular_content = '</font></b>\s?(<a.+\/a>   <br> )?(.+)\s+<br>\s+<br></font></b>'

        # (title, blank)
        list_title = re.findall(regular_title, response.text)

        # (time, "ID:", uid)
        list_uid = re.findall(regular_uid, response.text)
        # (pid, uname, date, time)
        list_meta = re.findall(regular_meta, response.text)

        # (post_id, uname)
        # list_pid = re.findall(regular_pid, response.text)
        # list_date = re.findall(regular_date, response.text)
        # list_time = re.findall(regular_time, response.text)

        # (reply_to, content)
        list_content = re.findall(regular_content, response.text)

        # for test
        # pls use external system terminal, otherwise raise a error
        # scrapy_shell_called(response, self)

        for i in range(len(list_meta)):
            if i % INSERT_NUM == 0:
                post_loader = LFristLoader(item=PostItem(), response=response)


            post_loader.add_value("uid", list_uid[i][2])
            post_loader.add_value("pid", list_meta[i][0])
            post_loader.add_value("date", list_meta[i][2])
            post_loader.add_value("time", list_meta[i][3])

            # post_loader.add_value("pid", list_pid[i][0])
            # post_loader.add_value("date", list_date[i])
            # post_loader.add_value("time", list_time[i])

            post_loader.add_value("title", list_title[0][0])
            post_loader.add_value("content", list_content[i][1])

            if i % INSERT_NUM == INSERT_NUM - 1:
                yield post_loader.load_item()
            elif i == len(list_meta) - 1:
                yield post_loader.load_item()
