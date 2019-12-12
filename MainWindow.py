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
from RtpPacket import *
from Rtsp import *
from FullScreenWindows import FullScreenWindow
from signal import RtpSignals
from RtcpPacket import *
from time import time, sleep
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

    FULL_SCREEN = 0
    SMALL_SCREEN = 1

    SLIDER_SIZE = 255
    DEFAULT_QUALITY = 20

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

        # 子窗口
        self.sonWidget = FullScreenWindow(None, self)
        # self.sonWidget.hide()
        # 我用来初始化的
        self.basicFps = 0
        self.fps = 0
        self.speed = 1
        self.frame_cnt = 0
        self.frame_pos = 0

        self.displayType = self.SMALL_SCREEN

        # 用以显示的多线程量
        self.bufferQueue = queue.Queue() # 多线程显示缓存的列表
        self.packetsQueue = queue.Queue()
        self.rtsp = Rtsp()
        self.params = {}
        self.playEvent = threading.Event()
        self.waitEvent = threading.Event()
        self.playLock = threading.Lock()
        self.rtpLock = threading.Lock()
        self.rtcpLock = threading.Lock()
        self.packetLock = threading.Lock()
        self.refreshLock = threading.Lock()
        self.timer = QTimer(self)

        self.slider.setMaximum(self.SLIDER_SIZE)
        self.slider.sliderPressed.connect(self.pressSlider)
        self.slider.sliderReleased.connect(self.releaseSlider)
        self.slider.setSingleStep(0)
        self.slider.setPageStep(0)
        self.init.clicked.connect(self.setupMovie)
        self.play.clicked.connect(self.playMovie)
        self.pause.clicked.connect(self.pauseMovie)
        self.teardown.clicked.connect(self.exitClient)
        self.fullScreen.clicked.connect(self.switchDisplay)
        self.timer.timeout.connect(self.refreshSlider)
        self.speedBox.currentIndexChanged.connect(self.changeSpeedBox)

        self.qualityEdit.setValidator(QIntValidator(1, 100))
        self.quality = self.DEFAULT_QUALITY
        self.setQualityB.clicked.connect(self.setQuality)

        self.labelWidth = self.label.width()
        self.labelHeight = self.label.height()

        self.sonWidget.slider.sliderPressed.connect(self.pressSlider)
        self.sonWidget.slider.sliderReleased.connect(self.releaseSlider)
        self.sonWidget.play.clicked.connect(self.playMovie)
        self.sonWidget.pause.clicked.connect(self.pauseMovie)
        self.sonWidget.exit.clicked.connect(self.switchDisplay)
        self.sonWidget.comboBox.currentIndexChanged.connect(self.changeSpeedBox)
        self.loadingLabel.setScaledContents(True)
        self.sonWidget.loadingLabel.setScaledContents(True)
        self.movie = QMovie("loading.gif")
        self.loadingLabel.setMovie(self.movie)
        self.wait.pressed.connect(self.waitMovie)
        self.sonWidget.loadingLabel.setMovie(self.movie)


        # 和子窗口的东西
        self.playLabel = self.label
        self.curBox = self.speedBox
        self.curSlider = self.slider

        self.rtpSignals = RtpSignals(self.sonWidget)
        self.rtpSignals.AnimeSignal.connect(self.sonAnime)
        self.rtpSignals.ReAnimeSignal.connect(self.sonReAnime)
        self.rtpSignals.LoadSignal.connect(self.loading)
        self.rtpSignals.LoadDoneSignal.connect(self.loadingDone)
        self.rtpSignals.VideoEndSignal.connect(self.pauseMovie)
        self.rtpSignals.NeedBufferSignal.connect(self.buffering)

        self.bufferLock = threading.Lock()
        self.sonLock=threading.Lock()

    def onSendAnime(self):
        self.rtpSignals.AnimeSignal.emit()

    def onSendReAnime(self):
        self.rtpSignals.ReAnimeSignal.emit()

    def buffering(self):
        if self.bufferLock.acquire(blocking=False):
            print("xxxxxxxxxxxxbufferingxxxxxxxxxx")
            self.loading()
            # QThread.msleep(1000)
            QTimer.singleShot(1000, self.bufferOut)

    def bufferOut(self):
        self.rtpSignals.LoadDoneSignal.emit()
        self.bufferLock.release()
        print("xxxxxxxxxxxxbuffer outxxxxxxxxxx")

    def sonAnime(self):
        self.sonLock.acquire()
        self.sonWidget.anime()
        self.sonLock.release()
    def sonReAnime(self):
        self.sonLock.acquire()
        self.sonWidget.reAnime()
        self.sonLock.release()
    def sendRequest(self, *args, **kwargs):
        self.rtspSeq += 1
        message = self.rtsp.request(self.requestSent, self.fileName, self.rtpPort, self.rtspSeq,
                                    self.sessionId, *args, **kwargs)
        self.rtspSocket.send(message.encode())
        self.recvRtspReply()

    def setQuality(self):
        quality = int(self.qualityEdit.text())
        if self.quality == quality:
            QMessageBox.information(self, '提示', '您当前quality已经是{}'.format(quality),
                                 QMessageBox.Ok)
        else:
            if quality > 40:
                select = QMessageBox.question(self, '警告', '您设置的视频质量过高,可能引起严重的失帧,卡顿,您还继续吗?',
                                     QMessageBox.Ok | QMessageBox.No)
                if select == QMessageBox.Ok:
                    pass
                else:
                    return
            QMessageBox.information(self, '提示', '选好了 quality为{}'.format(quality),
                                 QMessageBox.Ok)
            self.quality = quality

            dirtyFlag = False  # 脏标记表示是否已经暂停了
            if self.state == self.READY:
                dirtyFlag = True
            if self.state != self.INIT:
                if self.state == self.PLAYING:
                    self.pauseMovie()
                self.bufferQueue = queue.Queue()
                self.packetsQueue = queue.Queue()

                self.requestSent = METHOD.SET_PARAMETER
                self.sendRequest(frame_pos=self.frame_pos, quality=quality)

                self.state = self.READY
                self.playMovie()

                if dirtyFlag:
                    self.pauseMovie()

    def changeSpeed(self, speed):
        self.fps = int(self.basicFps * speed)
        self.cycle = 1 / self.fps

    def loading(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXloadingXXXXXXXXXXXXXXXXXXXXXXx")
        self.waitEvent.set()
        self.loadingLabel.show()
        self.sonWidget.loadingLabel.show()
        self.movie.start()

    def loadingDone(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXloading doneXXXXXXXXXXXXXXXXXXXXXXx")
        self.waitEvent.clear()
        self.loadingLabel.hide()
        self.sonWidget.loadingLabel.hide()

    def waitMovie(self):
        if self.state == self.INIT:
            QMessageBox.information(self, '欸', '请在play后再点击该按钮,作用是先等视频下载一会儿 ',
                QMessageBox.Yes, QMessageBox.Yes)
            return

        if self.waitEvent.isSet():
            self.waitEvent.clear()
            self.wait.setText('等待加载视频')
        else:
            self.waitEvent.set()
            self.wait.setText('播放')

    @qt_exception_wrapper
    def switchDisplay(self):
        if self.state != self.INIT:
            if self.displayType == self.FULL_SCREEN:
                self.show()
                self.sonWidget.exitToPar()
                self.displayType = self.SMALL_SCREEN
                self.playLabel = self.label
                self.curBox = self.speedBox
                self.curSlider = self.slider
                # self.sonWidget.exitToPar()

            else:
                self.displayType = self.FULL_SCREEN
                # self.sonWidget.setMouseTracking(True)
                self.playLabel = self.sonWidget.label
                self.curBox = self.sonWidget.comboBox
                self.curSlider = self.sonWidget.slider
                self.sonWidget.resizeToFill()
                self.hide()
                self.rtpSignals.start()

        else:
            raise Exception('Error: you need play video first')

    @qt_exception_wrapper
    def changeSpeedBox(self):
        speed = float(self.curBox.currentText())
        self.changeSpeed(speed)

    @qt_exception_wrapper
    def pressSlider(self):
        self.timer.stop()
        if self.state != self.INIT:
            self.preSliderValue = self.curSlider.value()

    @qt_exception_wrapper
    def releaseSlider(self):
        dirtyFlag = False #脏标记表示是否已经暂停了
        if self.state == self.READY:
            dirtyFlag = True
        if self.state != self.INIT:
            if self.state == self.PLAYING:
                self.pauseMovie()
            self.bufferQueue = queue.Queue()
            self.packetsQueue = queue.Queue()
            value = self.curSlider.value()
            if value != self.preSliderValue:
                if value == self.SLIDER_SIZE:
                    value -= 1
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
            if self.frame_cnt == 0:
                self.slider.setEnabled(False)
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
        self.sonWidget.close()

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

        t.start()
        t = threading.Thread(target=self.packetization)

        t.start()
        t = threading.Thread(target=self.listenRtp)

        t.start()
        t = threading.Thread(target=self.listenRtcp)

        t.start()
        self.refreshLock.acquire()
        self.rtpLock.acquire()
        # self.rtcpLock.acquire()
        self.packetLock.acquire()
        # 当两个都结束时,析构一些变量
        # self.bufferQueue = queue.Queue()
        # self.packetsQueue = queue.Queue()
        self.packetLock.release()
        self.refreshLock.release()
        # self.rtcpLock.release()
        self.rtpLock.release()
        # playLoop全局只有一个保证了refreshLock不会死锁
        self.playLock.release()

    def pushFrameRtp(self, frame, rtpPackets):
        """用于产生之后绘图使用的packet"""
        print("cope with frame: {}".format(frame))
        if frame > self.frame_pos:  # Discard the late packet
            rtpPacket = SimpleRtpPacket()
            rtpPacket.frame = frame
            for packet in rtpPackets:
                rtpPacket.payload += packet.getPayload()
            self.bufferQueue.put(rtpPacket)

    def packetization(self):
        """用于将udp裸包处理成可以被视频用的包"""
        self.packetLock.acquire()
        firstFlag = False
        lastFrameNbr = 0
        isComplete = True
        rtpPackets = []
        accumOffset = 0

        while True:
            if self.playEvent.isSet():
                print(' refresh into playevent')
                break
            if self.packetsQueue.empty():
                continue
            rtpPacket = self.packetsQueue.get()
            seqnum = rtpPacket.extendedSeq()
            frameNbr = rtpPacket.lineNo()
            timestamp = rtpPacket.timestamp()
            length = rtpPacket.length()
            offset = rtpPacket.offset()
            marker = rtpPacket.marker()
            self.ssrc = rtpPacket.ssrc()


            # if firstFlag:
            #     lastFrameNbr = frameNbr
            #     firstFlag = False

            #正常情况,连续一帧的分包
            if lastFrameNbr == frameNbr and isComplete:
                if seqnum != lastSeqnum + 1:
                    print("********abort frame {}".format(lastFrameNbr))
                    isComplete = False
                    rtpPackets.clear()
                else:
                    rtpPackets.append(rtpPacket)
                    accumOffset += length

                if marker == 1:
                    """marker = 1 代表一帧结束"""
                    print("++++++++++push frame {}".format(lastFrameNbr))
                    self.pushFrameRtp(frameNbr, rtpPackets)

            # 新的一帧的开始
            if lastFrameNbr != frameNbr:
                if offset == 0:
                    lastFrameNbr = frameNbr
                    isComplete = True
                    rtpPackets = []
                    accumOffset = 0

                    rtpPackets.append(rtpPacket)
                    accumOffset += length
                else:
                    isComplete = False
                    rtpPackets.clear()

                if marker == 1:
                    """marker = 1 代表一帧结束"""
                    print("++++++++push frame {}".format(lastFrameNbr))
                    self.pushFrameRtp(frameNbr, rtpPackets)

            lastSeqnum = seqnum

        self.packetLock.release()
            # if seqnum > self.frame_pos:  # Discard the late packet
            #     self.bufferQueue.put(rtpPacket)

    def listenRtcp(self):
        # self.rtcpLock.acquire()
        self.jitter = 0
        self.cumu_lost = 0
        lastlastseq = 0
        while True:
            # print('listen')

            if self.playEvent.isSet():
                break
            try:
                (data, address) = self.rtcpSocket.recvfrom(65536)
                print("receive RTCP")
                if data:
                    rtcpPacket = SRRtcpPacket()
                    rtcpPacket.decode(data)
                    rc = rtcpPacket.rc()
                    if rc == 203:
                        # BYE
                        break
                    padding = rtcpPacket.padding()
                    ssrc = rtcpPacket.sender_ssrc()
                    ntpH, ntpL = rtcpPacket.ntpTime()
                    rtp = rtcpPacket.rtpTime()
                    packCnt= rtcpPacket.packCnt()
                    octCnt = rtcpPacket.octCnt()


                    lsr = (ntpH >> 16 & 65535) + ntpL << 16
                    dlsr = int(time()) - ntpL
                    self.jitter = int(dlsr*0.1 + 0.9*self.jitter)
                    cumu_lost = self.lastSeqnum - self.startSeqnum - self.receivePackets
                    frac_lost = int((cumu_lost - self.cumu_lost) / (self.lastSeqnum - lastlastseq) * 255)
                    if frac_lost > 255:
                        frac_lost = 255
                    if frac_lost <0:
                        frac_lost = 0
                    lastlastseq = self.lastSeqnum
                    self.cumu_lost = cumu_lost
                    sendBackPacket = RRRtcpPacket()
                    print("current lost {}".format(frac_lost))
                    sendBackPacket.appendReportBlock(self.ssrc, frac_lost, self.cumu_lost,
                                                     self.lastSeqnum, self.jitter, lsr, dlsr)
                    sendBackPacket.encode(1, padding, 311, self.ssrc)


                    # print('seqnum {}'.format(seqnum))
                    # 收到后回答
                    self.rtcpSocket.sendto(sendBackPacket.getPacket(), address)

            except:
                if self.teardownAcked == 1:
                    self.rtcpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtcpSocket.close()

        # self.rtcpLock.release()

    def listenRtp(self):
        """Listen for RTP packets."""
        self.rtpLock.acquire()
        lastFrameNbr = 0
        lastSeqnum = 0
        isComplete = True
        rtpPackets = []
        accumOffset = 0
        flag = True
        self.startSeqnum = 0
        self.lastSeqnum = 0
        self.receivePackets = 0
        while True:
            # print('listen')
            if self.playEvent.isSet():
                print(' refresh into playevent')
                break
            try:
                data = self.rtpSocket.recv(65536)
                if data:
                    rtpPacket = UncompressedRtp()
                    rtpPacket.extendDecode(data)
                    seqnum = rtpPacket.extendedSeq()
                    frameNbr = rtpPacket.lineNo()
                    if flag:
                        flag = False
                        self.lastSeqnum = seqnum
                        self.startSeqnum = seqnum
                    # print('seqnum {}'.format(seqnum))
                    if seqnum >= self.lastSeqnum:
                        self.receivePackets += 1
                        self.lastSeqnum = seqnum
                        print('push {}'.format(seqnum))
                        self.packetsQueue .put(rtpPacket)

            except:
                print('listen error')
                if self.teardownAcked == 1:
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()


        self.rtpLock.release()
    @qt_exception_wrapper
    def refreshSlider(self):
        if self.state != self.INIT:
            if self.frame_cnt == 0:
                # self.slider.setEnabled(False)
                return
            ratio = float(self.frame_pos) / float(self.frame_cnt)
            pos = int(ratio * self.SLIDER_SIZE)
            self.slider.setValue(pos)

    @qt_exception_wrapper
    def refreshFrame(self):
        """根据fps从队列中回复图像"""
        # 多线程显示图片
        self.refreshLock.acquire()

        while True:
            # print('REFRESH')
            stime = time()
            try:
                if self.playEvent.isSet():
                    print(' refresh into playevent')
                    break

                if self.teardownAcked == 1:
                    break

                if self.waitEvent.isSet():
                    continue

                if self.bufferQueue.empty():
                    # 这代表了卡
                    if self.frame_pos == self.frame_cnt:
                        # 代表了放完了
                        self.rtpSignals.VideoEndSignal.emit()
                        # self.pauseMovie()
                    else:
                        self.rtpSignals.NeedBufferSignal.emit()
                    # self.rtpSignals.LoadSignal.emit()
                    # QThread.msleep(1000)
                    # self.rtpSignals.LoadDoneSignal.emit()
                    continue
                rtpPacket = self.bufferQueue.get()
                self.frame_pos = rtpPacket.frame
                self.updateMovie(rtpPacket.payload)
            except Exception as e:
                #TODO rtcp可调整
                print(e)
            etime = time()
            deltaTime = etime - stime
            if deltaTime < self.cycle:
                sleep(self.cycle - deltaTime)
            else:
                ## 等待一段时间
                pass# TODO 用rtcp调整
        self.refreshLock.release()

    def updateMovie(self, imageBytes):
        """Update the image file as video frame in the GUI."""

        if len(imageBytes) > 0:
            image = QImage.fromData(imageBytes)
            pixmap = QPixmap.fromImage(image)
            if pixmap.width() > self.labelWidth:
                pixmap = pixmap.scaledToWidth(self.labelWidth)
            self.sonLock.acquire()
            self.playLabel.setPixmap(pixmap)
            self.sonLock.release()

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
                self.openRtcpPort()
                self.sessionId = session
            elif self.requestSent == METHOD.PLAY:
                self.state = self.PLAYING
            elif self.requestSent == METHOD.PAUSE:
                print('request PAUSE')
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

    def openRtcpPort(self):
        self.rtcpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the timeout value of the socket to 0.5sec
        self.rtcpSocket.settimeout(0.5)

        try:
            # Bind the socket to the address using the RTP port given by the client user
            self.rtcpSocket.bind((self.serverAddr, self.rtpPort + 1))
        except Exception as e:
            QMessageBox.information(self, 'Error', 'Meet with Error: ' + str(e),
                QMessageBox.Yes, QMessageBox.Yes)
