# -*- coding: utf-8 -*-
import random
import math
import time
import sys
import threading
import traceback
import socket
import RtpPacket
PACKET_DATA_SIZE = 256

from VideoStream import *
from Rtsp import *

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
        self.quality = 0

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
            rtpPort = ports[0]
            message = self.setup(filename, seq, rtpPort)
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
            # self.event = threading.Event()
            self.event.clear()
            self.worker = threading.Thread(target=self.sendRtp)
            self.worker.setDaemon(True)
            self.worker.start()
        elif self.state == self.PAUSE:
            self.state = self.PLAYING
            self.event.clear()
            self.worker = threading.Thread(target=self.sendRtp)
            self.worker.setDaemon(True)
            self.worker.start()
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

    def sendRtp(self):

        self.rtpLock.acquire()
        counter = 0
        thresold = 10

        while True:
            if self.event.isSet():
                print("set event")
                break

            data = self.videoStream.nextFrame()
            if data:
                marker = 0
                timestamp = int(time.time())
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
                        time.sleep(self.sleepTime)

                        lenOffset += length
                        offset += 1
                    except:
                        print('error happen')
                        traceback.print_exc(file=sys.stdout)
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
    rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rtspSocket.bind(('', port))
    rtspSocket.listen(5)

    while True:
        connSocket, address = rtspSocket.accept()
        t= threading.Thread(target=newServer, args=(connSocket, address))
        t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except:
        print('no port input, default to 8000')
        port = 8000
    main(int(port))
