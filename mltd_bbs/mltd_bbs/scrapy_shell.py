#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'pkk'
__mtime__ = '2018/1/23'
"""


def scrapy_shell_called(response, self):
    # for test
    # pls use external system terminal, otherwise raise a error
    from scrapy.shell import inspect_response
    inspect_response(response, self)