# -*- coding: utf-8 -*-


import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QMetaObject, QRect, QSize)
from PySide2.QtWidgets import *

from common.utils import SmLogger


from standalone.keyword_trend import KeywordTrend as KT
from standalone.product_event import ProductAndEvent as PE



#키워드 트렌드 리서치 쓰레드
class ThreadClassForKT (QtCore.QThread):

    someting = QtCore.Signal(object)

    def __init__(self, parent = None):
        super(ThreadClassForKT,self).__init__(parent)

    def run(self):
        KT.myThread = self
        KT.doIt(KT)

    def updateMSG (self, msg):
        try:
            self.someting.emit(msg)
        except Exception as e:
            print("__init__:")
            print(e)



#신상품 / 이벤트 리서치 쓰레드
class ThreadClassForPE (QtCore.QThread):
    def __init__(self, parent = None):
        super(ThreadClassForPE,self).__init__(parent)
    def run(self):
        PE.doIt(PE)



class Ui_MainWindow(object):

    textBrowser = None
    ktThread = None
    peTrhead = None

    def __init__ (self, parent = None) :
        self.ktThread = ThreadClassForKT()
        self.ktThread.someting.connect(self.updateMSG)
        SmLogger.uiTarget = self.ktThread

        self.peThread = ThreadClassForPE()


    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"샵스마트 리서치")
        MainWindow.setEnabled(True)
        MainWindow.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(800, 600))
        MainWindow.setMaximumSize(QSize(800, 600))
        self.centralwidget = QWidget(MainWindow)

        self.centralwidget.setObjectName(u"centralwidget")




        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.document().setMaximumBlockCount(3000)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(10, 50, 780, 450))




        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 20, 181, 31))

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(195, 512, 200, 50))
        self.pushButton.clicked.connect (self.doKTResearch)

        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(395, 512, 200, 50))
        self.pushButton_2.clicked.connect (self.doPEResearch)


        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi



    #ui update
    def updateMSG (self, message):
        self.textBrowser.append (message)
        self.textBrowser.hide ()
        self.textBrowser.show ()
        self.textBrowser.moveCursor(QtGui.QTextCursor.End)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:18pt; font-weight:600; font-style:italic; color:#408002;\">Shopsmart research crawler</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\ud0a4\uc6cc\ub4dc \ud2b8\ub80c\ub4dc \ub9ac\uc11c\uce58 \uc2e4\ud589", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\uc2e0\uc0c1 / \uc774\ubca4\ud2b8 \ub9ac\uc11c\uce58 \uc2e4\ud589", None))
    # retranslateUi

    def doKTResearch (self):
        self.ktThread.start()

    def doPEResearch (self):
        self.peThread.start()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())