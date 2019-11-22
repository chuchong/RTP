import random
import math
import time
import sys
import threading
import socket

class Server:
    INIT = 0
    READY = 1
    PLAYING = 2
    def __init__(self):
        self.state = Server.INIT
