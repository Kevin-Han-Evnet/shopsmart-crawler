#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''


IS_SERVER = True #--> 로컬 테스트 일대는 False 로 할것.

import os
import sys
from _codecs import utf_8_encode
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

import time as tm
from warnings import catch_warnings

if (IS_SERVER) :
    import pymysql.cursors
    

import time as tm
from operator import getitem
import datetime
import errno
import math
from common.config import mydb
from common.config import base_file_url
from common.config import s3
from common.config import bucketName
from common.config import GeneralUtil
from common.utils import SmLogger




#implicitly_wait -- second
WAIT_DURATION = 10

#system sleep duration -- second
SLEEP_DURATION = 10

#page load time out
PAGE_LOAD_TIMEOUT = 30


LOGIN_PAGE = "https://partner.sinsangmarket.kr"
PRODUCT_FORM_PAGE = "https://partner.sinsangmarket.kr/goodsRegistration"

VENDOR_CODE = "";
ID_FIELD_NAME = "userid"
ID = ""
PWD_FIELD_NAME = "passwd"
PWD = ""

ALERT_TEXT = ""

#고고고
gUtil = GeneralUtil ("", PAGE_LOAD_TIMEOUT, WAIT_DURATION, 0, 0, 0)


def initWebDriver ():
    
    global WAIT_DURATION
    global SLEEP_DURATION
    
    # Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
    driver = gUtil.initWebDriver ()
    driver.get('about:blank')
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
    
    return driver


def login (driver) : 
    
    
    driver.implicitly_wait(WAIT_DURATION)
    # url에 접근한다.
    driver.get(LOGIN_PAGE)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
    
    
    # 아이디/비밀번호를 입력해준다.
    driver.find_element_by_name(ID_FIELD_NAME).send_keys(ID)
    driver.find_element_by_name(PWD_FIELD_NAME).send_keys(PWD)
    
    
    # 로그인 후 작업하자.
    driver.find_element_by_id('btn_login').click()
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "login complete. <br>")
    
    
def sendProductInfo (
        driver, 
        product_images, 
        product_name, 
        is_oversea, 
        local_price, 
        oversea_price, 
        category_code, 
        color, 
        size,
        texture_mixed,
        thickness,
        transparency,
        elasticity,
        lining,
        laundry_inco,
        description,
        publishing_type,
        publishing_delay,
        made_in,
        style) :
    
    global ALERT_TEXT
    
    ALERT_TEXT = ""
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "sendProductInfo ====================================================<br>")
    driver.get (PRODUCT_FORM_PAGE)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
    
   
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "sendProductInfo 222 ====================================================<br>")
    
    #럽로드할 이미지 셋팅
    p_images = product_images.split (",")
    element = driver.find_element_by_name ("uploaded")
    
    for i in range (len (p_images)) :
        
        #aws s3에서 이미지 다운로드....
        dirname = "product_images"
        if not os.path.exists(base_file_url + dirname) : os.makedirs(base_file_url + dirname)
        s3.download_file(bucketName, p_images[i], base_file_url + dirname + "/" + p_images[i][p_images[i].rfind("/") + 1:])
        element.send_keys(base_file_url + dirname + "/" + p_images[i][p_images[i].rfind("/") + 1:])
   
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "image handling complete -------><br>")
    
    #이미지 순서 고고 
    for i in range (len (p_images)) :
        driver.execute_script("orderSelect(" + str(i) + ")")
        
    
    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "image arrange complte -------><br>")
    
    
    #상품명
    p_name = str (product_name)
    if (IS_SERVER != True) : p_name = unicode(p_name.decode("utf-8"))
    driver.find_element_by_class_name("goodsName").send_keys (p_name)
    
    #해외검색 노출 체크박스
    if (int (is_oversea) == 0) :  
        driver.execute_script("arguments[0].click();", driver.find_element_by_id("chinaPrice"))
    
    #가격
    driver.find_element_by_class_name ("goodsPrice").send_keys (str (local_price))
    if (int (is_oversea) == 1) : driver.find_element_by_class_name ("foreignPrice").send_keys (str (oversea_price))
    
    #카테고리 -- 
    driver.execute_script("categoryChoice(" + str(category_code) + ")")
    
    
    #색상
    try :
        p_color = str (color) + " "
        if (IS_SERVER != True) : p_color = unicode(p_color.decode("utf-8"))
        driver.find_element_by_name ("input").send_keys (p_color)
    except Exception as ex :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "새상 지정 error occured ---> " + str (ex))
    
    #사이즈
    try :
        p_size = str (size) + " "
        if (IS_SERVER != True) : p_size = unicode(p_size.decode("utf-8"))
        driver.find_element_by_name ("inputS").send_keys (p_size)
    except Exception as ex :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "사이즈 지정 error occured ---> " + str (ex))
    
    
    try :
        #혼용율
        p_mixed = str (texture_mixed) + " "
        if (IS_SERVER != True) : p_mixed = unicode(p_mixed.decode("utf-8"))
        driver.find_element_by_name ("inputM").send_keys (p_mixed)
        
        #옷감정보 - 두께감
        p_thick = int (thickness)
        if (p_thick == 1) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("thickness1"))
        elif (p_thick == 2) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("thickness2"))
        elif (p_thick == 3) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("thickness3"))
        
        #옷감정보 - 비침
        p_transparency = int (transparency)
        if (p_transparency == 1) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("shine1"))
        elif (p_transparency == 2) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("shine2"))
        elif (p_transparency == 3) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("shine3"))
        
        #옷감정보 - 신축성
        p_elasticity = int (elasticity)
        if (p_elasticity == 1) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("flexibility1"))
        elif (p_elasticity == 2) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("flexibility2"))
        elif (p_elasticity == 3) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("flexibility3"))
        elif (p_elasticity == 4) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("flexibility4"))
        
        #옷감정보 - 안감
        p_lining = int (lining)
        if (p_lining == 1) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("lining1"))
        elif (p_lining == 2) :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id("lining2"))
        
        #옷감정보 - 세탁방법
        p_laundry_info = str (laundry_inco).split (",")
        if 1 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod1")) # --> 손세탁
        if 2 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod2")) # --> 드라이(클리닝)
        if 3 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod3")) # --> 물세탁
        if 4 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod4")) # --> 단독세탁
        if 5 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod5")) # --> 울세탁
        if 6 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod6")) # --> 표백제 사용금지
        if 7 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod7")) # --> 다림질 금지
        if 8 in p_laundry_info : driver.execute_script("arguments[0].click();", driver.find_element_by_id("washingMethod8")) # --> 세탁기 금지
    except Exception as ex :
        #SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "error occured ---> " + str (ex))
        pass
    

    #상세설명
    p_description = str (description)
    if (IS_SERVER != True) : p_description = unicode(p_description.decode("utf-8"))
    driver.find_element_by_id ("myTextarea").send_keys (p_description)
    
    #공개여부 1~3
    pub_option = int (publishing_type)
    pub_delay = str (publishing_delay)
    
    if (pub_option == 1) :
        driver.execute_script("arguments[0].click();", driver.find_element_by_id("allOpen"))
    elif (pub_option == 2) :
        driver.execute_script("arguments[0].click();", driver.find_element_by_id("tradeOpen"))
    elif (pub_option == 3) :
        driver.execute_script("arguments[0].click();", driver.find_element_by_id("delayOpen"))
        driver.find_element_by_xpath ("/html/body/div[1]/div[12]/label[3]/input").send_keys (pub_delay)
    
    #제조국
    driver.find_element_by_xpath ("/html/body/div[1]/div[13]/label[" + str (made_in) + "]").click ()

    #낱장 주문 가능 여부 -- 일단 디폴트
    driver.find_element_by_xpath ("/html/body/div[1]/div[15]/div[2]/label[2]").click ()

    #스타일 지정 (필요시)
    try :
        p_style = str (style)
        if (p_style != "") :
            driver.execute_script("arguments[0].click();", driver.find_element_by_id (p_style))
    except Exception as ex :
        #SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "error occured ---> " + str (ex))
        pass
    
    driver.find_element_by_id ("regist").click ()
    
    try :
        alert = driver.switch_to_alert()
        ALERT_TEXT = alert.text
    except : 
        pass
    
    tm.sleep (SLEEP_DURATION) # ---> 인간적으로 몇 초만 기다리자. 파일이 올라가는데...
    #----> 1일 업로드 제한 걸림. 명일(수요일) 테스트 해 볼것. 실패시 다음날 (0시 지나자마자)자동으로 올라가는 방식도 고려해 볼것.
   


def sendProduct () :
    
    global VENDOR_CODE
    global ID
    global PWD
    
    driver = initWebDriver ()

    try :
        
        if (IS_SERVER) :
            
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM tbl_vendor_product WHERE vendor_idx='" + str (VENDOR_CODE) + "' AND sm_published=0 ORDER BY reg_date ASC LIMIT 0,10;")
            products = cursor.fetchall()
            
            if (len(products) > 0) : 
            
            
                login (driver)
                tm.sleep (3)
            
                for product in products :
                    
                    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (product[0]) + "번 상품 신상마켓 전달 시작 -------------------------------------------------------- ")
                    
                    try :
                        sendProductInfo(
                            driver, 
                            product[2],
                            product[3],
                            product[4],
                            product[5],
                            product[6], 
                            product[7], 
                            product[8], 
                            product[9],
                            product[10],
                            product[11],
                            product[12],
                            product[13],
                            product[14],
                            product[15],
                            product[16],
                            product[17],
                            product[18],
                            product[19],
                            product[20]
                        )
                        
                        if (ALERT_TEXT == None or str (ALERT_TEXT) == "") :
                            qry = "UPDATE tbl_vendor_product SET sm_published=1 WHERE idx=" + str(product[0]) + ";"
                            SmLogger.info (SmLogger, os.path.basename(__file__) + " " + qry)
                            cursor.execute(qry)
                            mydb.commit ()
                        else :
                            SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "alert --> " + str (ALERT_TEXT))
                            
                    except Exception as ex :
                        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (ex))
                        pass
                    
                    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (product[0]) + "번 상품 신상마켓 전달 끝 -------------------------------------------------------- ")
                    tm.sleep(10)
                else :
                    SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "신상마켓 전달 내용 없음")
                
            #mydb.close () --> filnay 에서 닫을거임
            #driver.save_screenshot("damn.png")
            
        else :
            
            VENDOR_CODE = '33'
            ID = "mrcurt716"
            PWD = "123456"
            
            login (driver)
            tm.sleep (3)
            
            pp_images = "/Users/kevinhan/Documents/01.WORKS/www.kevin75.com/P3D/IMG_7278.jpg,/Users/kevinhan/Documents/01.WORKS/www.kevin75.com/P3D/IMG_7260.jpg,/Users/kevinhan/Documents/01.WORKS/www.kevin75.com/P3D/34450022814_5828032bd3_o.jpg"
            sendProductInfo(
                driver, 
                pp_images,
                "테스트 제품입니다요",
                0, 
                35000, 
                0, 
                14, 
                "레드 옐로우 핑크 베이지", 
                "S M L XL",
                "",
                1,
                2,
                1,
                1,
                "1,3,7",
                "몰라 알수가 없어~",
                3,
                15,
                1,
                "Dandy"
            )
            
            
        
    except Exception as ex : 
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (ex))
    finally:
        
        if (IS_SERVER) : mydb.close ()
        driver.quit()




