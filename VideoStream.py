import os
import cv2
DEFAULT_FPS = 24
class VideoStream:
    """mjpeg/mjpg格式用的stream"""
    def __init__(self, filename):
        self.filename = filename
        try:
            self.file = open(filename, 'rb')
        except Exception:
            print('cannot read', filename)
            raise IOError
        self.frameCnt = self._getFrameCnt()
        self.frameNum = 0

    def _getFrameCnt(self):
        self.file.seek(0)

        self.frameSets = []
        pos = 0
        while True:
            try:
                _, framePos = self._nextFrame()
                self.frameSets.append(pos)
                pos += framePos
            except:
                break

        self.file.seek(0)
        return len(self.frameSets)

    def getFrameCnt(self):
        return self.frameCnt

    def byte2int(self, byteArr):

        zero = 48
        size = len(byteArr)
        dec = 0

        for i in range(size):
            dec = dec + (10 ** (size - 1 - i)) * (byteArr[i] - zero)

        print(dec)
        return dec

    def _nextFrame(self):
        data = self.file.read(5)
        data = bytearray(data)

        dataInt = self.byte2int(data)
        finalInt = dataInt

        if data:
            frameLength = finalInt
            frame = self.file.read(frameLength)
            if len(frame) != frameLength:
                raise ValueError('Error: incomplete')

            self.frameNum = self.frameNum + 1

            return frame, frameLength

    def setCurFrame(self, frame):
        self.frameNum = frame

    def nextFrame(self):
        frame, _ = self._nextFrame()
        return frame

    def getFrameNum(self):
        return self.frameNum

    def getFps(self):
        return DEFAULT_FPS #这个不清楚


class JpgsStream:
    """mjpeg/mjpg格式用的stream"""
    def __init__(self, folder):
        self.folder = folder
        try:
            self.files = os.listdir(folder)
        except Exception:
            print('cannot read', folder)
            raise IOError
        self.frameNum = 0

    def nextFrame(self):
        if self.frameNum < len(self.files):
            filename = os.path.join(self.folder, self.files[self.frameNum])
            file = open(filename, 'rb')
            frame = file.read()
            self.frameNum = self.frameNum + 1

            return frame

    def getFrameCnt(self):
        return len(self.files)


    def getFrameNum(self):
        return self.frameNum

    def setCurFrame(self, frame):
        self.frameNum = frame

    def getFps(self):
        return DEFAULT_FPS #这个不清楚

class Mp4Stream:
    """用opencv提取序列帧"""
    def __init__(self, filename):
        self.filename = filename
        try:
            # self.file = open(filename, 'rb')
            self.capture = cv2.VideoCapture(filename)
        except:
            raise IOError

        self.frameNum = 0
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.frameCnt = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.totalTime = self.frameCnt / self.fps
        self.quality = 50

    def setCurFrame(self, frame):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame)
        self.frameNum = frame

    def nextFrame(self):
        # if self.capture.get(cv2.CAP_PROP_POS_MSEC) > self.totalTime:
        #     return None

        # 动态调整图片大小
        # if self.frameNum % 10 == 0 and self.quality < 100:
        #     self.quality += 10

        success , image = self.capture.read()
        if success:
            # print("sending images")
            self.frameNum += 1
            # imageBytes = cv2.imencode('.jpg', image)[1].tostring()

            while True:
                q = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                imageBytes = cv2.imencode('.jpg', image, q)[1].tobytes()
                if len(imageBytes) < 65535 * 8:
                    break
                self.quality -= 10
            return imageBytes

        return None

    def getFrameNum(self):
        return self.frameNum

    def getFrameCnt(self):
        return self.frameCnt

    def getFps(self):
        return self.fps

