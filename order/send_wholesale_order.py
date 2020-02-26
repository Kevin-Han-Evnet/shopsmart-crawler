#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''

import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )


import datetime
import time as tm
import mysql.connector as pymysql
from common.config import mydb
from common.config import WholsaleOrderUtil
from common.utils import SmLogger


cursor = mydb.cursor()
wsUtil = WholsaleOrderUtil ()


lastnight11 = datetime.datetime.now ().replace (hour=23, minute=10, second=0, microsecond=0) - datetime.timedelta(days=1)
tonight11 = datetime.datetime.now ().replace (hour=23, minute=0, second=0, microsecond=0)

qry = "SELECT DISTINCT shop_id FROM " + TBL_WS_ORDER + " WHERE order_stat=0 AND reg_date > '" + str (lastnight11) + "';"
SmLogger.info (SmLogger, qry)
cursor.execute(qry)
shop_ids = cursor.fetchall ()


done_list = []
for shop_id in shop_ids :
    if (shop_id[0] != "") : done_list.append (shop_id[0])

w_not_in = ""
if (len(done_list) > 0) : w_not_in = " AND shop_id NOT IN (" + str (done_list)[1:-1] + ")"
where_clause = " WHERE closed=0 AND ws_ordered=0 AND vendor_contact IS NOT NULL AND vendor_contact<>''"

qry = "SELECT DISTINCT shop_id FROM " + TBL_ORDER_CRAWLING_RESULT + where_clause + w_not_in + ";"
cursor.execute (qry)
host_ids = cursor.fetchall ()

ws_items = []
qry = "SELECT * FROM " + TBL_ORDER_CRAWLING_REULST + where_clause + " AND ws_order_count>0" + w_not_in +";"

cursor.execute (qry)
ws_items = cursor.fetchall ()

optons = []
for ws_item in ws_items :
    #SmLogger.info (SmLogger, str (ws_item[0]) + " -- " + str (ws_item[1]) + " -- " + str (ws_item[2]) + " --- "+ str (ws_item[7]))

    options = []
    options = str (ws_item[7]).split (",")
    option_1 = ""
    option_2 = ""
    option_3 = ""



    if (len (options) > 0) : option_1 = str (options[0])
    if (len (options) > 1) : option_2 = str (options[1])
    if (len (options) > 2) : optons_3 = str (options[2])


    wsUtil.addInsertItem (ws_item[2],
                          ws_item[13],
                          ws_item[6],
                          option_1,
                          option_2,
                          option_3,
                          ws_item[10],
                          ws_item[15])


cursor.execute (wsUtil.insertQRY)


qry = "UPDATE " + TBL_ORDER_CRAWLING_RESULT + " SET ws_ordered=1, ws_order_auto=1, closed=1, ws_order_date='" + str (datetime.datetime.now ().replace (microsecond=0)) + "'" + where_clause + w_not_in + ";"
cursor.execute (qry)
SmLogger.info (SmLogger, "최종 --> " + qry)

#닫자...
mydb.commit ()
mydb.close ()