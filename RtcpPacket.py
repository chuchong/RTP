import sys
from time import time
RTCP_HEADER = 8
class RRRtcpPacket:
    header = bytearray(RTCP_HEADER)
    # sender_info = bytearray(20)
    report_blocks = bytearray(0)

    def decode(self, data):
        self.header = bytearray(data[0:RTCP_HEADER])
        self.report_blocks = bytearray(data[RTCP_HEADER:])

    def appendReportBlock(self, ssrc, frac_lost, cumu_lost, extseq, jitter, lsr, dlsr):
        """lsr 上次sr timestamp的中间字段"""
        report_block = bytearray(24)
        report_block[0] = ssrc >> 24 & 255
        report_block[1] = ssrc >> 16 & 255
        report_block[2] = ssrc >> 8 & 255
        report_block[3] = ssrc & 255
        report_block[4] = frac_lost
        report_block[5] = cumu_lost >> 16 & 255
        report_block[6] = cumu_lost >> 8 & 255
        report_block[7] = cumu_lost & 255
        report_block[8] = extseq >> 24 & 255
        report_block[9] = extseq >> 16 & 255
        report_block[10] = extseq >> 8 & 255
        report_block[11]  = extseq & 255
        report_block[12] = jitter >> 24 & 255
        report_block[13] = jitter >> 16 & 255
        report_block[14] = jitter >> 8 & 255
        report_block[15]  = jitter & 255
        report_block[16] = lsr >> 24 & 255
        report_block[17] = lsr >> 16 & 255
        report_block[18] = lsr >> 8 & 255
        report_block[19]  = lsr & 255
        report_block[20] = dlsr >> 24 & 255
        report_block[21] = dlsr >> 16 & 255
        report_block[22] = dlsr >> 8 & 255
        report_block[23]  = dlsr & 255
        self.report_blocks += report_block

    def encode(self, version, padding, length, ssrc, pt=201):
        """rc 代表公多少个report block """
        # pt = 201# SE默认为200
        header = bytearray(8)
        rc = len(self.report_blocks) // 24
        header[0] = (version << 6) | (padding << 5) | rc
        header[1] = pt
        header[2] = (length >> 8) & 255
        header[3] = length & 255
        header[4] = ssrc >> 24 & 255
        header[5] = ssrc >> 16 & 255
        header[6] = ssrc >> 8 & 255
        header[7] = ssrc & 255
        self.header = header

    def getInt(self, s: bytearray):
        v = s[0] << 24 | s[1] << 16 | s[2] << 8 | s[3]
        return int(v)

    def version(self):
        return int(self.header[0] >> 6)

    def padding(self):
        return int(self.header[0] >> 5 & 1)

    def rc(self):
        return int(self.header[0] & 31)

    def pt(self):
        return int(self.header[1])

    def length(self):
        return int(self.header[2] << 8 | self.header[3])

    def sender_ssrc(self):
        return int(self.getInt(self.header[4:8]))

    def ssrc(self, i):
        ssrci = self.report_blocks[24 * i: 24 * i + 4]
        v = self.getInt(ssrci)
        return int(v)

    def fracLost(self,i):
        flost = int(self.report_blocks[24 * i + 4])
        return flost

    def cumuLost(self, i):
        clost = self.report_blocks[24 * i + 5] << 16 \
                | self.report_blocks[24 * i + 6] << 8 \
                | self.report_blocks[24 * i + 7]
        return int(clost)

    def extSeq(self, i):
        return int(self.getInt(self.report_blocks[24*i+8:24*i+12]))

    def jitter(self, i):
        return int(self.getInt(self.report_blocks[24*i+12:24*i+16]))

    def lsr(self, i):
        return int(self.getInt(self.report_blocks[24*i+16:24*i+20]))

    def dlsr(self, i):
        return int(self.getInt(self.report_blocks[24*i+20:24*i+24]))

    def getPacket(self):
        return self.header + self.report_blocks

class ByeRtcpPacket(RRRtcpPacket):
    def encode(self, version, padding, length, ssrc, pt=203):
        """rc 代表公多少个report block """
        super().encode(version,padding,length,ssrc, pt)

class SRRtcpPacket(RRRtcpPacket):
    sender_info = bytearray(20)

    def decode(self, data):
        self.header = bytearray(data[0:RTCP_HEADER])
        self.sender_info = bytearray(data[RTCP_HEADER: RTCP_HEADER + 20])
        self.report_blocks = bytearray(data[RTCP_HEADER + 20:])

    def exEncode(self, version, padding, length, ssrc, ntpTimeH, ntpTimeL, rtpTime, pack_cnt, oct_cnt,
                 ):
        super().encode(version, padding,length, ssrc, 200)
        info = bytearray(20)
        info[0] = ntpTimeH >> 24 & 255
        info[1] = ntpTimeH >> 16 & 255
        info[2] = ntpTimeH >> 8 & 255
        info[3] = ntpTimeH >> 0 & 255

        info[4] = ntpTimeL >> 24 & 255
        info[5] = ntpTimeL >> 16 & 255
        info[6] = ntpTimeL >> 8 & 255
        info[7] = ntpTimeL & 255

        info[8] = rtpTime >> 24 & 255
        info[9] = rtpTime >> 16 & 255
        info[10] = rtpTime >> 8 & 255
        info[11] = rtpTime & 255

        info[12] = pack_cnt >> 24 & 255
        info[13] = pack_cnt >> 16 & 255
        info[14] = pack_cnt >> 8 & 255
        info[15] = pack_cnt & 255

        info[16] = oct_cnt >> 24 & 255
        info[17] = oct_cnt >> 16 & 255
        info[18] = oct_cnt >> 8 & 255
        info[19] = oct_cnt & 255

        self.sender_info = info

    def getPacket(self):
        return self.header + self.sender_info + self.report_blocks

    def ntpTime(self):
        sig = self.sender_info[0:4]
        sigN = super().getInt(sig)
        lea = self.sender_info[4:8]
        leaN = super().getInt(lea)
        return int(sigN), int(leaN)

    def rtpTime(self):
        rtime = super().getInt(self.sender_info[8:12])
        return int(rtime)

    def packCnt(self):
        pcnt = super().getInt(self.sender_info[12:16])
        return int(pcnt)

    def octCnt(self):
        ocnt = super().getInt(self.sender_info[16:20])
        return int(ocnt)
