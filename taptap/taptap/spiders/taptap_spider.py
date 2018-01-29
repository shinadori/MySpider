# -*- coding: utf-8 -*-
"""
@author: shiradori
@version: 1.2
"""


import scrapy
import logging
import json
import re
from items import RankItem
from items import LFristLoader
from settings import IMAGES_PIPELINE_ON

from urllib.parse import urljoin
from lxml import etree
from lxml.etree import XMLParser


parser = XMLParser(ns_clean=True, recover=True)
logger = logging.getLogger(__name__)


# xpath code
xpathPPage = '\
    //a[@class="card-middle-title "]/@href |\
    //a[@class="card-middle-title hasArea"]/@href'
xpathProduct = '\
    //a[@class="card-middle-title "]/h4/text() |\
    //a[@class="card-middle-title hasArea"]/h4/text()'
xpathRank = '\
    //span[@class="top-card-order-text"]/text()'
xpathIssuer = '\
    //p[@class="card-middle-author"]/a/text() |\
    //p[@class="card-middle-author"]/span/text()'


class TapTapSpider(scrapy.Spider):
    name = 'taptap_spider'
    domain = ["https://www.taptap.com",
              ]
    # target: https://www.taptap.com/top/...

    def start_requests(self):
        base_urls = [
            # android
            "top/download",
            # ios
            "top/ios",
            # google play - hk
            "top/google/hk/free",
            # appstore - cn
            "top/apple/cn/free",
            # developers
            "top/developers"
        ]
        used_urls = set(base_urls)
        for i in range(0, 4):
            yield scrapy.Request(
                    url=urljoin(TapTapSpider.domain[0], base_urls[i]),
                    callback=self.pr30_parse,
                    meta={"rankpage": base_urls[i],
                          "used_urls": used_urls}
                    )

    def pr30_parse(self, response):
        global xpathPPage, xpathProduct, xpathRank, xpathIssuer

        nextpage = []
        used_urls = response.meta["used_urls"]
        # other rank types
        # rank type:
        #   android - download/new/reserve/sell/played
        #   ios - download/new/reserve/played
        #   google play - free/new/grossing
        #   appstore - free/paid/grossing
        next_urls = response.xpath(
            '//ul[@class="nav nav-pills"]/li/a/@href'
            ).extract()
        # other areas
        # areas:
        #   google play - us/jp/tw/hk
        #   appstore - us/jp/kr/cn/tw/hk
        next_urls_area = response.xpath(
            '//ul[@class="list-unstyled dropdown-menu"]/li/a/@href'
            ).extract()
        if next_urls_area != [] or next_urls != []:
            for i in range(len(next_urls)):
                nextpage.append(re.search("top.+", next_urls[i]).group())
                # logger.warning("next_url: {}".format(nextpage[i]))
                if nextpage[i] not in used_urls:
                    used_urls.add(nextpage[i])
                    yield scrapy.Request(next_urls[i],
                                         callback=self.pr30_parse,
                                         meta={"rankpage": nextpage[i], "used_urls": used_urls})
            for i in range(len(next_urls), len(next_urls_area)):
                nextpage.append(re.search("top.+", next_urls_area[i]).group())
                # logger.warning("next_url: {}".format(nextpage[i]))
                if nextpage[i] not in used_urls:
                    used_urls.add(nextpage[i])
                    yield scrapy.Request(next_urls_area[i],
                                         callback=self.pr30_parse,
                                         meta={"rankpage": nextpage[i], "used_urls": used_urls})

        # scrape
        if "rankpage" in response.meta:
            rankpage = response.meta["rankpage"]

        ppage = response.xpath(xpathPPage).extract()

        ranker = LFristLoader(item=RankItem(), response=response)

        for i in range(len(ppage)):
            pathbase = '//a[@href="' + ppage[i] + '"]/../..'

            # ranker = LFristLoader(item=RankItem(), response=response)
            ranker.add_value("rankpage", rankpage)
            ranker.add_xpath("rank", xpathRank, lambda r: r[i])
            ranker.add_xpath("product", xpathProduct, lambda r: r[i])
            # ranker.add_xpath("issuer", xpathIssuer, lambda r: r[i])

            # scrapy issuer
            issuer = response.xpath(pathbase + '/div/p[@class="card-middle-author"]/a/text() | ' +
                                    pathbase + '/div/p[@class="card-middle-author"]/span/text()').extract()
            ranker.add_value("issuer", issuer)

            # scrapy image
            if IMAGES_PIPELINE_ON:
                image_urls = response.xpath(pathbase + '/div/a[@class="card-left-image"]/img/@src').extract()
                ranker.add_value("image_urls", image_urls, re='.+.png')

            # scrapy rate
            rate = response.xpath(pathbase + '/div/div/p[@class="middle-footer-rating"]/span/text()').extract()
            ranker.add_value("rate", rate)

            # scrapy tag
            tags = response.xpath(pathbase + '/div/div[@class="card-tags"]/a/text()').extract()
            for i in range(3 - len(tags)):
                tags.append("")
            for num in range(3):
                ranker.add_value("tag" + str(num + 1), tags[num])

        yield ranker.load_item()

        # https://www.taptap.com/ajax/top/download?page=2&total=30
        dataurl = response.xpath(
                '//section[@class="taptap-button-more"]/button/@data-url'
                ).extract()
        total = re.search("total=.+", dataurl[0]).group()[6:]
        logger.warning("dataurl: {}".format(dataurl[0]))
        yield scrapy.Request(
                url=dataurl[0],
                callback=self.pr_more_parse,
                meta={"page_no": 2,
                      "total": int(total),
                      "rankpage": rankpage})

    def pr_more_parse(self, response):
        global xpathPPage, xpathProduct, xpathRank, xpathIssuer

        # for test
        # pls use external system terminal, otherwise raise a error
# =============================================================================
#         if page_no > 2:
#             from scrapy.shell import inspect_response
#             inspect_response(response, self)
# =============================================================================

        # prepare the doc of html
        rawdoc = response.text
        json_acceptable_string = rawdoc.replace("'", "\"")
        cleardoc = json.loads(json_acceptable_string)

        if cleardoc["data"]["html"] != "":
            doc = etree.fromstring(cleardoc["data"]["html"], parser)

            # load metadata
            rankpage = response.meta["rankpage"]

            # extract data
            ppage = doc.xpath(xpathPPage)
            lRank = doc.xpath(xpathRank)
            lProduct = doc.xpath(xpathProduct)
            # lIssuer = doc.xpath(xpathIssuer)

            ranker = LFristLoader(item=RankItem(), response=response)

            for i in range(len(ppage)):
                pathbase = '//a[@href="' + ppage[i] + '"]/../..'

                # ranker = LFristLoader(item=RankItem(), response=response)
                ranker.add_value("rankpage", rankpage)
                ranker.add_value("rank", lRank, lambda r: r[i])
                ranker.add_value("product", lProduct, lambda r: r[i])
                # ranker.add_value("issuer", lIssuer, lambda r: r[i])

                # scrapy issuer
                issuer = response.xpath(pathbase + '/div/p[@class="card-middle-author"]/a/text() | ' +
                                        pathbase + '/div/p[@class="card-middle-author"]/span/text()').extract()
                ranker.add_value("issuer", issuer)

                # scrapy rate
                rate = doc.xpath(pathbase + '/div/div/p[@class="middle-footer-rating"]/span/text()')
                ranker.add_value("rate", rate)

                # scrapy tags
                tags = doc.xpath(pathbase + '/div/div[@class="card-tags"]/a/text()')
                for i in range(3 - len(tags)):
                    tags.append("")
                for num in range(3):
                    ranker.add_value("tag" + str(num + 1), tags[num])

            yield ranker.load_item()

            # load metadata
            page_no = response.meta["page_no"] + 1
            total = response.meta["total"] + len(ppage)

            # https://www.taptap.com/ajax/top/download?page=2&total=30
            dataurl = cleardoc["data"]["next"]
            logger.warning("dataurl: {}".format(dataurl))
            if cleardoc["data"]["next"] is not None:
                yield scrapy.Request(
                        url=dataurl,
                        callback=self.pr_more_parse,
                        meta={"page_no": page_no,
                              "total": total,
                              "rankpage": rankpage})
