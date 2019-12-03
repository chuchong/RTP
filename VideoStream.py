
class VideoStream:
    """mjpeg/mjpg格式用的stream"""
    def __init__(self, filename):
        self.filename = filename
        try:
            self.file = open(filename, 'rb')
        except Exception:
            print('cannot read', filename)
            raise IOError
        self.frameNum = 0

    def byte2int(self, byteArr):

        zero = 48
        size = len(byteArr)
        dec = 0

        for i in range(size):
            dec = dec + (10 ** (size - 1 - i)) * (byteArr[i] - zero)

        print(dec)
        return dec

    def nextFrame(self):
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

            return frame

    def getFrameNum(self):
        return self.frameNum

