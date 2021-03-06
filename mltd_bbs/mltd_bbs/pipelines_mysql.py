# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import mltd_bbs.mysql_query as sql
import mltd_bbs.mysql_init_db as db
from mltd_bbs.mysql_init_sheet import SHEET_NAMES_ADDAD
from mltd_bbs.items import itemFields
from mltd_bbs.items import PostItem
from mltd_bbs.settings import INSERT_NUM

class SQLPipeline(object):
    @classmethod
    def __init__(cls):
        # SHEET_NAMES_ADDAD = {
        #  "sheet1": ("SheetName1Added", "ItemName1"),
        #  "sheet2": ("SheetName2Added", "ItemName2"),
        #  "sheet3": ("SheetName3Added", "ItemName3"),
        #  "sheet4": ("SheetName4Added", "ItemName4"),
        # }
        cls.SQL_INSERT_DICT = {}
        for v in SHEET_NAMES_ADDAD.values():
            iname = v[1]

            cls.SQL_INSERT_DICT["sheet_name_" + iname] = v[0]
            cls.SQL_INSERT_DICT["sql_insert_" + iname] = sql.insert_multi(INSERT_NUM)

    def open_spider(self, spider):
        try:
            db.mysqldb.ping()
        except Exception as e:
            db.mysqldb.close()

    def close_spider(self, spider):
        db.mysqldb.close()

    def process_item(self, item, spider):
        # determine the item type
        if isinstance(item, PostItem):
            iname = "PostItem"
        else:
            iname = "Unknown"
            raise Exception("Uncatched Item: " + item.items())

        # cal item num
        for v in item.values():
            inum = len(v)
            break

        sheet_name = SQLPipeline.SQL_INSERT_DICT["sheet_name_" + iname]
        if inum == INSERT_NUM:
            sql_insert = SQLPipeline.SQL_INSERT_DICT["sql_insert_" + iname]
        else:
            sql_insert = sql.insert_multi(inum)

            # SQL Queries
        try:
            # insert query
            db.cur.execute(
                sql_insert.format(
                    sql.field_insert_multi(sheet_name, item, itemFields[iname], inum)
                )
            )
            db.mysqldb.commit()
        except Exception as e:
            db.mysqldb.rollback()
        return item
