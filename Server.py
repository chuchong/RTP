import random
import math
import time
import sys
import threading
import traceback
import socket
import RtpPacket
PACKET_DATA_SIZE = 256

from VideoStream import VideoStream
class Server:

    INIT = 0
    READY = 1
    PLAYING = 2
    PAUSE = 3

    def __init__(self, connSocket, clientAddress):
        self.state = Server.INIT
        self.connSocket = connSocket
        self.clientAddress = clientAddress

    def respond(self, code, seq):
        if code == 200:
            reply = 'RTSP/1.0 200 OK\nCSeq: ' + str(seq) + '\nSession: '+ str(self.session)
            connSocket = self.connSocket
            connSocket.send(reply.encode())

        else:
            print("Error: code is not 200")


    def run(self):
        threading.Thread(target=self.recvRtspRequest).start()

    def recvRtspRequest(self):
        while True:
            data = self.connSocket.recv(PACKET_DATA_SIZE)
            if data:
                self.processRtspRequest(data.decode())

    def processRtspRequest(self, data):

        request = data.split('\n')

        firstLine = request[0].split(' ')
        requestType, filename = firstLine[0], firstLine[1]

        seq = request[1].split(' ')[1]

        if requestType == 'SETUP':
            rtpPort = request[2].split(' ')[3]
            self.setup(filename, seq, rtpPort)
        elif requestType == 'PLAY':
            self.play(seq)
        elif requestType == 'PAUSE':
            self.pause(seq)
        elif requestType == 'TEARDOWN':
            self.teardown(seq)

    def setup(self, filename, seq, rtpPort):
        if self.state == self.INIT:
            try:
                self.videoStream = VideoStream(filename)
                self.state = self.READY
            except IOError:
                self.respond(404, seq)

            self.session = random.randint(100000,999999)
            self.respond(200, seq)
            self.rtpPort = int(rtpPort)

    def play(self, seq):
        if self.state == self.READY:
            self.state = self.PLAYING

            self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.event = threading.Event()
            self.worker = threading.Thread(target=self.sendRtp)
            self.worker.start()
            self.respond(200, seq)
        elif self.state == self.PAUSE:
            self.state = self.PLAYING

    def pause(self,seq):
        if self.state == self.PLAYING:
            self.state = self.READY
            self.event.set()
            self.respond(200, seq)

    def teardown(self, seq):
        self.event.set()
        self.respond(200, seq)
        self.rtpSocket.close()

    def sendRtp(self):

        counter = 0
        thresold = 10

        while True:
            self.event.wait(0.05)

            if self.event.isSet():
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

def main(port):
    rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rtspSocket.bind(('', port))
    rtspSocket.listen(5)

    while True:
        connSocket, address = rtspSocket.accept()
        Server(connSocket, address).run()

if __name__ == '__main__':
    try:
        port = sys.argv[1]
        main(int(port))
    except:
        raise Exception('argv incorrect')
