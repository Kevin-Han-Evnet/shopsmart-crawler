#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 22.

@author: kevinhan
'''


import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

from common.config import mydb

import time as tm
import random

from common.utils import SmLogger


SmLogger.info (SmLogger, os.path.basename(__file__) + " \n\n\n")
SmLogger.info (SmLogger, os.path.basename(__file__) + " ====================================================================================")
SmLogger.info (SmLogger, os.path.basename(__file__) + " \n\n\n")


cursor = mydb.cursor()

img_list = [
    "vendor_product/test_images/156210914371070800_1935332633.jpg",
    "vendor_product/test_images/156271601481471600_1574994230.jpg",
    "vendor_product/test_images/156279939897703700_257972112.jpg",
    "vendor_product/test_images/156279989233017100_167449965.jpg",
    "vendor_product/test_images/156280051831418700_178874149.jpg",
    "vendor_product/test_images/u_15602087668038800_984378587.jpg"
]


cursor.execute("SELECT * FROM tbl_mt_product_category;")
categories = cursor.fetchall()



colors = [
    "더블카라반팔 블라우스",
    "꼬임 블라우스",
    "노방리본 블라우스",
    "진주배색반팔 블라우스",
    "폴마프릴 블라우스 입니다요",
    "이게 도대체 뭥미??? 왜 안됨???"
]

cloth_sizes_male = "90 95 100 105 110 Free"
cloth_sizes_female = "55 66 77 88 99 Free Bigsize"
cloth_size_kid = "12M 24M 36M S M L"

shoes_size_adult = "230 235 240 245 250 255 260 265 270 275 280"
shoes_size_kid = "160 170 180 190 200 210 220 230"
accessory_size = "프리사이즈"

textures = [
    "면 폴리에스테르",
    ""
]

style_tags = [
    "20대초반,러블리",
    "30대후반,미시스타일",
    "20대후반,캠퍼스룩",
    "10대,러블리",
    "에슬레저"
]


def saveFakeProduct (pNum, vendor) :
    
    """
    
    $wpdb->show_errors();
    $fuck = $wpdb->insert(
            VENDOR_PRODUCT,
            array(
                'vendor_idx' => $vendor_idx,
                'product_images' => implode (",", $uploaded_files),
                'product_name' => $product_name,
                'is_oversea' => $is_oversea,
                'local_price' => $local_price,
                'oversea_price' => $oversea_price,
                'category_code' => $category_code,
                'color' => $color,
                'size' => $size,
                'texture_mix' => $texture_mix,
                'thickness' => $thickness,
                'transparency' => $transparency,
                'elasticity' => $elasticity,
                'lining' => $lining,
                'laundry_info' => implode (",", $laundry_info),
                'description' => $description,
                'publishing_type' => $publishing_type,
                'publishing_delay' => ($publishing_type == 3) ? $publishing_delay : 0,
                'made_in' => $made_in,
                'sample_type' => $sample_type,
                'style' => $style,
                'style_tag' => ???
            )
        );
    
    """
    idx = random.randrange (0, len(img_list))
    is_oversea = int (random.randrange (0, 2))
    local_price = int (random.randrange (1, 30) * 1000)
    oversea_price = 0
    if (is_oversea > 0) :
        oversea_price = int (random.randrange (1, 30) * 1000)
        
    
    category_info = categories[random.randrange (0, len(categories))]
    color = colors[random.randrange (0, len(colors))]
    
    size = ""
    if (int (category_info[3]) == 1) :
        size = cloth_sizes_female
    elif (category_info[3] == 2) :
        size = shoes_size_adult
    elif (category_info[3] == 3) :
        size = ""
    elif (category_info[3] == 4) :
        size = accessory_size
    elif (category_info[3] == 5) :
        size = cloth_sizes_male
    elif (category_info[3] == 6) :
        size = shoes_size_adult
    elif (category_info[3] == 7) :
        size = ""
    elif (category_info[3] == 8) :
        size = accessory_size
    elif (category_info[3] == 9) :
        size = cloth_size_kid
    elif (category_info[3] == 10) :
        size = shoes_size_kid
        
        
    style_tag = style_tags[random.randrange (0, len(style_tags))]
    
    
    sql = "INSERT INTO tbl_vendor_product ("
    sql += "vendor_idx, "
    sql += "product_images, "
    sql += "product_name, "
    sql += "is_oversea, "
    sql += "local_price, "
    sql += "oversea_price, "
    sql += "category_code, "
    sql += "color, "
    sql += "size, "
    sql += "texture_mix, "
    sql += "description, "
    sql += "publishing_type, "
    sql += "publishing_delay, "
    sql += "made_in, "
    sql += "sample_type, "
    sql += "style_tag"
    sql += ") VALUES ({}, \"{}\", \"{}\", {}, {}, {}, {}, \"{}\", \"{}\", \"{}\", \"{}\", {}, {}, {}, {}, \"{}\");".format (
                int (vendor[0]),
                str (img_list[idx]),
                str (vendor[1]) + " 샘플 제품 " + str(pNum),
                is_oversea,
                local_price,
                oversea_price,
                int (category_info[0]),
                color,
                size,
                str (textures[random.randrange (0, len(textures))]),
                "설명이야 뻖하죠. 설명 설명 " + str (vendor[1]) + " 샘플 제품 " + str(pNum),
                3,
                30,
                int (random.randrange (1, 4)),
                int (random.randrange (1, 6)),
                style_tag
            )
        
    cursor.execute(sql)



cursor.execute("SELECT * FROM tbl_vendor WHERE sm_sync=0;")
vendors = cursor.fetchall()

if (len (vendors) > 0) :
    for vendor in vendors :
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (vendor[0]) + " : " + str(vendor[1]) + " -->  요놈 함 넣어보자 -------------------------------------------------------- ")
        
        for i in range (300) :
            saveFakeProduct (i, vendor)
        
        SmLogger.info (SmLogger, os.path.basename(__file__) + " " + str (vendor[0]) + " : " + str(vendor[1]) + " -->  요놈 함 넣었다 -------------------------------------------------------- ")
            
    
    tm.sleep(2)
    
mydb.commit()
mydb.close()