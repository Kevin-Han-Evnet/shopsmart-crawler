#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''

import shutil
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
import logging
from common.config import ShopsmartDB as SDB
from common.config import s3
from common.config import bucketName
from common.config import base_file_url
from common.config import GeneralUtil
from common.config import Tables
from common.utils import SmLogger

from urllib.parse import urlparse
import uuid
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from PIL import Image

#implicitly_wait -- second
WAIT_DURATION = 3

#system sleep duration -- second
SLEEP_DURATION = 3

#page load time out
PAGE_LOAD_TIMEOUT = 30



#고고고
gUtil = GeneralUtil ("", PAGE_LOAD_TIMEOUT, WAIT_DURATION, 0, 0, 0)


target_name = ''
NP_URL = ''
tag_selector = ''
sub_tag_selector = ''
img_tag_selector = ''
research_idx = -1
not_nessesary_strings = ''
np_code_name = ''

save_success_count = 0;
save_failed_count = 0;
crawling_engine = 'URLLIB'


mydb = SDB.getDB()



def getPureInfo (org_text) :
    
    global not_nessesary_strings
    
    result = str (org_text)
    not_nessesary_string_list = str (not_nessesary_strings).strip ().split(",")
    if (len (not_nessesary_string_list) > 0) :
        for t in not_nessesary_string_list :
            result = result.replace(t, "")

    return result


def parseItems (current_url, item) :


    global save_success_count;
    global save_failed_count;

    dt = datetime.datetime.now()
    cursor = mydb.cursor()

    link_url = ''

    if (item.select('a') != None and len(item.select('a')) > 0) :
        link_url = item.select('a')[0].get('href')
    else :
        link_url = item.get('onclick')[item.get('onclick').find('/'): item.get('onclick').rfind('\'')]

    np_url = ""

    if (link_url.startswith('http')) :
        np_url = link_url
    elif (link_url[0]  == "/") :
        np_url = "http://" + urlparse(str(current_url)).hostname + link_url
    else :
        np_url = str(current_url)[0:str(current_url).rfind ("/")] + "/" + link_url

    params = dict(parse.parse_qsl(parse.urlsplit(np_url).query))


    np_code = None

    if (np_code_name.startswith ('/') == True) :
        np_code = link_url.split ('/')[int(np_code_name[1])]
    elif (np_code_name.startswith ('none')) :
        np_code = str(uuid.uuid4())
    else :
        np_code = params[str (np_code_name)]

    np_description = item.text.strip().replace('\n\n\n\n', '<br>').replace('\n\n\n', '<br>').replace ('\n\n', '<br>').replace ('\n\n', '<br>').replace ('\'', '').replace ('\"', '')
    if (len(str(not_nessesary_strings).strip()) > 0) : np_description = getPureInfo(np_description)


    #걸러내자...
    if (np_description.find ('var prdNo') > 0) :
        np_description = np_description[0 : np_description.find('var prdNo')]
    elif (np_description.find ('if(getProductCode') >= 0) :
        np_description = np_description[np_description.find('}<br><br><br>')+13::]


    if (img_tag_selector != None and img_tag_selector != '') :
        imgs = item.select(img_tag_selector)
        if (str(imgs[0]).find('ec-data-src') >= 0) :
            np_image_url = str(imgs[0].get("ec-data-src"))
        else :
            np_image_url = str (imgs[0].get('src'))

        # 이미지 패쓰및 s3 아이디 따기 ------------------------------------------------------------------------------------------------------------
        t = np_image_url.split('/')
        if (np_image_url.startswith('//')) :
            np_image_url = 'http:' + np_image_url

        if (np_image_url.startswith ('http://') == False and np_image_url.startswith('https://') == False):
            np_image_url = "http://" + urlparse(str(current_url)).hostname + '/' + np_image_url;

        uniqueId = str (uuid.uuid4())
        dirname = "np_crawling/" + str (research_idx) + "/" + str (dt.year) + '/' + str (dt.month) + '/' + str (dt.day)
        filename = dirname  + '/' + uniqueId + "." + t[len(t) - 1].split ('?')[0].split(".")[1]
        cv_filename = dirname + '/' + uniqueId + ".png"

        final_filename = filename
        if (filename.lower().find('.webp') > 0) : final_filename = cv_filename
        # 이미지 패쓰및 s3 아이디 따기 ------------------------------------------------------------------------------------------------------------
    else :
        filename = None


    sql = "INSERT INTO " + Tables.TBL_NP_CRAWLING_RESULT + " (crawling_info_idx, target_name, np_url, np_code, np_image_url, np_description) VALUES (%d, '%s', '%s', '%s', '%s', '%s')" % (
        int (research_idx),
        str (target_name),
        np_url,
        np_code,
        final_filename,
        np_description
    )


    try :


        cursor.execute(sql)
        save_success_count += 1


        if (img_tag_selector is not None and img_tag_selector is not '') :
            #이미지 받아서 s3로 넘기고 삭제하기 ------------------------------------------------------------------------------------------------------------
            if not os.path.exists(base_file_url + dirname) : os.makedirs(base_file_url + dirname)

            if (np_image_url.startswith('//')) :
                np_image_url = 'http:' + np_image_url

            if (np_image_url.startswith ('http://') == False and np_image_url.startswith('https://') == False):
                np_image_url = "http://" + urlparse(str(current_url)).hostname + '/' + np_image_url;



            SmLogger.info (SmLogger, "이미지 주소는요 --> " + np_image_url)
            SmLogger.info (SmLogger, "임시 저장 주소는요? --> " + base_file_url + final_filename)
            SmLogger.info (SmLogger, "s3 저장 주소는요? --> " + bucketName + "/" + final_filename)
            SmLogger.info (SmLogger, "--------------------------------------------------------------------------------------------------------------")

            request.urlretrieve (np_image_url, base_file_url + filename)                                              #--> 이미지 다운로드

            if (final_filename.find('.png') > 0) :
                im = Image.open(base_file_url + filename)
                im.save(base_file_url + final_filename, 'png')

            s3.upload_file (base_file_url + final_filename, bucketName, final_filename, {'ACL':'public-read'})                    #--> s3 업로드
            #이미지 받아서 s3로 넘기고 삭제하기 ------------------------------------------------------------------------------------------------------------

    except Exception as ex :
        save_failed_count += 1
        SmLogger.info (SmLogger, "중복데이타 --> " + str (ex))
        pass

    return save_failed_count

    
def getItems (pNum):
    
    
    global WAIT_DURATION
    global SLEEP_DURATION
    global sub_tag_selector

    global save_success_count;
    global save_failed_count;

    
    
    save_success_count = 0;
    save_failed_count = 0;
    items = []
    current_url = ""
    
    try :
    

        if ('%s' in NP_URL):
            current_url = NP_URL % str(pNum)

        else :
            current_url = NP_URL


        soup = None
        items = []


        if (str (crawling_engine) == 'URLLIB') :
            #urllib 방식 ----------------------------------------------------------------------------------------------------------------------------------------
            objRequest = request.Request(
                current_url,
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                    'window-size' : '1920x1080'
                }
            )

            success = 1
            page_source = ""
            try :
                page_source = request.urlopen(objRequest).read().decode ("utf-8")
            except :
                success = 0

            if (success == 0) :
                try :
                    page_source = request.urlopen(objRequest).read().decode ("utf-16")
                except :
                    success = 0

            if (success == 0) :
                try :
                    page_source = request.urlopen(objRequest).read().decode ("utf-16-le")
                except :
                    success = 0
            #urllib 방식 ----------------------------------------------------------------------------------------------------------------------------------------


            soup = bs(page_source, 'html.parser')
            items = soup.select(tag_selector)

        elif (str (crawling_engine) == 'WEBDRIVER'):
            #웹드라이버 방식 ----------------------------------------------------------------------------------------------------------------------------------------
            driver = gUtil.initWebDriver ()
            driver.get (current_url)
            driver.implicitly_wait (WAIT_DURATION)
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
            driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
            page_source = driver.page_source.strip()

            soup = bs(page_source, 'html.parser')
            items = soup.select(tag_selector)
            #웹드라이버 방식 ----------------------------------------------------------------------------------------------------------------------------------------

        imgs = []
        links = []

        dirname = ""
        filename = ""


        if (len(items) > 0) :

            SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str(pNum) + " 페이지 아이템 " + str (len(items)) + "개 저장 시도")


            for item in items :

                if (sub_tag_selector is not None and sub_tag_selector is not '') : #2단 루핑 구조 일때

                    sub_items = item.select(sub_tag_selector)
                    for sub_item in sub_items :
                        parseItems (current_url, sub_item)

                else :                                                             #1단 루핑 구조 일때
                    parseItems (current_url, item)



        else :
            SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str(pNum) + " 페이지 아이템 없음.")
        
    except Exception as ex :
        
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + "에러 발생 --> " + str (ex))
        #saveErrorLog (result, target, category, message)
            
        
    finally :
        try :
            shutil.rmtree (base_file_url + "np_crawling")         
        except :
            pass
        #driver.quit ()
        mydb.commit ()
        #mydb.close () --> 위에서 한꺼번에 할거야...
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str(pNum) + " 페이지 아이템 " + str (save_success_count) + "개 저장 성공, " + str (save_failed_count) + "개 중복 수집으로 인한 실패처리.")
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str(pNum) + " 페이지 아이템 " + str (len(items)) + "개 처리 완료")
        if (int (save_failed_count) > 0) : return 0
        else : return len(items)
        
        
        
        
        
        
        
        