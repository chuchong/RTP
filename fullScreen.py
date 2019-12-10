# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fullScreen.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1280, 960)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(0, 0, 1280, 900))
        self.label.setText("")
        self.label.setObjectName("label")
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(10, 880, 1920, 80))
        self.widget.setAutoFillBackground(True)
        self.widget.setObjectName("widget")
        self.slider = QtWidgets.QSlider(self.widget)
        self.slider.setGeometry(QtCore.QRect(1, 6, 1906, 22))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slider.sizePolicy().hasHeightForWidth())
        self.slider.setSizePolicy(sizePolicy)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.pause = QtWidgets.QPushButton(self.widget)
        self.pause.setGeometry(QtCore.QRect(212, 40, 93, 28))
        self.pause.setObjectName("pause")
        self.play = QtWidgets.QPushButton(self.widget)
        self.play.setGeometry(QtCore.QRect(423, 40, 93, 28))
        self.play.setObjectName("play")
        self.exit = QtWidgets.QPushButton(self.widget)
        self.exit.setGeometry(QtCore.QRect(1, 40, 93, 28))
        self.exit.setObjectName("exit")
        self.comboBox = QtWidgets.QComboBox(self.widget)
        self.comboBox.setGeometry(QtCore.QRect(1056, 43, 62, 21))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setGeometry(QtCore.QRect(845, 40, 60, 16))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pause.setText(_translate("Form", "暂停"))
        self.play.setText(_translate("Form", "开始"))
        self.exit.setText(_translate("Form", "退出全屏"))
        self.comboBox.setItemText(0, _translate("Form", "1"))
        self.comboBox.setItemText(1, _translate("Form", "1.5"))
        self.comboBox.setItemText(2, _translate("Form", "2"))
        self.comboBox.setItemText(3, _translate("Form", "0.75"))
        self.comboBox.setItemText(4, _translate("Form", "0.5"))
        self.label_2.setText(_translate("Form", "播放速率"))

