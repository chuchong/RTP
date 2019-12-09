# -*- coding: utf-8 -*-
# import Client
from tkinter import *
from tkinter import Tk

# from Client import Client
#
serverAddr = "127.0.0.1"
serverPort = 8000
rtpPort = 12455
fileName = "Sekiro.mp4"
# root = Tk()
# client = Client(root, serverAddr, serverPort, rtpPort, fileName)
# client.master.title('Client')
# root.mainloop()

import sys
from MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
app = QApplication(sys.argv)
mainWindow = MainWindow(serverAddr, serverPort, rtpPort, fileName)
mainWindow.show()
#    mainWindow.test()
sys.exit(app.exec_())
