# -*- coding: utf-8 -*-
# 主页面
# import Client
from tkinter import *
from tkinter import Tk

try:
    serverAddr = sys.argv[1]
except:
    serverAddr = "127.0.0.1"
    print('serverAddr default to 127.0.0.1')

try:
    serverPort = sys.argv[2]
except:
    serverPort = 8000
    print('serverPort default to 8000')

try:
    rtpPort = sys.argv[3]
except:
    rtpPort = 12451
    print('rtpPort default to 12451')

try:
    fileName = sys.argv[4]
except:
    fileName = 'SekiroH.mp4'
    print('folderName default to Sekiro.mp4')

import sys
from MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from FullScreenWindows import FullScreenWindow
app = QApplication(sys.argv)
mainWindow = MainWindow(serverAddr, serverPort, rtpPort, fileName)
mainWindow.show()
# mainwindow = FullScreenWindow(None)
# mainwindow.show()
#    mainWindow.test()
sys.exit(app.exec_())
