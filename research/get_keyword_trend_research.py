#-*- coding: utf-8 -*-
'''
Created on 2019. 6. 4.

@author: kevinhan
'''


import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

import time as tm
from common.config import ShopsmartDB as SDB
from common.config import Tables
import datetime
from dateutil.relativedelta import relativedelta

from research.crawler import KeywordTrendCrawler
from common.utils import SmLogger

#키워드 트렌드 크롤링
def getQueryCount (research_idx, target_name,
                   keywordgroup_1, keywords_1,
                   keywordgroup_2, keywords_2,
                   keywordgroup_3, keywords_3,
                   keywordgroup_4, keywords_4,
                   keywordgroup_5, keywords_5,
                   period, timeUnit, device, gender, str_ages) :

    dt = datetime.datetime.now()
    keywordGroups = []

    if (str (keywordgroup_1) != "") :
        keywordGroups.append({"groupName":str (keywordgroup_1), "keywords":str (keywords_1).split (",")})

    if (str (keywordgroup_2) != "") :
        keywordGroups.append({"groupName":str (keywordgroup_2), "keywords":str (keywords_2).split (",")})

    if (str (keywordgroup_3) != "") :
        keywordGroups.append({"groupName":str (keywordgroup_3), "keywords":str (keywords_3).split (",")})

    if (str (keywordgroup_4) != "") :
        keywordGroups.append({"groupName":str (keywordgroup_4), "keywords":str (keywords_4).split (",")})

    if (str (keywordgroup_5) != "") :
        keywordGroups.append({"groupName":str (keywordgroup_5), "keywords":str (keywords_5).split (",")})



    end_date = dt;
    start_date = dt;

    tMonth = 0

    if (int (period) == 0) :
        end_date = dt - datetime.timedelta (days=1)
        start_date = datetime.datetime(2016, 1, 1)
    elif (int (period) == 1) :
        end_date = dt - datetime.timedelta (days=1)
        start_date = dt - relativedelta (months=1)
    elif (int (period) == 2) :
        end_date = dt - datetime.timedelta (days=1)
        start_date = dt - relativedelta (months=3)
    elif (int (period) == 3) :
        end_date = dt - datetime.timedelta (days=1)
        start_date = dt - relativedelta (years=1)




    ages = str (str_ages).split (",")
    if (len(ages) <= 1) : ages = []

    KeywordTrendCrawler.target_name = target_name
    KeywordTrendCrawler.doRetrieveData(
        research_idx,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        timeUnit,
        keywordGroups,
        device,
        ages,
        gender
    )




def doIt () :
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"====================================================================================")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")


    mydb = SDB.getDB()
    cursor = mydb.cursor(buffered=True , dictionary=True)
    cursor.execute("SELECT * FROM " + Tables.TBL_KEYWORD_TREND_CRAWLING_INFO + ";")
    research_list = cursor.fetchall()

    if (len (research_list) > 0) :
        for research in research_list :

            cursor.execute("SELECT * FROM " + Tables.TBL_MEMBERSHIP + " WHERE membership_seq=" + str(research['membership_seq']) + ";")
            membership = cursor.fetchone()

            if (int(research['keyword_trend_crawling_stat']) == 1) :
                SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str(membership['comp_nm']) + " 쿼리수 크롤링 시작 --- ")
                getQueryCount (research['idx'], membership['comp_nm'],
                               research['keyword_group_1'], research['keywords_1'],
                               research['keyword_group_2'], research['keywords_2'],
                               research['keyword_group_3'], research['keywords_3'],
                               research['keyword_group_4'], research['keywords_4'],
                               research['keyword_group_5'], research['keywords_5'],
                               research['period'], research['timeUnit'], research['device'], research['gender'], research['age'])
                SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str(membership['comp_nm']) + " 쿼리수 크롤링 끝 --- ")

            tm.sleep(2)


    else :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"크롤링 대상 없음 -------------------------------------------------------- ")

    mydb.close ()

    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"====================================================================================")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")

doIt ()