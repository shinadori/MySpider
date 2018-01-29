#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'middlewares_proxy'
__author__ = 'Billy'
__mtime__ = '2018/1/23'
"""

import base64
import random
import logging
from mltd_bbs.settings import PROXIES


class ProxyMiddleware(object):
    """
    cover scrapy's HttpProxyMiddleware.
    if 'proxy' in request.meta, HttpProxyMiddleware don't do anything.
    """
    def process_request(self, request, spider):
        """overwrite method"""
        if 'proxy' in request.meta:
            return

        proxy = random.choice(PROXIES)
        request.meta['proxy'] = "http://%s" % proxy['ip_port']
        # encoded_user_pass = base64.encodestring(proxy['user_pass'])
        encoded_user_pass = base64.b64encode(proxy['user_pass'].encode(encoding='utf-8'))
        request.headers['Proxy-Authorization'] = 'Basic ' + str(encoded_user_pass)
        # logging.info('[ProxyMiddleware] proxy:%s is used', proxy)