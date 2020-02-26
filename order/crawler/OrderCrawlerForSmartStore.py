#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''

import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

from bs4 import BeautifulSoup as bs
import time as tm
from warnings import catch_warnings
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
WAIT_DURATION = 3

#system sleep duration -- second
SLEEP_DURATION = 3

#page load time out
PAAGE_LOAD_TIMEOUT = 30


base_file_url = '/var/www/html/shopsmart/apis/files/'
CRAWLING_INFO_IDX = -1;
SHOP_ID = "";

PAGE_COUNT = 50
LOGIN_PAGE = 'https://sell.smartstore.naver.com/#/login'
ORDER_PAGE = 'https://sell.smartstore.naver.com/#/naverpay/manage/order'

PLATFORM_ID = ''
ID_FIELD_NAME = 'loginId'
ID = ''
PWD_FIELD_NAME = 'loginPassword'
PWD = ''

F_SPACE = "    |    "
space = "        |        "

cursor = mydb.cursor()
MAX_CHECKED_ASIS = 0;
MAX_CHECKED_TOBE = 1;
DUP_ASSET = None

PLATFORM_TYPE = 4


#고고고
gUtil = GeneralUtil (SHOP_ID, PAAGE_LOAD_TIMEOUT, WAIT_DURATION, MAX_CHECKED_TOBE, CRAWLING_INFO_IDX, PLATFORM_TYPE)


def login (driver) : 
    # url에 접근한다.
    driver.get(LOGIN_PAGE)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
    
    
    # 아이디/비밀번호를 입력해준다.
    driver.find_element_by_id(ID_FIELD_NAME).send_keys(ID)
    driver.find_element_by_id(PWD_FIELD_NAME).send_keys(PWD)
    
    
    # 로그인 후 작업하자.
    driver.find_element_by_id("loginButton").click()



#데이타 베이스 저장
def saveItems (pNum, articles) :
    
    
    global MAX_CHECKED_ASIS
    global MAX_CHECKED_TOBE
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + str (pNum) + " 페이지 " + str (len(articles)) + "개의 주문서 저장 시도")
    
    save_success_count = 0;
    save_failed_count = 0;
    
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
        
        t = ""
        vendor_name = ""
        vendor_location = ""
        
        total_cnt = len(articles)
        half_pos = int (total_cnt / 2)
       
        for i in range (0, half_pos) :
            
                objs = articles[i].select('td')
                headerObjs = articles[i + half_pos].select('td')
                
                vendor_name = ""
                vendor_location = ""
                
                #if (len(objs) > 3) :
                #    SmLogger.info (SmLogger, headerObjs[1].text.strip () + " || " + headerObjs[2].text.strip () + " --> " + objs[0].text.strip () + " --- " + objs[1].text.strip () + " --- " + objs[2].text.strip () + " --- " + objs[3].text.strip ())


                product_name = gUtil.getProductName (objs[3].text)
                product_option = gUtil.getProductOption (objs[4].text)
                check_dup_code = product_name + "-" + product_option
                order_count = int (gUtil.getNumeric (objs[5].text.strip ()))
                stock_count = 0
                ws_order_count = 0
                if (order_count - stock_count >= 0) : ws_order_count = order_count - stock_count
                coast = 0 
                price = 0
                vendor_info = objs[1].text.strip () + " -- " + objs[2].text.strip ()
                vendor_contact = "no information"
                vendor_name = "no inormation"
                vendor_location = "no imformation"

                """ --> 테이블 및 정보 변경해서 다시 작업할것.
                try :
                    cursor.execute ("INSERT INTO " + Tables.TBL_MEMBERSHIP + " (vendor_name, vendor_contact, vendor_location) VALUES ('" + vendor_name + "', '" + vendor_contact + "', '" + vendor_location + "');")
                    mydb.commit()
                except :
                    #nothing;
                    pass
                """



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
                
                
    
        SmLogger.info (SmLogger, os.path.basename(__file__) + str (pNum) + " 페이지 " + str (save_success_count) + "개의 주문서 저장 성공, " + str (save_failed_count) + "개의 주문서 저장 실패")
    
    finally :
        mydb.commit ()
        #mydb.close () --> 위에서 최종적으로 할겨..
        pass
    


def getItems ():
    
    global SLEEP_DURATION
    global MAX_CHECKED_ASIS
    global MAX_CHECKED_TOBE
    
    
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


    dt = datetime.datetime.now()
    driver = gUtil.initWebDriver ()
    
    
    try :
        
        
        login (driver)
        tm.sleep (SLEEP_DURATION)
        
        tURL = ORDER_PAGE
        
        driver.get (tURL)
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
       
        tm.sleep(SLEEP_DURATION)
        
        driver.switch_to.frame('__naverpay')
        tm.sleep(SLEEP_DURATION)
        
        
        soup = bs(driver.page_source.strip (), 'html.parser')
        articles = soup.select('div._body.body > div._table_container > table > tbody > tr')
        
        
        saveItems(1, articles)
        
        tm.sleep(SLEEP_DURATION)
        
        
        if (len(articles) < PAGE_COUNT) : 
            driver.quit ();
            gUtil.checkAndCloseOrder ()
        else : 
            getNextPageItems (2, driver) 
    
        
        
        
        
    finally :
        driver.quit ();
        pass
        
    
        
def getNextPageItems (pNum, driver) :
    
    global WAIT_DURATION
    global SLEEP_DURATION
    
    try :
        
        driver.execute_script("fetch (" + str (pNum) + ");") 
        
        tm.sleep(2)
        soup = bs(driver.page_source.strip (), 'html.parser')
        
        articles = soup.select('#dataList > tbody > tr')
        saveItems(pNum, articles)
        
        
        if (len(articles) < PAGE_COUNT) : 
            driver.quit ();
            gUtil.checkAndCloseOrder ()
        else : 
            getNextPageItems (int(pNum) + 1, driver) 
        
    finally :
        driver.quit ();
        gUtil.checkAndCloseOrder ()
        pass
    














    