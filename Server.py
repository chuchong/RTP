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

    def __init__(self, connSocket, clientAddress):
        self.state = Server.INIT
        self.connSocket = connSocket
        self.clientAddress = clientAddress
        self.rtsp = Rtsp()
        self.rtpSocket = None
        self.params = {}
        self.event = threading.Event()
        self.session = 0

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
            return message

    def set_params(self, seq, params):
        paramList = []
        for key in params.keys():
            self.params[key] = params[key]
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

        counter = 0
        thresold = 10

        while True:
            # self.event.wait(0.0166)
            if self.event.isSet():
                print("set event")
                break

            data = self.videoStream.nextFrame()
            if data:
                try:
                    frameNum = self.videoStream.getFrameNum()
                    port = self.rtpPort
                    self.rtpSocket.sendto(self.makeRtp(data, frameNum),
                                      (self.clientAddress[0],#accept 返回的address 是二元组
                                       port))
                    time.sleep(0.05)
                except:
                    print('error happen')
                    traceback.print_exc(file=sys.stdout)

    def makeRtp(self, data, frameNum):

        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26  # MJPEG type
        seqnum = frameNum
        ssrc = 0

        rtpPacket = RtpPacket.RtpPacket()

        rtpPacket.encode(version, padding, extension, cc, seqnum,
                         marker, pt, ssrc,
                         data)

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
        # port = sys.argv[1]
        # main(int(port))
        port = 8000
        main(port)
    except:
        raise Exception('argv incorrect')
