#-*- coding: utf-8 -*-
'''
Created on 2019. 3. 7.

@author: kevinhan
'''

from common.utils import SmLogger

class Vendor :

    def __init__ (self) :
        SmLogger.info (SmLogger, "init --> " + str(self))