#!/usr/bin/env python

# -*- coding: utf-8 -*-

import mltd_bbs.mysql_init_db as db
import mltd_bbs.mysql_query as sql
from mltd_bbs.items import itemFields
from mltd_bbs.settings import SHEET_NAMES
from datetime import datetime


# add timestamp for sheet_name
def sheet_timestamp(name, on):
    if on is True:
        name_added = name + "-" + download_time
    else:
        name_added = name
    return name_added


# create sheet according to the SheetNamesDict and ItemFieldsDict
def create_sheet(sndict, ifdict, sndict_added):
    for k, v in sndict.items():
        # k: "sheet1"
        # v: ("SheetName", SHEET_NAMES_TIMESTAMP, "ReferItemName")
        sheet_name = SHEET_NAMES[k][0]
        add_time = SHEET_NAMES[k][1]
        item_names = SHEET_NAMES[k][2]

        # create_sheet query
        sql_create_sheet = sql.create_table(ifdict[item_names])

        # change sheet name and add to sndict_add
        sheet_name = sheet_timestamp(sheet_name, add_time)
        sndict_added[k] = (sheet_name, item_names)

        # create sheet
        try:
            db.cur.execute(sql_create_sheet % sheet_name)
            db.mysqldb.commit()
        except Exception as e:
            db.mysqldb.rollback()
            db.mysqldb.close()


download_time = datetime.now().strftime("%y%m%d%H%M%S")

SHEET_NAMES_ADDAD = {}
create_sheet(SHEET_NAMES, itemFields, SHEET_NAMES_ADDAD)
# SHEET_NAMES_ADDAD = {
#  "sheet1": ("SheetName1Added", "ItemName1"),
#  "sheet2": ("SheetName2Added", "ItemName2"),
#  "sheet3": ("SheetName3Added", "ItemName3"),
#  "sheet4": ("SheetName4Added", "ItemName4"),
# }
