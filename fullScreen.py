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
        self.widget.setGeometry(QtCore.QRect(10, 880, 1280, 80))
        self.widget.setObjectName("widget")
        self.layoutWidget = QtWidgets.QWidget(self.widget)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 1261, 76))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.play = QtWidgets.QPushButton(self.layoutWidget)
        self.play.setObjectName("play")
        self.gridLayout.addWidget(self.play, 1, 2, 1, 1)
        self.exit = QtWidgets.QPushButton(self.layoutWidget)
        self.exit.setObjectName("exit")
        self.gridLayout.addWidget(self.exit, 1, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 1, 5, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 4, 1, 1)
        self.pause = QtWidgets.QPushButton(self.layoutWidget)
        self.pause.setObjectName("pause")
        self.gridLayout.addWidget(self.pause, 1, 1, 1, 1)
        self.slider = QtWidgets.QSlider(self.layoutWidget)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.gridLayout.addWidget(self.slider, 0, 0, 1, 6)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.play.setText(_translate("Form", "开始"))
        self.exit.setText(_translate("Form", "退出全屏"))
        self.comboBox.setItemText(0, _translate("Form", "1"))
        self.comboBox.setItemText(1, _translate("Form", "1.5"))
        self.comboBox.setItemText(2, _translate("Form", "2"))
        self.comboBox.setItemText(3, _translate("Form", "0.75"))
        self.comboBox.setItemText(4, _translate("Form", "0.5"))
        self.label_2.setText(_translate("Form", "播放速率"))
        self.pause.setText(_translate("Form", "暂停"))

