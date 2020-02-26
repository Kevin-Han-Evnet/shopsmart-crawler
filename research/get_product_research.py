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
from common.utils import SmLogger
import datetime
from dateutil.relativedelta import relativedelta


#import crawler.NewProductCrawler as NewProductCrawler
#import crawler.EventCrawler as EventCrawler

from research.crawler import NewProductCrawler
from research.crawler import EventCrawler



#으으음 ㅋㅋㅋ
#신상품 크롤링
def getNewProductList (pNum, research_idx, target_name, crawling_engine, np_url, tag_selector, sub_tag_selector, img_tag_selector, np_code_name, not_nessesary_strings) :

    global NewProductCrawler
    
    NewProductCrawler.target_name = target_name
    NewProductCrawler.NP_URL = np_url
    NewProductCrawler.tag_selector = tag_selector
    NewProductCrawler.sub_tag_selector = sub_tag_selector
    NewProductCrawler.img_tag_selector = img_tag_selector
    NewProductCrawler.research_idx = research_idx
    NewProductCrawler.np_code_name = np_code_name
    NewProductCrawler.not_nessesary_strings = not_nessesary_strings
    NewProductCrawler.crawling_engine = crawling_engine
    
    itemcount = NewProductCrawler.getItems(pNum)

    if (itemcount > 0) : getNewProductList (pNum + 1, research_idx, target_name, crawling_engine, np_url, tag_selector, sub_tag_selector, img_tag_selector, np_code_name, not_nessesary_strings)
    
    
#이벤트 크롤링 -- 메롱
def getEventList (pNum, research_idx, target_name, crawling_engine, event_url, tag_selector, sub_tag_selector, img_tag_selector, event_code_name, not_nessesary_strings) :
    
    EventCrawler.target_name = target_name
    EventCrawler.EVENT_URL = event_url
    EventCrawler.tag_selector = tag_selector
    EventCrawler.sub_tag_selector = sub_tag_selector
    EventCrawler.img_tag_selector = img_tag_selector
    EventCrawler.research_idx = research_idx
    EventCrawler.event_code_name = event_code_name
    EventCrawler.not_nessesary_strings = not_nessesary_strings
    EventCrawler.crawling_engine = crawling_engine

    itemcount = EventCrawler.getItems(pNum)

    if (int (itemcount) > 0) : getEventList (pNum + 1, research_idx, target_name, crawling_engine, event_url, tag_selector, sub_tag_selector, img_tag_selector, event_code_name, not_nessesary_strings)
    




def doIt ():
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"====================================================================================")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")


    mydb = SDB.getDB()
    cursor = mydb.cursor(buffered=True , dictionary=True)
    cursor.execute("SELECT * FROM " + Tables.TBL_RESEARCH_INFO + ";")
    research_list = cursor.fetchall()

    if (len (research_list) > 0) :
        for research in research_list :

            if (int(research['np_crawling_stat']) == 1) :

                SmLogger.info (SmLogger, os.path.basename(__file__) + " " + research['target_name'] + " 신상품 크롤링 시작 --- ")
                getNewProductList (1, research['idx'], research['target_name'], research['crawling_engine'], research['np_list_page'], research['np_tag_selector'],
                                   research['np_sub_tag_selector'], research['np_img_tag_selector'], research['np_code_name'], research['np_not_nessesary_strings'])
                SmLogger.info (SmLogger, os.path.basename(__file__) + " " +research['target_name'] + " 신상품 크롤링 끝 --- ")

                sql = "UPDATE " + Tables.TBL_RESEARCH_INFO + " SET np_count=(SELECT COUNT(*) FROM " + Tables.TBL_NP_CRAWLING_RESULT + " WHERE crawling_info_idx=" + str(research['idx']) + ") WHERE idx=" + str(research['idx']) + ";"
                cursor.execute (sql)
                mydb.commit()



            if (int(research['event_crawling_stat']) == 1) :
                SmLogger.info (SmLogger, os.path.basename(__file__) + " " +research['target_name'] + " 이벤트 크롤링 시작 --- ")
                getEventList (1, research['idx'], research['target_name'], research['crawling_engine'], research['event_list_page'], research['event_tag_selector'], research['event_sub_tag_selector'], research['event_img_tag_selector'],
                              research['event_code_name'], research['event_not_nessesary_strings'])
                SmLogger.info (SmLogger, os.path.basename(__file__) + " " +research['target_name'] + " 이벤트 크롤링 끝 --- ")

                sql = "UPDATE " + Tables.TBL_RESEARCH_INFO + " SET event_count=(SELECT COUNT(*) FROM " + Tables.TBL_EVENT_CRAWLING_RESULT + " WHERE crawling_info_idx=" + str(research['idx']) + ") WHERE idx=" + str(research['idx']) + ";"
                cursor.execute (sql)
                mydb.commit()





    else :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"크롤링 대상 없음 -------------------------------------------------------- ")

    mydb.close ()

    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"====================================================================================")
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " +"\n\n\n")


doIt()