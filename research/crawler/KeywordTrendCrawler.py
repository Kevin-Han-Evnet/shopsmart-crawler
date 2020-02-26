#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 22.

@author: kevinhan
'''


import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

from urllib import request as request
import json
import datetime
import time as tm
import mysql.connector as pymysql
from macpath import split
import base64
from common.config import ShopsmartDB as SDB
from common.config import Tables
from common.utils import SmLogger
import logging
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

target_name = ''
client_id = "8TX0MWJ5mDqUGm99E1Vt"
client_secret = "vZ7vcVQsjT"
url = "https://openapi.naver.com/v1/datalab/search";


mydb = SDB.getDB()
cursor = mydb.cursor()
    
    
    
def svaeData (research_idx, json_request, json_response) :
    global mydb
    global cursor
    
    try :
        
        cursor.execute("SELECT COUNT(*) FROM " + Tables.TBL_KEYWORD_TREND_CRAWLING_RESULT + " WHERE crawling_info_idx=" + str(research_idx) + ";")
        before_count = cursor.fetchone()
        
        if (int (before_count[0]) > 0) :
            sql = "UPDATE " + Tables.TBL_KEYWORD_TREND_CRAWLING_RESULT + " SET json_request=\"{}\", json_response=\"{}'\", reg_date=NOW() WHERE crawling_info_idx={};".format (
                base64.b64encode(str(json_request).encode('utf-8')), 
                base64.b64encode(str(json_response).encode('utf-8')),
                int (research_idx)
            )
            #SmLogger.info (SmLogger, "FUCK 1")
        else :
            sql = "INSERT INTO " + Tables.TBL_KEYWORD_TREND_CRAWLING_RESULT + " (crawling_info_idx, target_name, json_request, json_response) VALUES ({}, \"{}\", \"{}\", \"{}\");".format (
                int (research_idx),
                str (target_name),
                base64.b64encode(str(json_request).encode('utf-8')), 
                base64.b64encode(str(json_response).encode('utf-8'))
            )
            #SmLogger.info (SmLogger, "FUCK 2-->" + sql)
        
                
        cursor.execute(sql)
        mydb.commit ()
        
    except Exception as ex : 
        logging.error(ex)

    


#데이타 가와~~
def doRetrieveData (research_idx, startDate, endDate, timeUnit, keywordGroups, device, ages, gender) :
    
    global client_id
    global client_secret
    global url

    tGender = gender
    if (tGender == 'all'):
        tGender = ''

    tDevice = device
    if (tDevice == 'all'):
        tDevice = ''

    params = {
        "startDate" :   startDate,
        "endDate"   :   endDate,
        "timeUnit"  :   timeUnit,
        "keywordGroups"   :   keywordGroups,
        "device"    :   tDevice,
        "ages"      :   ages,
        "gender"    :   tGender
    }
    
    objRequest = request.Request(url)
    objRequest.add_header("X-Naver-Client-Id",client_id)
    objRequest.add_header("X-Naver-Client-Secret",client_secret)
    objRequest.add_header("Content-Type","application/json")

    response = request.urlopen(objRequest, data=json.dumps(params).encode("utf-8"))
    rescode = response.getcode()
    
    
    
    
    if(rescode==200):
        response_body = response.read()
        objResult = json.loads (response_body.decode('utf-8'))
        #testPrint (objResult)
        svaeData (research_idx, params, objResult)
        
    else:
        SmLogger.info (SmLogger, "Error Code:" + rescode)












