## 用于进行rtsp通讯,采用rtso/1.0
import enum
import re

@enum.unique
class METHOD(enum.Enum):
    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3
    GET_PARAMETER = 4
    SET_PARAMETER = 5

@enum.unique
class PARAM(enum.Enum):
    FRAME_CNT = 0 # 总的帧数
    FRAME_POS = 1 # 当前帧
    FPS = 2


class Rtsp:
    """产生rtsp通讯字符串"""
    params = {
        PARAM.FRAME_CNT:'frame_cnt',
        PARAM.FRAME_POS: 'frame_pos',
        PARAM.FPS: 'fps'}
    methods = ['SETUP', 'PLAY', 'PAUSE',
               'TEARDOWN', 'GET_PARAMETER', 'SET_PARAMETER']
    rtspVersion = 'RTSP/1.0'
    status={
            200: 'OK',
            405: 'Method Not Allowed',
            451: 'Parameter Not Understood',
            452: 'Conference Not Found',
            453: 'Not Enough Bandwidth',
            454: 'Session Not Found',
            455: 'Method Not Valid in This State',
            456: 'Header Field Not Valid for Resource',
            457: 'Invalid Range',
            458: 'Parameter Is Read-Only',
            459: 'Aggregate Operation Not Allowed',
            460: 'Only Aggregate Operation Allowed',
            461: 'Unsupported Transport',
            462: 'Destination Unreachable',
            551: 'Option not supported'
            }
    reg = re.compile('^(.*): (.*)$')

    @classmethod
    def getParamFromEnum(cls, paramEnum):
        return cls.params[paramEnum]

    def respond(self, code,  seq, session, args=[], kwargs={}):
        """warning: args时mutable的,也就是说只会被初始化一次,默认初始化时请不要修改其值"""
        """rtsp产生respond"""
        statusStr = self.status[code]

        firstLine = '{} {} {}\n'.format(self.rtspVersion, code, statusStr)
        secondLine = 'CSeq {}\n'.format(seq)
        thirdLine = 'Session: {}\n'.format(session)

        message = firstLine + secondLine + thirdLine
        if len(args):
            message = message + '\n'
            for param in args:
                message = message + '{}\n'.format(param)
        elif len(kwargs):
            message = message + '\n'
            for param in kwargs.keys():
                message = message + '{}: {}\n'.format(param, kwargs.get(param))
        print(message)
        message = message.rstrip('\n')
        return message


    def request(self, method, filename, client_port, seq, session, *args, **kwargs):
        """rtsp产生request"""
        methodStr = self.methods[method.value]

        firstLine = '{} {} {}\n'.format(methodStr, filename, self.rtspVersion)
        secondLine = 'CSeq {}\n'.format(seq)
        if method == METHOD.SETUP:
            thirdLine = 'Transport: RTP/UDP; client-port= {}-{}\n'.format(
                client_port, client_port + 1)# 这里一般用横杠区分rtp的port和rtcp的port
        else:
            thirdLine = 'Session: {}\n'.format(session)

        message = firstLine + secondLine + thirdLine
        if method == METHOD.GET_PARAMETER:
            message = message +  '\n'
            for param in args:
                message = message + '{}\n'.format(param)
        elif method == METHOD.SET_PARAMETER:
            message = message +  '\n'
            for param in kwargs.keys():
                message = message + '{}: {}\n'.format(param, kwargs.get(param))

        print(message)
        message = message.rstrip('\n')
        return message

    def getEnum(self, str):
        """从字符串获取其属于类型"""
        num = self.methods.index(str)
        return METHOD(num)

    def getDictParams(self, lines):
        params = {}
        for line in lines:
            try:
                match = self.reg.match(line)
                param, value = match[1], match[2]
                params[param] = value
            except:
                print('Error: Dict format not correct')
        return params

    def getParams(self, lines):
        params = []
        for line in lines:
            params.append(line)
        return params



    def parseReplyNormal(self, data):
        """用于一般reply的parse"""
        lines = str(data).splitlines()
        code = int(lines[0].split(' ')[1])
        if code != 200:
            raise Exception('Error: {}'.format(lines[0]))
        seqNum = int(lines[1].split(' ')[1])
        session = int(lines[2].split(' ')[1])
        return seqNum, session

    def parseReplyGet(self, data):
        """request 为 get时调用这个"""
        lines = str(data).splitlines()
        seqNum, session = self.parseReplyNormal('\n'.join(lines[:3]))

        params = self.getDictParams(lines[4:])

        return seqNum, session, params

    def parseReplySet(self, data):
        """request为 set时调用这个"""
        lines = str(data).splitlines()
        seqNum, session = self.parseReplyNormal('\n'.join(lines[:3]))

        params = self.getParams(lines[4:])

        return seqNum, session, params

    def parseRequest(self, data):
        request = str(data).split('\n')

        firstLine = request[0].split(' ')
        requestType, filename = self.getEnum(firstLine[0]), firstLine[1]
        seq = request[1].split(' ')[1]
        if requestType == METHOD.SETUP:
            rtpPorts = request[2].split(' ')[3].split('-')
            return requestType, filename, seq, rtpPorts, None, None
        else:
            session = request[2].split(' ')[1]

        if requestType == METHOD.GET_PARAMETER:
            params = self.getParams(request[4:])
            return requestType, filename, seq, None, session, params
        elif requestType == METHOD.SET_PARAMETER:
            params = self.getDictParams(request[4:])
            return requestType, filename, seq, None, session, params
        else:
            return requestType, filename, seq, None, session, None

# rtsp = Rtsp()
# # str1 = rtsp.request(METHOD(4), 'a', None, 1, 2, 'length', 'me')
# str2 = rtsp.request(METHOD(5), 'a', None, 1, 2, length=1, me=2)
# str1 = rtsp.respond(455, 1, 2)
# print(str1)
# print(str2)
#
# print(rtsp.getEnum('SETUP'))


