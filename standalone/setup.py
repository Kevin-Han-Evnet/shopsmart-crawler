# -*- coding: utf-8 -*-
from setuptools import setup


# name, description, version등의 정보는 일반적인 setup.py와 같습니다.
setup(name="ss-research",
      description="리서치 크롤러 입니다.",
      version="0.0.1",
      # 설치시 의존성 추가
      setup_requires=["py2app"],
      app=["standalone/run_gui.py"],
      options={
          "py2app": {
              # PySide2 구동에 필요한 모듈들은 포함시켜줍니다.
              "includes": ["PySide2.QtCore",
                           "PySide2.QtCore.QCoreApplication",
                           "PySide2.QtCore.QMetaObject",
                           "PySide2.QtCore.QObject",
                           "PySide2.QtCore.QPoint",
                           "PySide2.QtCore.QRect",
                           "PySide2.QtCore.QSize",
                           "PySide2.QtCore.QUrl",
                           "PySide2.QtCore.Qt",
                           "PySide2.QtGui",
                           "PySide2.QtGui.QBrush",
                           "PySide2.QtGui.QColor",
                           "PySide2.QtGui.QConicalGradient",
                           "PySide2.QtGui.QFontDatabase",
                           "PySide2.QtGui.QIcon",
                           "PySide2.QtGui.QLinearGradient",
                           "PySide2.QtGui.QPalette",
                           "PySide2.QtGui.QPainter",
                           "PySide2.QtGui.QPixmap",
                           "PySide2.QtGui.QRadialGradient",
                           "PySide2.QtWidgets"
                           "PySide2.QtWidgets.*"]
          }
      })