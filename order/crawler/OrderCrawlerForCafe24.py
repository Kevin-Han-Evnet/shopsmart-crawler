#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''

import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as bs
import time as tm
from warnings import catch_warnings
from urllib import parse
from urllib import request as request
from operator import getitem
import datetime
import errno
import math
from common.config import mydb
from common.config import GeneralUtil
from common.config import Tables
import uuid
from common.utils import SmLogger

#implicitly_wait -- second
WAIT_DURATION = 5

#system sleep duration -- second
SLEEP_DURATION = 5

#page load time out
PAGE_LOAD_TIMEOUT = 30


base_file_url = '/var/www/html/shopsmart/apis/files/'
CRAWLING_INFO_IDX = -1;
SHOP_ID = "";
PAGE_COUNT = 50
LOGIN_PAGE = 'https://eclogin.cafe24.com/Shop/?url=Init&login_mode=2&is_multi=F'
ORDER_PAGE = 'https://planbco.cafe24.com/admin/php/shop1/s_new/shipped_before_product_list.php#none'
PLATFORM_ID_FIELD_NAME = 'mall_id'
PLATFORM_ID = ''
ID_FIELD_NAME = 'userid'
ID = ''
PWD_FIELD_NAME = 'userpasswd'
PWD = ''
LOGIN_FORM = 'frm_user'

PAGE_NUM = 0;


space = "        |        "

cursor = mydb.cursor()

MAX_CHECKED_ASIS = 0;
MAX_CHECKED_TOBE = 1;
DUP_ASSET = None

PLATFORM_TYPE = 1



#고고고
gUtil = GeneralUtil (SHOP_ID, PAGE_LOAD_TIMEOUT, WAIT_DURATION, MAX_CHECKED_TOBE, CRAWLING_INFO_IDX, PLATFORM_TYPE)


def login (driver) :
    # url에 접근한다.
    driver.get(LOGIN_PAGE)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

    # 아이디/비밀번호를 입력해준다.
    driver.find_element_by_name(PLATFORM_ID_FIELD_NAME).send_keys(PLATFORM_ID)
    driver.find_element_by_name(ID_FIELD_NAME).send_keys(ID)
    driver.find_element_by_name(PWD_FIELD_NAME).send_keys(PWD)


    # 로그인 후 작업하자.
    driver.find_element_by_name(LOGIN_FORM).submit()


#데이타 베이스 저장
def saveItems (articles) :

    global WAIT_DURATION
    global SLEEP_DURATION
    global PAGE_NUM
    global MAX_CHECKED_ASIS
    global MAX_CHECKED_TOBE


    save_success_count = 0;
    save_failed_count = 0;

    SmLogger.info (SmLogger, os.path.basename(__file__), str (PAGE_NUM) + " 페이지 " + str(len(articles)) + "개의 주문서 저장 시도")

    try :


        crawling_info_idx = CRAWLING_INFO_IDX
        shop_id = SHOP_ID
        check_dup_code = ""
        product_name = ""
        product_option = ""
        order_count = 0
        stock_count = 0
        ws_order_count = 0
        coast = 0
        price = 0
        vendor_info = ""
        vendor_contact = ""

        for article in articles :
            objs = article.select('tr > td')

            if (len(objs) > 12) :

                product_name = gUtil.getProductName(objs[7].text)
                product_option = gUtil.getProductOption(objs[8].text)
                check_dup_code = product_name + "-" + product_option
                order_count = int (gUtil.getHtmlText(objs[10].text.strip()))
                stock_count = int (gUtil.getHtmlText(objs[11].text.strip()))
                ws_order_count = 0
                if (order_count - stock_count >= 0) : ws_order_count = order_count - stock_count
                coast = 0 #gUtil.getHtmlText(objs[9].text.strip())
                price = 0
                vendor_info = gUtil.getHtmlText(objs[6].text.strip())
                vendor_contact = ""

                dup_sel_qry = "SELECT idx FROM " + Tables.TBL_ORDER_CRAWLING_RESULT + " WHERE check_dup_code='" + check_dup_code + "' AND crawling_info_idx=" + str (CRAWLING_INFO_IDX) + " AND closed=0;"
                cursor.execute (dup_sel_qry)
                DUP_ASSET = cursor.fetchall ()

                if (DUP_ASSET == None or len (DUP_ASSET) == 0) :
                    gUtil.addInsertItem (check_dup_code,
                                  product_name,
                                  product_option,
                                  order_count,
                                  stock_count,
                                  ws_order_count,
                                  coast,
                                  price,
                                  vendor_info,
                                  vendor_contact)

                elif (DUP_ASSET[0][0] in gUtil.t_update_order_idxs) :

                    check_dup_code = check_dup_code + "-" + str (uuid.uuid4())
                    gUtil.addInsertItem(check_dup_code,
                                  product_name,
                                  product_option,
                                  order_count,
                                  stock_count,
                                  ws_order_count,
                                  coast,
                                  price,
                                  vendor_info,
                                  vendor_contact)

                    gUtil.t_dup_update_order_idxs.append (DUP_ASSET[0][0])

                else :
                    gUtil.addUpdateItem(DUP_ASSET[0][0], order_count, stock_count, ws_order_count)


                option_count = (len(objs) - 13) / 3 #--> 13번째 컬럼가지 첫번째 옵션.. 그이후로 더 있다면 동일한 제품의 옵션들이다. 컬럼갯수는 3개씩.
                if (math.ceil(option_count) > 0) :

                    start = 13
                    for i in range (0, math.ceil(option_count)) :

                        product_option = gUtil.getProductOption(objs[start].text)
                        check_dup_code = product_name + "-" + product_option
                        order_count = gUtil.getHtmlText(objs[start + 1].text.strip())
                        stock_count = gUtil.getHtmlText(objs[start + 2].text.strip())
                        ws_order_count = 0
                        if (int (order_count) - int (stock_count) >= 0) : ws_order_count = int (order_count) - int (stock_count)

                        dup_sel_qry = "SELECT idx FROM " + Tables.TBL_ORDER_CRAWLING_RESULT + " WHERE check_dup_code='" + check_dup_code + "' AND crawling_info_idx=" + str (CRAWLING_INFO_IDX) + " AND closed=0;"
                        cursor.execute (dup_sel_qry)
                        DUP_ASSET = cursor.fetchall ()


                        if (DUP_ASSET == None or len (DUP_ASSET) == 0) :
                            gUtil.addInsertItem(
                                          check_dup_code,
                                          product_name,
                                          product_option,
                                          order_count,
                                          stock_count,
                                          ws_order_count,
                                          coast,
                                          price,
                                          vendor_info,
                                          vendor_contact)

                        elif (DUP_ASSET[0][0] in gUtil.t_update_order_idxs) :

                            check_dup_code = check_dup_code + "-" + str (uuid.uuid4())
                            gUtil.addInsertItem(
                                          check_dup_code,
                                          product_name,
                                          product_option,
                                          order_count,
                                          stock_count,
                                          ws_order_count,
                                          coast,
                                          price,
                                          vendor_info,
                                          vendor_contact)

                            gUtil.t_dup_update_order_idxs.append (DUP_ASSET[0][0])


                        else :
                            gUtil.addUpdateItem(DUP_ASSET[0][0], order_count, stock_count, ws_order_count)

                        start += 3




                try :

                    if (gUtil.insertQRY != "") :
                        cursor.execute(gUtil.insertQRY)

                    updateQRY = gUtil.getUpdateQRY ()
                    if (updateQRY != "") :
                        cursor.execute (updateQRY)

                    save_success_count += 1
                    tm.sleep(0.5)


                except (RuntimeError, TypeError, NameError, pymysql.err.IntegrityError) :
                    save_failed_count += 1
                    SmLogger.info (SmLogger, "SQL 실패 ----- ")
                    pass

                gUtil.insertQRY = ""
                updateQRY = ""
                gUtil.updateInfoList.clear()

            else :
                save_failed_count += 1


        SmLogger.info (SmLogger, os.path.basename(__file__), str (PAGE_NUM) + " 페이지 " + str(save_success_count) + "개의 주문서 저장 성공, " + str(save_failed_count) + "개의 주문서 저장 실패(주문서가 이닌 object)")

    finally :
        #데이타 저장 성공 후에는 대기시간 되돌림.
        WAIT_DURATION = 3
        SLEEP_DURATION = 10
        mydb.commit ()
        #mydb.close () --> 위에서 최종적으로 할겨..





def getItems ():

    global WAIT_DURATION
    global SLEEP_DURATION
    global PAGE_NUM
    global MAX_CHECKED_ASIS
    global MAX_CHECKED_TOBE
    global gUtil

    #1차 max 값을 뽑아낸다.
    qry = "SELECT MAX(checked) FROM " + Tables.TBL_ORDER_CRAWLING_RESULT + " WHERE crawling_info_idx=" + str (CRAWLING_INFO_IDX) + ";"
    cursor.execute(qry)
    dupT = cursor.fetchone ()


    if (dupT is None or dupT[0] is None) :
        MAX_CHECKED_ASIS = 0
    else :
        MAX_CHECKED_ASIS = int (dupT[0])

    MAX_CHECKED_TOBE = MAX_CHECKED_ASIS + 1
    gUtil.MAX_CHECKED_TOBE = MAX_CHECKED_TOBE
    gUtil.SHOP_ID = SHOP_ID
    gUtil.CRAWLING_INFO_IDX = CRAWLING_INFO_IDX

    PAGE_NUM += 1;


    dt = datetime.datetime.now()
    driver = gUtil.initWebDriver ()


    SmLogger.info (SmLogger, os.path.basename(__file__), str (PAGE_NUM) + " 페이지 주문서 페이지 요청")
    try :


        login (driver)
        tm.sleep (SLEEP_DURATION)


        driver.get(ORDER_PAGE)
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")


        driver.implicitly_wait (WAIT_DURATION)
        driver.find_element_by_id('eBtnSearch').click()
        tm.sleep(SLEEP_DURATION)

        soup = bs(driver.page_source.strip (), 'html.parser')

        #searchResultList > tbody:nth-child(3)
        articles = soup.select('form > div > div > div > table > tbody')

        saveItems(articles)


        tm.sleep(SLEEP_DURATION)

        if (len(articles)) :
            getNextPageItems (2, driver)
        else :
            driver.quit ()
            gUtil.checkAndCloseOrder ()

    finally :
        driver.quit ()
        gUtil.checkAndCloseOrder ()


def getNextPageItems (pNum, driver) :

    global WAIT_DURATION
    global SLEEP_DURATION
    global PAGE_NUM

    PAGE_NUM += 1

    SmLogger.info (SmLogger, os.path.basename(__file__), str (PAGE_NUM) + " 페이지 주문서 페이지 요청")
    driver.implicitly_wait (WAIT_DURATION)
    try :
        driver.find_element_by_xpath('//*[@id="QA_prepareProduct2"]/div[7]/a[2]').click()
        soup = bs(driver.page_source.strip (), 'html.parser')

        #searchResultList > tbody:nth-child(3)
        articles = soup.select('form > div > div > div > table > tbody')

        saveItems(articles)

        tm.sleep(SLEEP_DURATION)


        next_link = driver.find_element_by_xpath('//*[@id="QA_prepareProduct2"]/div[7]/a[2]').get_attribute('href')[-4:]

        if (len(articles) > 4 and next_link != "none") :
            getNextPageItems (int(pNum) + 1, driver)
        else :
            driver.quit ()
            gUtil.checkAndCloseOrder ()

    except TimeoutException as ex:
        SmLogger.info (SmLogger, os.path.basename(__file__), str (PAGE_NUM) + "페이지 요청 -- Exception has been thrown. " + str(ex))
        driver.quit ()
        gUtil.checkAndCloseOrder ()
        
        
            









    
    
    