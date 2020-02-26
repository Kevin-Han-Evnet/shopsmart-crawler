#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''


import mysql.connector as pymysql
import boto3
from common.utils import SmLogger



class ShopsmartDB :
    def getDB ():
        mydb = pymysql.connect(
            host="shopsmart.cluster-cveskpxitnmv.ap-northeast-2.rds.amazonaws.com",
            user="shopsmart_dbu",
            passwd="tiqtmakxm0328",
            database="shopsmart-new"
        )

        return mydb


class Tables :
    TBL_NP_CRAWLING_RESULT = "tb_crl_np_result"
    TBL_EVENT_CRAWLING_RESULT = "tb_crl_event_result"
    TBL_ORDER_CRAWLING_INFO = "tb_crl_order_info"
    TBL_ORDER_CRAWLING_RESULT = "tb_crl_order_result"
    TBL_KEYWORD_TREND_CRAWLING_INFO = "tb_crl_keyword_info"
    TBL_KEYWORD_TREND_CRAWLING_RESULT = "tb_crl_keyword_result"
    TBL_RESEARCH_INFO = "tb_crl_research_info"
    TBL_RESEARCH_TARGET = "tb_crl_resultch_target"
    TBL_WS_ORDER = "tb_ws"
    TBL_MEMBERSHIP = "tb_membership"



base_file_url = '/tmp/'

# aws s3 bucket setting ---------------
bucketName = "shopsmart-s3"
s3 = boto3.client('s3', aws_access_key_id='AKIA2QJBVCLU6LR4QWYV', aws_secret_access_key='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')
# aws s3 bucket setting ---------------


from selenium import webdriver
from selenium.common.exceptions import TimeoutException
class GeneralUtil :

    PAGE_LOAD_TIMEOUT = 0
    WAIT_DURATION = 0
    MAX_CHECKED_TOBE = 0
    CRAWLING_INFO_IDX = 0
    PLATFORM_TYPE = 0
    SHOP_ID = ""

    updateInfoList = []
    insertQRY = ""
    updateQRY = ""

    """ 디버깅을 위한 모니터링 값  """
    t_total_order_count = 0
    t_new_order_count = 0
    t_update_order_count = 0
    t_canceled_order_count = 0
    t_insert_items = []
    t_update_order_idxs = []
    t_dup_update_order_idxs = []
    is_complete = False

    def __init__(self, SHOP_ID, PAGE_LOAD_TIMEOUT, WAIT_DURATION, MAX_CHECKED_TOBE, CRAWLING_INFO_IDX, PLATFORM_TYPE) :

        self.SHOP_ID = SHOP_ID
        self.PAGE_LOAD_TIMEOUT = PAGE_LOAD_TIMEOUT
        self.WAIT_DURATION = WAIT_DURATION
        self.MAX_CHECKED_TOBE = MAX_CHECKED_TOBE
        self.CRAWLING_INFO_IDX = CRAWLING_INFO_IDX
        self.PLATFORM_TYPE = PLATFORM_TYPE
        self.is_complete = False


    def initWebDriver (self):

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        # 혹은 options.add_argument("--disable-gpu")
        options.add_argument("lang=ko_KR") # 한국어!


        #이미지 로드 금지 시켜 보자...
        chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

        # Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
        driver = webdriver.Chrome('/Users/kevinhan/c_browser/chromedriver', options=options)
        driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(self.WAIT_DURATION)
        driver.get('about:blank')
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")

        return driver


    #내용가공
    def getHtmlText (self, org_str) :
        return org_str.replace ('\n\n\n', '<br>').replace ('\n\n', '<br>').replace ('\n', '<br>')

    #제품명 반환bin
    def getProductName (self, product_name) :
        if (product_name.find ("[공급사상품명]") >= 0) :
            return str (product_name.split ("[공급사상품명]")[1]).strip ()
        else :
            return product_name.strip ()


    #옵션명 반환
    def getProductOption (self, options) :
        result = ""

        if (self.PLATFORM_TYPE == 1) : #카페24 -- 기장 / 색상 / 사이즈 순서 (개별 옵션 없을수 있음

            pos_1 = options.find ("기장")
            pos_2 = options.find ("색상")
            pos_3 = options.find ("사이즈")

            #기장 옵션
            if (pos_1 >= 0) :
                if (pos_2 > 0) : result += (options[pos_1 : pos_2]) + ","
                elif (pos_3 > 0) : result += (options[pos_1 : pos_3]) + ","
                else : result += (options) + ","

            #색상 옵션
            if (pos_2 >= 0) :
                if (pos_3 > 0) : result += (options[pos_2 : pos_3]) + ","
                else : result += (options[pos_2:]) + ","

            #사이즈
            if (pos_3 > 0) : result += (options[pos_3:]) + ","

            result = result [0:-1]

        elif (self.PLATFORM_TYPE == 2) :

            if (options.find ("[수정]") > 0) :
                result += options.split ("[수정]")[0]
            else :
                result += options

        elif (self.PLATFORM_TYPE == 4) :

            if (options.find ("/") > 0) :
                tmp = options.split ("/")
                for t in tmp :
                    result += t.strip () + ","

                result = result [0:-1]

        else :
            result = options

        return result




    #내용가공
    def getPureText (self, org_str) :
        return org_str.replace ("   ", "").replace ('\n\n\n', '').replace ('\n\n', '').replace ('\n', '').strip ()

    def getNumeric (self, org_str) :
        return int (org_str.replace (',', '').replace ('개', '').replace ('원', ''))


    #체크하여 주문서 닫기
    def checkAndCloseOrder (self) :

        if (self.is_complete == True) : return

        self.t_total_order_count = self.t_new_order_count + self.t_update_order_count

        SmLogger.info (SmLogger, "REPORT --------------------------------------------------------------------------------------------")
        SmLogger.info (SmLogger, "전체 주문 건수 --> " + str (self.t_total_order_count))
        SmLogger.info (SmLogger, "신규 주문건수 --> " + str (self.t_new_order_count))
        SmLogger.info (SmLogger, "기존 주문건수 --> " + str (self.t_update_order_count))
        SmLogger.info (SmLogger, "실제 업데이트 쿼리 작성 수 --> " + str (len (self.t_update_order_idxs)))
        SmLogger.info (SmLogger, "중복 업데이트 시도 건수 --> " + str (len (self.t_dup_update_order_idxs)))
        SmLogger.info (SmLogger, "중복 업데이트 시도 대상 --> " + str (self.t_dup_update_order_idxs))
        SmLogger.info (SmLogger, "REPORT --------------------------------------------------------------------------------------------")

        qry = "UPDATE " + Tables.TBL_ORDER_CRAWLING_RESULT + " SET closed=1, reg_date=now() WHERE  crawling_info_idx=" + str (self.CRAWLING_INFO_IDX) + " AND checked < " + str (self.MAX_CHECKED_TOBE) + " AND closed=0;"
        mydb.cursor().execute (qry)
        mydb.commit()

        self.is_complete = True

    #인서트 쿼리
    def addInsertItem (self,
                       check_dup_code,
                       product_name,
                       product_option,
                       order_count,
                       stock_count,
                       ws_order_count,
                       coast,
                       price,
                       vendor_info,
                       vendor_contact) :


        if (self.insertQRY == "") :
            sql = "INSERT INTO " + Tables.TBL_ORDER_CRAWLING_RESULT + " ("
            sql += "crawling_info_idx, "
            sql += "membership_seq, "
            sql += "check_dup_code, "
            sql += "product_name, "
            sql += "product_option, "
            sql += "order_count, "
            sql += "stock_count, "
            sql += "ws_order_count, "
            sql += "coast, "
            sql += "price, "
            sql += "vendor_info, "
            sql += "vendor_contact, "
            sql += "checked, "
            sql += "platform_type) VALUES ({}, {}, '{}', '{}', '{}', {}, {}, {}, {}, {}, '{}', '{}', {}, {})"
            self.insertQRY = sql.format (
                int (self.CRAWLING_INFO_IDX),
                self.SHOP_ID,
                str (check_dup_code),
                product_name,
                product_option,
                order_count,
                stock_count,
                ws_order_count,
                coast,
                price,
                vendor_info,
                vendor_contact,
                self.MAX_CHECKED_TOBE,
                self.PLATFORM_TYPE
            )
        else :
            option_sql = ", ({}, {}, '{}', '{}', '{}', {}, {}, {}, {}, {}, '{}', '{}', {}, {})"
            self.insertQRY += option_sql.format (
                int (self.CRAWLING_INFO_IDX),
                self.SHOP_ID,
                check_dup_code,
                product_name,
                product_option,
                order_count,
                stock_count,
                ws_order_count,
                coast,
                price,
                vendor_info,
                vendor_contact,
                self.MAX_CHECKED_TOBE,
                self.PLATFORM_TYPE
            )

        self.t_new_order_count += 1
        self.t_insert_items.append(check_dup_code)



    #업데이트 쿼리 작성
    def addUpdateItem (self,
                       idx,
                       order_count,
                       stock_count,
                       ws_order_count) :


        self.updateInfoList.append(dict (idx=idx, order_count=order_count, stock_count=stock_count, ws_order_count=ws_order_count))
        self.t_update_order_idxs.append (idx)
        self.t_update_order_count += 1


    def getUpdateQRY (self) :


        if (len (self.updateInfoList) == 0) :
            return ""
        else :

            tIdxs = []
            result = "UPDATE " + Tables.TBL_ORDER_CRAWLING_RESULT + " SET "

            result_order_count = "order_count=(CASE"
            result_stock_count = ", stock_count=(CASE"
            result_ws_order_count = ", ws_order_count=(CASE"

            for i in range (0, len (self.updateInfoList)) :
                result_order_count += " WHEN idx=" + str (self.updateInfoList[i]["idx"]) + " THEN " + str (self.updateInfoList[i]["order_count"])
                result_stock_count += " WHEN idx=" + str (self.updateInfoList[i]["idx"]) + " THEN " + str (self.updateInfoList[i]["stock_count"])
                result_ws_order_count += " WHEN idx=" + str (self.updateInfoList[i]["idx"]) + " THEN " + str (self.updateInfoList[i]["ws_order_count"])
                tIdxs.append(self.updateInfoList[i]["idx"])

            result_order_count += " END)"
            result_stock_count += " END)"
            result_ws_order_count += " END)"

            result += result_order_count + result_stock_count + result_ws_order_count + ", checked=" + str (self.MAX_CHECKED_TOBE) + " WHERE idx in (" + str(tIdxs)[1:-1] + ");"

            tIdxs.clear()

            return result

class WholsaleOrderUtil :

    insertQRY = ""

    def __init__(self):
        self.insertQRY = ""

    #인서트 쿼리
    def addInsertItem (self,
                       shop_id,
                       vendor_contact,
                       product_name,
                       option_1,
                       option_2,
                       option_3,
                       coast,
                       order_count) :


        if (self.insertQRY == "") :
            sql = "INSERT INTO " + Tables.TBL_WS_ORDER + " ("
            sql += "membership_seq, "
            sql += "vendor_contact, "
            sql += "product_name, "
            sql += "option_1, "
            sql += "option_2, "
            sql += "option_3, "
            sql += "coast, "
            sql += "order_count) VALUES ({}, '{}', '{}', '{}', '{}', '{}', {}, {})"
            self.insertQRY = sql.format (
                shop_id,
                str (vendor_contact),
                str (product_name),
                str (option_1),
                str (option_2),
                str (option_3),
                int (coast),
                int (order_count)
            )
        else :
            option_sql = ", ({}, '{}', '{}', '{}', '{}', '{}', {}, {})"
            self.insertQRY += option_sql.format (
                shop_id,
                str (vendor_contact),
                str (product_name),
                str (option_1),
                str (option_2),
                str (option_3),
                int (coast),
                int (order_count)
            )