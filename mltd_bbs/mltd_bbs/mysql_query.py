#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


def create_table(idict):
    # create_sheet query
    sql = "CREATE TABLE IF NOT EXISTS `%s` ("
    datatype = ""
    for i in range(2):
        if i == 0:
            for (k, v) in idict.items():
                datatype += k + " " + v[0] + ", "
        else:
            sql += datatype[:-2] + ");"

    return sql


def insert_multi(field_length):
    sql = "INSERT INTO `{0[0]}` VALUES "
    for i in range(field_length):
        if i == 0:
            sql = sql + "({0[" + str(i + 1) + "]})"
        else:
            sql = sql + ", ({0[" + str(i + 1) + "]})"

    return sql


def field_insert_multi(sheet_name, item, item_fields, item_num):
    item_after_acsii = {}
    value_dict = {}

    # transfer item(ascii) to item(non_ascii)
    for (k, v) in item_fields.items():
        item_after_acsii[k] = []
        # process ascii part
        if v[1]:
            for i in range(len(item[k])):
                item_after_acsii[k].append(item[k][i])
        else:
            for i in range(len(item[k])):
                item_after_acsii[k].append(
                    json.dumps(item[k][i], ensure_ascii=False)
                )

    # prepare for value_dict
    for i in range(item_num):
        value_dict[i] = []

    # add value to the value_dict
    for k, v in item_after_acsii.items():
        for i in range(len(item_after_acsii[k])):
            value_dict[i].append(v[i])

    sql_list = [sheet_name]
    # generate the sql_list
    for v in value_dict.values():
        sql_list.append(",".join(v))
    return sql_list
    # sql_insert.format(sql_list)
    # n is the num of item's attrs
    # l is the length of the list of item's attr
    # sql_list = [mysql_init_sheet.sheet_name,
    #             [json.dumps(item[0][0], ensure_ascii=v[1]),
    #              json.dumps(item[1][0], ensure_ascii=v[1]),
    #              ...,
    #              json.dumps(item[n][0], ensure_ascii=v[1])
    #             ],
    #             [json.dumps(item[0][1], ensure_ascii=v[1]),
    #              json.dumps(item[1][1], ensure_ascii=v[1]),
    #              ...,
    #              json.dumps(item[n][1], ensure_ascii=v[1])
    #             ],
    #             ...,
    #             [json.dumps(item[0][l], ensure_ascii=v[1]),
    #              json.dumps(item[1][l], ensure_ascii=v[1]),
    #              ...,
    #              json.dumps(item[n][l], ensure_ascii=v[1])
    #             ]
    #            ]
