#!/usr/bin/env python

# -*- coding: utf-8 -*-

import pymysql
from settings import DB_NAME
from settings import CONNECTION

# configuration of MySQL
conn_init = CONNECTION
db_name = DB_NAME

mysqldb = pymysql.Connect(host=conn_init["host"],
                          user=conn_init["user"],
                          password=conn_init["password"],
                          port=conn_init["port"],
                          charset=conn_init["charset"])
cur = mysqldb.cursor()
try:
    sql = "CREATE DATABASE IF NOT EXISTS `%s`"
    cur.execute(sql % db_name)
    mysqldb.commit()
    mysqldb.select_db(db_name)
except Exception as e:
    mysqldb.rollback()
    mysqldb.close()
