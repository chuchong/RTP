import Client
from tkinter import *
from tkinter import Tk

from Client import Client

serverAddr = "127.0.0.1"
serverPort = 8000
rtpPort = 12451
fileName = "video.mjpg"
root = Tk()
client = Client(root, serverAddr, serverPort, rtpPort, fileName)
client.master.title('Client')
root.mainloop()