## 用于进行rtsp通讯,采用rtso/1.0
import enum

@enum.unique
class METHOD(enum.Enum):
    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3
    GET_PARAMETER = 4
    SET_PARAMETER = 5


class Rtsp:
    methods = ('SETUP', 'PLAY', 'PAUSE',
               'TEARDOWN', 'GET_PARAMETER', 'SET_PARAMETER')
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


    def respond(self, code,  seq, session, *args, **kwargs):

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

        return message


    def request(self, method, filename, client_port, seq, session, *args, **kwargs):

        methodStr = self.methods[method.value]

        firstLine = '{} {} {}\n'.format(methodStr, filename, self.rtspVersion)
        secondLine = 'CSeq {}\n'.format(seq)
        if method == METHOD.SETUP:
            thirdLine = 'Transport: RTP/UDP; client-port= {}\n'.format(client_port)
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

        return message


rtsp = Rtsp()
# str1 = rtsp.request(METHOD(4), 'a', None, 1, 2, 'length', 'me')
str2 = rtsp.request(METHOD(5), 'a', None, 1, 2, length=1, me=2)
str1 = rtsp.respond(200, 1, 2)
print(str1)
print(str2)




