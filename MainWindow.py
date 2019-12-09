# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
from PyQt5.QtWidgets import QApplication, QMainWindow
import os
import threading
import queue
import socket
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
from clientUI import Ui_MainWindow
from RtpPacket import RtpPacket
from Rtsp import *

#用于显示bug,只放在最顶层的函数上
CACHE_FILE_EXT = ".jpg"

def qt_exception_wrapper(func):
    def wrapper(self):
        try:
            func(self)
        except Exception as e:
            QMessageBox.information(self, 'Error', 'Meet with Error: ' + str(e),
                QMessageBox.Yes, QMessageBox.Yes)
    return wrapper

class MainWindow(QMainWindow, Ui_MainWindow):
    ##状态
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    SLIDER_SIZE = 255
    def __init__(self, serveraddr, serverport, rtpport, filename):
        super().__init__()
        # 原client的
        self.setupUi(self)
        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0

        self.connectToServer()
        # 我用来初始化的
        self.basicFps = 0
        self.fps = 0
        self.speed = 1

        self.bufferQueue = queue.Queue() # 多线程显示缓存的列表
        self.rtsp = Rtsp()
        self.params = {}
        self.playEvent = threading.Event()
        self.playLock = threading.Lock()
        self.rtpLock = threading.Lock()
        self.refreshLock = threading.Lock()
        self.frame_cnt = 0
        self.frame_pos = 0
        self.timer = QTimer(self)

        self.slider.setMaximum(self.SLIDER_SIZE)
        self.slider.sliderPressed.connect(self.pressSlider)
        self.slider.sliderReleased.connect(self.releaseSlider)
        self.init.clicked.connect(self.setupMovie)
        self.play.clicked.connect(self.playMovie)
        self.pause.clicked.connect(self.pauseMovie)
        self.teardown.clicked.connect(self.exitClient)
        self.timer.timeout.connect(self.refreshSlider)
        self.speedBox.currentIndexChanged.connect(self.changeSpeedBox)


    def sendRequest(self, *args, **kwargs):
        self.rtspSeq += 1
        message = self.rtsp.request(self.requestSent, self.fileName, self.rtpPort, self.rtspSeq,
                                    self.sessionId, *args, **kwargs)
        self.rtspSocket.send(message.encode())
        self.recvRtspReply()

    def changeSpeed(self, speed):
        self.fps = int(self.basicFps * speed)
        self.cycle = 1 / self.fps

    @qt_exception_wrapper
    def changeSpeedBox(self):
        speed = float(self.speedBox.currentText())
        self.changeSpeed(speed)

    @qt_exception_wrapper
    def pressSlider(self):
        self.timer.stop()
        if self.state != self.INIT:
            self.preSliderValue = self.slider.value()

    @qt_exception_wrapper
    def releaseSlider(self):
        dirtyFlag = False #脏标记表示是否已经暂停了
        if self.state == self.READY:
            dirtyFlag = True
        if self.state != self.INIT:
            if self.state == self.PLAYING:
                self.pauseMovie()
            value = self.slider.value()
            if value != self.preSliderValue:
                ratio = value / self.SLIDER_SIZE

                self.frame_pos = int(ratio * self.frame_cnt)
                assert(Rtsp.params[PARAM.FRAME_POS]=='frame_pos')#由于kwargs没有那么智能,只能这样了
                self.requestSent = METHOD.SET_PARAMETER
                self.sendRequest(frame_pos=self.frame_pos)
                # 重新播放
                self.state = self.READY
                self.playMovie()

                if dirtyFlag:
                    self.pauseMovie()


    @qt_exception_wrapper
    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.requestSent = METHOD.SETUP
            self.sendRequest()
            self.requestSent = METHOD.GET_PARAMETER
            frame_cnt = Rtsp.getParamFromEnum(PARAM.FRAME_CNT)
            fps = Rtsp.getParamFromEnum(PARAM.FPS)
            self.sendRequest(frame_cnt, fps)
            self.frame_cnt = float(self.params[Rtsp.getParamFromEnum(PARAM.FRAME_CNT)])
            self.basicFps = int(float(self.params[fps]))
            self.changeSpeed(self.speed)

    @qt_exception_wrapper
    def exitClient(self):
        """Teardown button handler."""
        # 不用考虑同步,关了就行
        try:
            self.requestSent = METHOD.TEARDOWN
            self.sendRequest()
        except Exception as e:
            print(e)
        self.close()

    @qt_exception_wrapper
    def pauseMovie(self):
        """Pause button handler."""
        # 暂停必然需要跳出了playLock

        if self.state == self.PLAYING:
            self.requestSent = METHOD.PAUSE
            self.sendRequest()
            # TODO 检查这里同步的正确性
            # 需要完全跳出playloop才能进行后续操作
            self.playLock.acquire()
            self.playLock.release()

    @qt_exception_wrapper
    def playMovie(self):
        """Play button handler."""
        if self.state == self.READY:
            # Create a new thread to listen for RTP packets
            self.requestSent = METHOD.SET_PARAMETER
            self.sendRequest(frame_pos=self.frame_pos)

            self.playEvent.clear()
            self.requestSent = METHOD.PLAY
            self.sendRequest()
            t = threading.Thread(target=self.playLoop)
            t.setDaemon(True)
            t.start()
            self.timer.start(20)

    def playLoop(self):
        # 播放的主循环,主要要使用其来同步listen和refresh
        self.playLock.acquire()
        t = threading.Thread(target=self.refreshFrame)
        t.setDaemon(True)  # 后台线程号结束
        t.start()
        t = threading.Thread(target=self.listenRtp)
        t.setDaemon(True)
        t.start()
        self.refreshLock.acquire()
        self.rtpLock.acquire()
        # 当两个都结束时,析构一些变量
        self.bufferQueue = queue.Queue()
        self.refreshLock.release()
        self.rtpLock.release()
        # playLoop全局只有一个保证了refreshLock不会死锁
        self.playLock.release()

    def listenRtp(self):
        """Listen for RTP packets."""
        self.rtpLock.acquire()
        while True:
            # print('listen')
            try:
                data = self.rtpSocket.recv(65535)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    currFrameNbr = rtpPacket.seqNum()

                    if currFrameNbr > self.frame_pos:  # Discard the late packet
                        self.bufferQueue.put(rtpPacket)
            except:
                if self.teardownAcked == 1:
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()

                if self.playEvent.isSet():
                    break
        self.rtpLock.release()
    @qt_exception_wrapper
    def refreshSlider(self):
        if self.state != self.INIT:
            ratio = float(self.frame_pos) / float(self.frame_cnt)
            pos = int(ratio * self.SLIDER_SIZE)
            self.slider.setValue(pos)

    @qt_exception_wrapper
    def refreshFrame(self):
        """根据fps从队列中回复图像"""
        # 多线程显示图片
        self.refreshLock.acquire()

        while True:
            stime = time.time()
            try:
                if self.playEvent.isSet():
                    break

                if self.teardownAcked == 1:
                    break
                rtpPacket = self.bufferQueue.get()
                self.frame_pos = rtpPacket.seqNum()
                self.updateMovie(rtpPacket.getPayload())
            except Exception as e:
                #TODO rtcp可调整
                print(e)
            etime = time.time()
            deltaTime = etime - stime
            if deltaTime < self.cycle:
                time.sleep(self.cycle - deltaTime)
            else:
                pass# TODO 用rtcp调整
        self.refreshLock.release()

    def updateMovie(self, imageBytes):
        """Update the image file as video frame in the GUI."""

        image = QImage.fromData(imageBytes)
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)

    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except Exception as e:
            QMessageBox.information(self, 'Error', 'Meet with Error: ' + str(e),
                QMessageBox.Yes, QMessageBox.Yes)

    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        # while True:
        reply = self.rtspSocket.recv(1024)
        print(reply.decode())
        if reply:
            self.parseRtspReply(reply.decode("utf-8"))

        # Close the RTSP socket upon requesting Teardown
        if self.requestSent == METHOD.TEARDOWN:
            self.rtspSocket.shutdown(socket.SHUT_RDWR)
            self.rtspSocket.close()
            return
            # break

    def parseRtspReply(self, data):
        """Parse the RTSP reply from the server."""
        if self.requestSent == METHOD.SET_PARAMETER:
            try:
                seqNum, session, params = self.rtsp.parseReplySet(data)
                # TODO 检测是否和发送的一致
            except Exception as e:
                print(e)
                raise e
        elif self.requestSent == METHOD.GET_PARAMETER:
            try:
                seqNum, session, params = self.rtsp.parseReplyGet(data)
                for key in params.keys():
                    self.params[key] = params[key]
            except Exception as e:
                print(e)
                raise e
        else:
            try:
                seqNum, session = self.rtsp.parseReplyNormal(data)
            except Exception as e:
                print(e)
                raise e

            if self.requestSent == METHOD.SETUP:
                self.state = self.READY
                # Open RTP port.
                self.openRtpPort()
                self.sessionId = session
            elif self.requestSent == METHOD.PLAY:
                self.state = self.PLAYING
            elif self.requestSent == METHOD.PAUSE:
                self.state = self.READY
                # The play thread exits. A new thread is created on resume.
                self.playEvent.set()
            elif self.requestSent == METHOD.TEARDOWN:
                self.state = self.INIT
                # Flag the teardownAcked to close the socket.
                self.teardownAcked = 1
            else:
                raise Exception("Error: unvalid respond status")

        if session != self.sessionId:
            raise Exception("Error: session code not match!")
        # Process only if the server reply's sequence number is the same as the request's

    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        # Create a new datagram socket to receive RTP packets from the server
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set the timeout value of the socket to 0.5sec
        self.rtpSocket.settimeout(0.5)

        try:
            # Bind the socket to the address using the RTP port given by the client user
            self.rtpSocket.bind((self.serverAddr, self.rtpPort))
        except Exception as e:
            QMessageBox.information(self, 'Error', 'Meet with Error: ' + str(e),
                QMessageBox.Yes, QMessageBox.Yes)
