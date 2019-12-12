# -*- coding: utf-8 -*-
import random
import math
import time
import sys
import threading
import traceback
import socket
import RtpPacket
from RtcpPacket import *
PACKET_DATA_SIZE = 256

from VideoStream import *
from Rtsp import *
from time import time, sleep
class Server:

    INIT = 0
    READY = 1
    PLAYING = 2
    PAUSE = 3

    MAX_PAYLOAD_SIZE = 60000 # 少弄些防止出问题

    def __init__(self, connSocket, clientAddress):
        self.state = Server.INIT
        self.connSocket = connSocket
        self.clientAddress = clientAddress
        self.rtsp = Rtsp()
        self.rtpSocket = None
        self.params = {}
        self.event = threading.Event()
        self.rtpLock = threading.Lock()
        self.session = 0
        self.seqnum = 0

        # rtcp可以控制的地方
        self.sleepTime = 0.01
        self.quality = 30

    def run(self):
        self.recvRtspRequest()

    def recvRtspRequest(self):
        while True:
            try:
                data = self.connSocket.recv(PACKET_DATA_SIZE)
                if data:
                    print(data.decode())
                    self.processRtspRequest(data.decode())

                if len(data) == 0: # 0 代表已经断开
                    return
            except Exception as e:
                print(e)
                return

    def processRtspRequest(self, data):

        print(str(data))
        requestType, filename, seq, ports, session, params = self.rtsp.parseRequest(data)

        if requestType == METHOD.SETUP:
            self.rtpPort = ports[0]
            self.rtcpPort = int(ports[0])+1
            message = self.setup(filename, seq, self.rtpPort)
        elif requestType == METHOD.PLAY:
            message = self.play(seq)
        elif requestType == METHOD.PAUSE:
            message = self.pause(seq)
        elif requestType == METHOD.TEARDOWN:
            message = self.teardown(seq)
        elif requestType == METHOD.SET_PARAMETER:
            message = self.set_params(seq, params)
        elif requestType == METHOD.GET_PARAMETER:
            message = self.get_params(seq, params)
        else:
            message = self.rtsp.respond(405, seq, self.session)

        connSocket = self.connSocket
        connSocket.send(message.encode())

    def setup(self, filename, seq, rtpPort):
        if self.state == self.INIT:
            try:
                if filename.endswith('.mp4'):
                    self.videoStream = Mp4Stream(filename)
                elif filename.endswith('.mjpg') or filename.endswith('.mjpeg'):
                    self.videoStream = VideoStream(filename)
                else:
                    self.videoStream = JpgsStream(filename)

                self.state = self.READY
            except IOError:
                message = self.rtsp.respond(404, seq, self.session)
                return message

            self.session = random.randint(100000, 999999)
            message = self.rtsp.respond(200, seq, self.session)
            self.rtpPort = int(rtpPort)
            self.params[Rtsp.getParamFromEnum(PARAM.FRAME_CNT)] = self.videoStream.getFrameCnt()
            self.params[Rtsp.getParamFromEnum(PARAM.FPS)] = self.videoStream.getFps()
            return message

    def set_params(self, seq, params):
        paramList = []
        for key in params.keys():
            self.params[key] = params[key]
            if key == Rtsp.params[PARAM.FRAME_POS]:
                self.videoStream.setCurFrame(int(self.params[key]))
            if key == Rtsp.params[PARAM.QUALITY]:
                self.quality = int(self.params[key])
            paramList.append(key)
        message = self.rtsp.respond(200, seq, self.session, args=paramList)
        return message

    def get_params(self, seq, params):
        paramDict = {}
        for param in params:
            try:
                paramDict[param] = self.params.get(param)
            except:
                print('Error: No value {} found'.format(param))
                self.rtsp.respond(451, seq, self.session)
                return
        message = self.rtsp.respond(200, seq, self.session, kwargs=paramDict)
        return message

    def play(self, seq):
        if self.state == self.READY:
            self.state = self.PLAYING
            self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.rtcpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.event = threading.Event()
            self.event.clear()
            self.worker = threading.Thread(target=self.sendRtp)
            self.worker2 = threading.Thread(target=self.listenRtcp)
            self.worker.setDaemon(True)
            self.worker.start()
            self.worker2.start()
        elif self.state == self.PAUSE:
            self.state = self.PLAYING
            self.event.clear()
            self.worker = threading.Thread(target=self.sendRtp)
            self.worker2 = threading.Thread(target=self.listenRtcp)
            self.worker.setDaemon(True)
            self.worker.start()
            self.worker2.start()
        message = self.rtsp.respond(200, seq, self.session)
        return message

    def pause(self,seq):
        if self.state == self.PLAYING:
            self.state = self.READY
            self.event.set()
            message = self.rtsp.respond(200, seq, self.session)
        else:
            message = self.rtsp.respond(455, seq, self.session)
        return message

    def teardown(self, seq):
        self.event.set()
        message = self.rtsp.respond(200, seq, self.session)
        if self.rtpSocket:
            self.rtpSocket.close()
        return message

    def sendRtcp(self):
        try:
            print("****************send rtcp")
            port = self.rtcpPort
            rtcpPacket = SRRtcpPacket()
            rtcpPacket.exEncode(1,0,112,0,0,int(time()), 0, 0, 0)
            self.rtcpSocket.sendto(rtcpPacket.getPacket(),
                                  (self.clientAddress[0],  # accept 返回的address 是二元组
                                   port))
            print("****************send rtcp")

            data = self.rtcpSocket.recv(65536)
            print("rtcp is on**************************** {}".format(data))
            rtcpPacket = RRRtcpPacket()
            rtcpPacket.decode(data)
            lost = rtcpPacket.fracLost(0)
            print("**********lost{}".format(lost))
            if lost > 50:
                print("*******************wtf lost")
                if self.sleepTime < 0.05:
                    self.sleepTime = self.sleepTime * 1.1
                if self.MAX_PAYLOAD_SIZE > 32768:
                    self.MAX_PAYLOAD_SIZE -= 100
                if self.quality > 0:
                    self.quality -= 1
        except Exception as e:
            print(e)
            pass

    def listenRtcp(self):
        pass
        # while True:
        #     try:
        #         pass
        #
        #     except Exception as e:
        #         print(e)
        #         pass


    def sendRtp(self):

        self.rtpLock.acquire()
        counter = 0
        thresold = 10
        self.seqnum = 0
        while True:


            if self.event.isSet():
                print("set event")
                break

            data = self.videoStream.nextFrame()
            if data:
                marker = 0
                timestamp = int(time())
                self.videoStream.quality = self.quality
                frameNum = self.videoStream.getFrameNum()
                remainSize = len(data)
                lenOffset = 0
                offset = 0
                while remainSize:
                    if remainSize > self.MAX_PAYLOAD_SIZE // 4:
                        length = self.MAX_PAYLOAD_SIZE // 4
                    else:
                        length = remainSize
                        marker = 1

                    remainSize -= length
                    payload = data[int(lenOffset): int(lenOffset) + int(length)]

                    try:
                        port = self.rtpPort
                        self.rtpSocket.sendto(self.makeRtp(payload, frameNum, length, offset, timestamp, marker),
                                          (self.clientAddress[0],#accept 返回的address 是二元组
                                           port))
                        sleep(self.sleepTime)

                        lenOffset += length
                        offset += 1

                    except:
                        print('error happen')
                        traceback.print_exc(file=sys.stdout)

                    if self.seqnum % 20 == 19:
                        print('**************satisfied')
                        threading.Thread(target=self.sendRtcp).start()
        self.rtpLock.release()

    def makeRtp(self, data, frameNum, length, offset, timestamp, marker):

        self.seqnum += 1
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = marker
        pt = 26  # MJPEG type
        seqnum = self.seqnum
        ssrc = 0
        timestamp = timestamp
        length = length
        field = 0
        cont = 0
        lineNo = int(frameNum)
        offset = offset

        rtpPacket = RtpPacket.UncompressedRtp()

        rtpPacket.extendedEncode(version, padding, extension, cc, seqnum,
                         marker, pt, ssrc, timestamp,
                         data,
                         length, field, lineNo, cont, offset)
        print('frame{} seq{} length:{} offset:{} marker:{}'.format(lineNo, seqnum, length, offset, marker))
        return rtpPacket.getPacket()

def newServer(connSocket, address):
    Server(connSocket, address).run()

def main(port):
    connSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connSocket.bind(('', port))
    connSocket.listen(5)

    while True:
        rtspSocket, address = connSocket.accept()
        t= threading.Thread(target=newServer, args=(rtspSocket, address))
        t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except:
        print('no port input, default to 8000')
        port = 8000
    main(int(port))
