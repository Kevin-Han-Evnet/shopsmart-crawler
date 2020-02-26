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
PAAGE_LOAD_TIMEOUT = 30


base_file_url = '/var/www/html/shopsmart/apis/files/'
CRAWLING_INFO_IDX = -1
SHOP_ID = ""
PLATFORM_ID = ''
PAGE_COUNT = 50
LOGIN_PAGE = ''
ACCOUNT_TYPE = 0
ORDER_PAGE = 'https://special50.makeshop.co.kr/makeshop/oomanager/oo_search_form.html?listType=readyDeliveryList'
ID_FIELD_NAME = 'id'
ID = ""
PWD_FIELD_NAME = 'passwd'
PWD = ""
LOGIN_FORM = 'loginform'




space = "        |        "
cursor = mydb.cursor()
MAX_CHECKED_ASIS = 0
MAX_CHECKED_TOBE = 1
DUP_ASSET = None

PLATFORM_TYPE = 3


#고고고
gUtil = GeneralUtil (SHOP_ID, PAAGE_LOAD_TIMEOUT, WAIT_DURATION, MAX_CHECKED_TOBE, CRAWLING_INFO_IDX, PLATFORM_TYPE)

def login (driver) : 
    # url에 접근한다.
    driver.get(LOGIN_PAGE)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

    
    if (ACCOUNT_TYPE == 1) :
        driver.execute_script("arguments[0].click();", driver.find_element_by_xpath('//*[@id="logintabWrap"]/ul/li[1]/label'))
    elif (ACCOUNT_TYPE == 2) :
        driver.execute_script("arguments[0].click();", driver.find_element_by_xpath('//*[@id="logintabWrap"]/ul/li[2]/label'))
    
    # 아이디/비밀번호를 입력해준다.
    driver.find_element_by_name(ID_FIELD_NAME).send_keys(ID)
    driver.find_element_by_name(PWD_FIELD_NAME).send_keys(PWD)
    
    # 로그인 후 작업하자.
    driver.find_element_by_name(LOGIN_FORM).submit()



def saveItems (articles) :
    
    global MAX_CHECKED_ASIS
    global MAX_CHECKED_TOBE
    
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
            objs = article.select('td')

            dup_sel_qry = "SELECT idx FROM " + Tables.TBL_ORDER_CRAWLING_RESULT + " WHERE check_dup_code='" + check_dup_code + "' AND crawling_info_idx=" + str (CRAWLING_INFO_IDX) + " AND closed=0;"
            cursor.execute (dup_sel_qry)
            DUP_ASSET = cursor.fetchall ()
            
            if (len(objs) > 3) :
                
                str_items = ""
                crawling_info_idx = CRAWLING_INFO_IDX
                shop_id = SHOP_ID
                product_name = gUtil.getProductName(str (objs[3].text))
                product_option = gUtil.getProductOption(objs[4].text)
                check_dup_code = product_name + "-" + product_option
                order_count = int (gUtil.getHtmlText(objs[5].text.strip()))
                stock_count = int (gUtil.getHtmlText(objs[6].text.strip()))
                ws_order_count = 0
                if (order_count - stock_count >= 0) : ws_order_count = order_count - stock_count
                coast = getNumeric (objs[7].text.strip ())
                coast = 0
                price = 0
                vendor_info = ""
                vendor_contact = ""


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

                
            else :
                
                product_option = gUtil.getProductOption(objs[0].text)
                check_dup_code = product_name + "-" + product_option
                order_count = int (gUtil.getHtmlText(objs[1].text.strip()))
                stock_count = gUtil.getHtmlText(objs[2].text.strip())

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
    
                    
    
    finally :
        mydb.commit ()
        #mydb.close () --> 위에서 최종적으로 할겨..
        pass
    



def getItems ():
    
    global WAIT_DURATION
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
        
        
    
        driver.get(ORDER_PAGE)
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
        
        
        driver.implicitly_wait (WAIT_DURATION)
        tm.sleep(SLEEP_DURATION)
        
        driver.find_element_by_xpath('//*[@id="orderManager"]/div[3]/div[2]/fieldset/div[9]/ul/li[3]/a').click()
        driver.implicitly_wait (WAIT_DURATION)
        tm.sleep(SLEEP_DURATION)
        
        soup = bs(driver.page_source.strip (), 'html.parser')
        
        #searchResultList > tbody:nth-child(3)
        articles = soup.select('#productSort > table > tbody > tr')
        
        
        saveItems(articles)
        tm.sleep(SLEEP_DURATION)
        
        #현재 한페이지 밖에 없는 관계로 다음페이지 구현에 어려윰이 있다. 내일하자...
        """
        if (len(articles)) : 
            getNextPageItems (2, driver) 
        else : 
            driver.quit ();
            gUtil.checkAndCloseOrder ()
        """
        
    finally :
        driver.quit ()
        gUtil.checkAndCloseOrder ()
        
        
    
def getNextPageItems (pNum, driver) :
    
    driver.implicitly_wait (WAIT_DURATION)
    
    
    """
    if (len(articles) > 4 and next_link != "none") :
        getNextPageItems (int(pNum) + 1, driver)
    else : 
        driver.quit ();
        gUtil.checkAndCloseOrder () 
    """


#로컬 테스트 (서버 릴리즈일때 지울것) -----------------------------------    
"""
SHOP_ID = "annpiona"
ID = "ann_nhncs2"
PWD = "rlaxogh!1"
    
getItems ()
"""
#로컬 테스트 (서버 릴리즈일때 지울것) -----------------------------------  
    
    
    
    