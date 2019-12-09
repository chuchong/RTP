# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clientUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(889, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.init = QtWidgets.QPushButton(self.centralwidget)
        self.init.setGeometry(QtCore.QRect(20, 390, 211, 131))
        self.init.setObjectName("init")
        self.play = QtWidgets.QPushButton(self.centralwidget)
        self.play.setGeometry(QtCore.QRect(240, 390, 211, 131))
        self.play.setObjectName("play")
        self.pause = QtWidgets.QPushButton(self.centralwidget)
        self.pause.setGeometry(QtCore.QRect(460, 390, 211, 131))
        self.pause.setObjectName("pause")
        self.teardown = QtWidgets.QPushButton(self.centralwidget)
        self.teardown.setGeometry(QtCore.QRect(680, 390, 201, 131))
        self.teardown.setObjectName("teardown")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 831, 311))
        self.label.setText("")
        self.label.setObjectName("label")
        self.slider = QtWidgets.QSlider(self.centralwidget)
        self.slider.setGeometry(QtCore.QRect(20, 360, 851, 22))
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 889, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.init.setText(_translate("MainWindow", "init"))
        self.play.setText(_translate("MainWindow", "play"))
        self.pause.setText(_translate("MainWindow", "pause"))
        self.teardown.setText(_translate("MainWindow", "teardown"))

