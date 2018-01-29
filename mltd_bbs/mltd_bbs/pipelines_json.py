# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import json
from datetime import datetime


file_name = "common"
download_time = datetime.now().strftime("%y%m%d%H%M%S")


class JSONPipeline(object):
    def open_spider(self, spider):
        global file_name, download_time
        self.file = open(file_name + "-" + download_time + '.json',
                         'a', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
