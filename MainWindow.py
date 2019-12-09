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
        self.frameNbr = 0
        self.buffer = queue.Queue() # 多线程显示缓存的列表
        self.rtsp = Rtsp()
        self.params = {}
        self.onRtp = False # 是否正在使用rtp进行传输
        self.frame_cnt = 0
        self.frame_pos = 0

        self.slider.setMaximum(self.SLIDER_SIZE)
        self.init.clicked.connect(self.setupMovie)
        self.play.clicked.connect(self.playMovie)
        self.pause.clicked.connect(self.pauseMovie)
        self.teardown.clicked.connect(self.exitClient)

    def sendRequest(self, *args, **kwargs):
        self.rtspSeq += 1
        message = self.rtsp.request(self.requestSent, self.fileName, self.rtpPort, self.rtspSeq,
                                    self.sessionId, *args, **kwargs)
        self.rtspSocket.send(message.encode())
        self.recvRtspReply()

    @qt_exception_wrapper
    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.requestSent = METHOD.SETUP
            self.sendRequest()
            self.requestSent = METHOD.GET_PARAMETER
            self.sendRequest(Rtsp.getParamFromEnum(PARAM.FRAME_CNT))
            self.frame_cnt = self.params[Rtsp.getParamFromEnum(PARAM.FRAME_CNT)]

    @qt_exception_wrapper
    def exitClient(self):
        """Teardown button handler."""
        try:
            self.requestSent = METHOD.TEARDOWN
            self.sendRequest()
        except Exception as e:
            print(e)
        self.close()

    @qt_exception_wrapper
    def pauseMovie(self):
        """Pause button handler."""
        if self.state == self.PLAYING:
            self.requestSent = METHOD.PAUSE
            self.sendRequest()

    @qt_exception_wrapper
    def playMovie(self):
        """Play button handler."""
        if self.state == self.READY:
            # Create a new thread to listen for RTP packets

            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.requestSent = METHOD.PLAY
            self.sendRequest()
            t = threading.Thread(target=self.refreshFrame)
            t.setDaemon(True) # 后台线程号结束
            t.start()
            t = threading.Thread(target=self.listenRtp)
            t.setDaemon(True)
            t.start()

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refreshSlider)
            self.timer.start(20)

    def listenRtp(self):
        """Listen for RTP packets."""
        while True:
            # print('listen')
            try:
                data = self.rtpSocket.recv(65535)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    currFrameNbr = rtpPacket.seqNum()
                    # print('receive ', currFrameNbr)
                    # self.buffer.append(rtpPacket)

                    # print("Current Seq Num: " + str(currFrameNbr))
                    #
                    if currFrameNbr > self.frameNbr:  # Discard the late packet
                        self.buffer.put(rtpPacket)
                        self.frameNbr = currFrameNbr
                        # self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
            except:
                # Stop listening upon requesting PAUSE or TEARDOWN
                if self.playEvent.isSet():
                    return

                # Upon receiving ACK for TEARDOWN request,
                # close the RTP socket
                if self.teardownAcked == 1:
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()

    @qt_exception_wrapper
    def refreshSlider(self):
        ratio = float(self.frame_pos) / float(self.frame_cnt)
        pos = int(ratio * self.SLIDER_SIZE)
        self.slider.setValue(pos)

    @qt_exception_wrapper
    def refreshFrame(self):
        # 多线程显示图片
        while True:
            try:
                if self.playEvent.isSet():
                    return

                # Upon receiving ACK for TEARDOWN request,
                # close the RTP socket
                if self.teardownAcked == 1:
                    # self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    # self.rtpSocket.close()
                    return
                # stime = time.time()
                # rtpPacket = self.buffer.pop(0)
                rtpPacket = self.buffer.get()
                self.frame_pos = rtpPacket.seqNum()
                # ratio = (self.SLIDER_SIZE * seqNum / self.frame_cnt)
                # self.slider.setValue(int(ratio))
                self.updateMovie(rtpPacket.getPayload())
                # self.updateMovie(self.writeFrame(rtpPacket.getPayload()))

            except Exception as e:
                # 可能是没图片了
                print(e)
                return
            # etime = time.time()
            # deltaTime = etime - stime #差值为s为单位
            # remainTime = 0.05 - deltaTime
            # if remainTime > 0:
            #     time.sleep(remainTime)


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
