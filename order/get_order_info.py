#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''

import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

import time as tm
import mysql.connector as pymysql

import crawler.OrderCrawlerForCafe24 as crawlerForCafe24
import crawler.OrderCrawlerForSellMate as crawlerForSellMate
import crawler.OrderCrawlerForMakeShop as crawlerForMakeShop
import crawler.OrderCrawlerForSmartStore as crawlerForSmartStore
from common.config import mydb
from common.config import Tables

from common.utils import HashUtils as hashUtil
from common.utils import SmLogger


SmLogger.info (SmLogger, os.path.basename(__file__) + "\n\n\n")
SmLogger.info (SmLogger, os.path.basename(__file__) +"====================================================================================")
SmLogger.info (SmLogger, os.path.basename(__file__) + "\n\n\n")

#실행해 보자 -- 카페24
def getOrderListForCafe24 (pNum, crawling_info_idx, shop_id, platform_id, user_id, user_pwd) :
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (카페24) 주문서 크롤링 시작 -------------------------------------------------------- ")
    crawlerForCafe24.CRAWLING_INFO_IDX = crawling_info_idx;1
    crawlerForCafe24.SHOP_ID = shop_id
    crawlerForCafe24.PLATFORM_ID = platform_id
    crawlerForCafe24.ID = user_id
    crawlerForCafe24.PWD = user_pwd

    crawlerForCafe24.getItems ()
    """ try :
        crawlerForCafe24.getItems ()
    except Exception as ex :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " -- 에러 발생 --> " + str (ex)) """
    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (카페24) 주문서 크롤링 끝 -------------------------------------------------------- ")



#실행해 보자 -- 셀메이트
def getOrderListForSellMate (pNum, crawling_info_idx, shop_id, platform_id, user_id, user_pwd) :
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (셀메이트) 주문서 크롤링 시작 -------------------------------------------------------- ")
    crawlerForSellMate.CRAWLING_INFO_IDX = crawling_info_idx;
    crawlerForSellMate.SHOP_ID = shop_id
    crawlerForSellMate.PLATFORM_ID = platform_id
    crawlerForSellMate.ID = user_id
    crawlerForSellMate.PWD = user_pwd

    crawlerForSellMate.getItems ()
    """ try :
        crawlerForSellMate.getItems ()
    except Exception as ex :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " -- 에러 발생 --> " + str (ex)) """
    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (셀메이트) 주문서 크롤링 끝 -------------------------------------------------------- ")




#실행해 보자 -- 메이크샵
def getOrderListForMakeShop (pNum, crawling_info_idx, shop_id, account_type, platform_id, user_id, user_pwd, login_url) :

    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (메이크샵) 주문서 크롤링 시작 -------------------------------------------------------- ")
    crawlerForMakeShop.CRAWLING_INFO_IDX = crawling_info_idx;
    crawlerForMakeShop.SHOP_ID = shop_id
    crawlerForMakeShop.PLATFORM_ID = platform_id
    crawlerForMakeShop.ID = user_id
    crawlerForMakeShop.PWD = user_pwd
    crawlerForMakeShop.ACCOUNT_TYPE = int(account_type)
    crawlerForMakeShop.LOGIN_PAGE = (str(login_url))

    crawlerForMakeShop.getItems ()
    """ try :
        crawlerForMakeShop.getItems ()
    except Exception as ex :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " -- 에러 발생 --> " + str (ex)) """
    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (메이크샵) 주문서 크롤링 끝 -------------------------------------------------------- ")


#실행해 보자 -- 스토어팜 (스마트스토어)
def getOrderListForSmartStore (pNum, crawling_info_idx, shop_id, user_id, user_pwd) :

    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (스마트스토어) 주문서 크롤링 시작 -------------------------------------------------------- ")
    crawlerForSmartStore.CRAWLING_INFO_IDX = crawling_info_idx;
    crawlerForSmartStore.SHOP_ID = shop_id
    crawlerForSmartStore.ID = user_id
    crawlerForSmartStore.PWD = user_pwd

    crawlerForSmartStore.getItems ()
    """ try :
        crawlerForSmartStore.getItems ()
    except Exception as ex :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " -- 에러 발생 --> " + str (ex)) """
    SmLogger.info (SmLogger, os.path.basename(__file__) + " -- " + str (shop_id) + " 쇼핑몰 (스마트스토어) 주문서 크롤링 끝 -------------------------------------------------------- ")




cursor = mydb.cursor(buffered=True , dictionary=True)

cursor.execute("SELECT * FROM " + Tables.TBL_MEMBERSHIP + " WHERE type='SMART';")
shops = cursor.fetchall ()

for shop in shops :
    SmLogger.info (SmLogger, os.path.basename(__file__) +  str (shop['membership_seq']) + " | " + str (shop['comp_nm']) + " | " + str (shop['sid']) + " 주문서 -------------------------------------------------------------------")

    cursor.execute("SELECT * FROM " + Tables.TBL_ORDER_CRAWLING_INFO + " WHERE disabled=0 AND membership_seq=" + str (shop['membership_seq']) + ";")
    order_platforms = cursor.fetchall()

    user_pwd = ""

    if (len (order_platforms) > 0 and shop['key_32'] != '') :
        for order_platform in order_platforms :

            #사용자 계정 비번 복호화
            user_pwd = hashUtil.getUnHashedPwd(shop['key_32'], shop['key_16'], order_platform['user_pwd'])

            tm.sleep(2)

            if (str (order_platform['platform_type']) == 'CAFE24') :
                getOrderListForCafe24 (1, order_platform['idx'], order_platform['membership_seq'], order_platform['platform_id'], order_platform['user_id_k'], user_pwd)
                pass
            elif (str (order_platform['platform_type']) == 'SELMATE') :
                getOrderListForSellMate (1, order_platform['idx'], order_platform['membership_seq'], order_platform['platform_id'], order_platform['user_id_k'], user_pwd)
                pass
            elif (str (order_platform['platform_type']) == 'MAKESHOP') :
                getOrderListForMakeShop (1, order_platform['idx'], order_platform['membership_seq'], order_platform['account_type'], order_platform['platform_id'], order_platform['user_id_k'], user_pwd, order_platform['login_url'])
                pass
            elif (str (order_platform['platform_type']) == 'SMARTSTORE') :
                getOrderListForSmartStore (1, order_platform['idx'], order_platform['membership_seq'], order_platform['user_id_k'], user_pwd)
                pass
    else :
        SmLogger.info (SmLogger, os.path.basename(__file__) +  "주문서 크롤링 정보 없음 -------------------------------------------------------------------")




mydb.commit ()
mydb.close ()


SmLogger.info (SmLogger, os.path.basename(__file__) +  "\n\n\n")
SmLogger.info (SmLogger, os.path.basename(__file__) +  "====================================================================================")
SmLogger.info (SmLogger, os.path.basename(__file__) +  "\n\n\n")


