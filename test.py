# a = 10 ** 5
# print(type(a))
import os

# import time
# a = time.time()
# for i in range(10000):
#     print(1)
# b = time.time()
#
# print(b - a)

# class VideoStream:
#     """mjpeg/mjpg格式用的stream"""
#     def __init__(self, filename):
#         self.filename = filename
#         self.size =  os.path.getsize(filename)
#         try:
#             self.file = open(filename, 'rb')
#         except Exception:
#             print('cannot read', filename)
#             raise IOError
#         self.frameNum = 0
#
#     def byte2int(self, byteArr):
#
#         zero = 48
#         size = len(byteArr)
#         dec = 0
#
#         for i in range(size):
#             dec = dec + (10 ** (size - 1 - i)) * (byteArr[i] - zero)
#         #
#         # print(dec)
#         return dec
#
#     def nextFrame(self):
#         data = self.file.read(5)
#         data = bytearray(data)
#
#         dataInt = self.byte2int(data)
#         finalInt = dataInt
#
#         if data:
#             frameLength = finalInt
#             frame = self.file.read(frameLength)
#             if len(frame) != frameLength:
#                 raise ValueError('Error: incomplete')
#
#             self.frameNum = self.frameNum + 1
#
#             return frame, frameLength
#
#     def getFrameCnt(self):
#         self.file.seek(0)
#
#         self.frameSets = []
#         pos = 0
#         while True:
#             try:
#                 _, framePos = self.nextFrame()
#                 self.frameSets.append(pos)
#                 pos += framePos
#                 if pos >= self.size:
#                     break
#             except:
#                 break
#
#         return len(self.frameSets)
#
#
# stream = VideoStream('video.mjpg')
# cnt = stream.getFrameCnt()
# print(cnt)
# for i in stream.frameSets:
#     print(i)

# import cv2
# image = cv2.imread('test.png')
# quality = 100
# while True:
#     q = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
#     imageBytes = cv2.imencode('.jpg', image, q)[1].tobytes()
#     if len(imageBytes) < 65535 * 8:
#         break
#     quality -= 10
# with open('test.jpg', 'wb') as f:
#     f.write(imageBytes)

# import re
# reg = re.compile('^(.*): (.*)$')
# strlines = ['a: 1\n', 'b: 2\n', 'c: 3\n', 'd: 4\n']
# for line in strlines:
#     match = reg.match(line)
#     print(match[1], match[2])
# # print(a)
#
# port = 'a-b'
# k = port.split('-')
# print(k)
#
# def test(args=[], kwargs = {}):
#     if len(args):
#         for i in args:
#             print(i)

# test([1,2,3,4])
# test()

import time, threading

#
#
# time.sleep(5)
# l = threading.Lock()
# def x():
#     l.acquire()
# t = threading.Thread(target=x).start()
#
# l.acquire()

a = bytearray(10)
# b = bytearray(b'12345')
# c = bytearray(b'67890')
# a = a + b + c
# print(a[2:5])
a += bytearray([12,12,12])
b = bytearray(20)
b[0:13] = a[:]
print(a[:])