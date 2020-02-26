#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''

import shutil
import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

import time as tm
import mysql.connector as pymysql

import sender.SendProductToSM as productSender
from common.config import mydb
from common.config import base_file_url
from common.utils import SmLogger


SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "\n\n\n")
SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "====================================================================================")
SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "\n\n\n")

#실행해 보자 
def sendProductToSM (vendor_code, vendor_name, sm_id, sm_pwd) :
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (vendor_name) + " 쇼핑몰 제품 신상마켓 전송 시작 -------------------------------------------------------- ")
    productSender.VENDOR_CODE = str (vendor_code);
    productSender.ID = str (sm_id)
    productSender.PWD = str (sm_pwd)
    
    
    try :
        productSender.sendProduct ()
    except Exception as ex :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (vendor_name) + "에러 발생 --> " + str (ex))
    
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (vendor_name) + " 쇼핑몰 제품 신상마켓 전송 끝 -------------------------------------------------------- ")

cursor = mydb.cursor()


cursor.execute("SELECT * FROM tbl_vendor WHERE sm_sync=1;")
shops = cursor.fetchall()

if (len (shops) > 0) :
    for shop in shops :
        tm.sleep(2)
        sendProductToSM (shop[0], shop[1], shop[5], shop[6])
else :
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "신상 마켓 연동 업체 없음 -------------------------------------------------------------------")
    
    
    
    
mydb.close ()

try :
    shutil.rmtree (base_file_url + "product_images")         
except :
    pass 


SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "\n\n\n")
SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "====================================================================================")
SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "\n\n\n")


