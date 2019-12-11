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
        MainWindow.resize(960, 796)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.init = QtWidgets.QPushButton(self.centralwidget)
        self.init.setGeometry(QtCore.QRect(20, 620, 211, 81))
        self.init.setObjectName("init")
        self.play = QtWidgets.QPushButton(self.centralwidget)
        self.play.setGeometry(QtCore.QRect(240, 620, 211, 81))
        self.play.setObjectName("play")
        self.pause = QtWidgets.QPushButton(self.centralwidget)
        self.pause.setGeometry(QtCore.QRect(460, 620, 211, 81))
        self.pause.setObjectName("pause")
        self.teardown = QtWidgets.QPushButton(self.centralwidget)
        self.teardown.setGeometry(QtCore.QRect(680, 620, 201, 81))
        self.teardown.setObjectName("teardown")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 882, 561))
        self.label.setText("")
        self.label.setObjectName("label")
        self.slider = QtWidgets.QSlider(self.centralwidget)
        self.slider.setGeometry(QtCore.QRect(20, 590, 851, 22))
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.speedBox = QtWidgets.QComboBox(self.centralwidget)
        self.speedBox.setGeometry(QtCore.QRect(110, 720, 87, 22))
        self.speedBox.setObjectName("speedBox")
        self.speedBox.addItem("")
        self.speedBox.addItem("")
        self.speedBox.addItem("")
        self.speedBox.addItem("")
        self.speedBox.addItem("")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 720, 72, 15))
        self.label_2.setObjectName("label_2")
        self.fullScreen = QtWidgets.QPushButton(self.centralwidget)
        self.fullScreen.setGeometry(QtCore.QRect(220, 720, 93, 28))
        self.fullScreen.setObjectName("fullScreen")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 26))
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
        self.speedBox.setItemText(0, _translate("MainWindow", "1.0"))
        self.speedBox.setItemText(1, _translate("MainWindow", "1.5"))
        self.speedBox.setItemText(2, _translate("MainWindow", "2.0"))
        self.speedBox.setItemText(3, _translate("MainWindow", "0.75"))
        self.speedBox.setItemText(4, _translate("MainWindow", "0.5"))
        self.label_2.setText(_translate("MainWindow", "播放速度"))
        self.fullScreen.setText(_translate("MainWindow", "全屏显示"))

