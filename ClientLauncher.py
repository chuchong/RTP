# -*- coding: utf-8 -*-
# import Client
from tkinter import *
from tkinter import Tk

# from Client import Client
#
serverAddr = "127.0.0.1"
serverPort = 8000
rtpPort = 12450
fileName = "SekiroHD.mp4"
# root = Tk()
# client = Client(root, serverAddr, serverPort, rtpPort, fileName)
# client.master.title('Client')
# root.mainloop()

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
