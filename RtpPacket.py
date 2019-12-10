import sys
from time import time
HEADER_SIZE = 12
UNCOMPRESSED_HEADER = 26
class RtpPacket:    
    header = bytearray(HEADER_SIZE)
    
    def __init__(self):
        pass
        
    def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
        """Encode the RTP packet with header fields and payload."""
        timestamp = int(time())
        header = bytearray(HEADER_SIZE)
        
        # Fill the header bytearray with RTP header fields
        header[0] = (version << 6) | (padding << 5) | (extension << 4) | cc
        header[1] = (marker << 7) | pt
        header[2] = (seqnum >> 8) & 255 #upper bits
        header[3] = seqnum & 255
        header[4] = timestamp >> 24 & 255
        header[5] = timestamp >> 16 & 255
        header[6] = timestamp >> 8 & 255
        header[7] = timestamp & 255
        header[8] = ssrc >> 24 & 255
        header[9] = ssrc >> 16 & 255
        header[10] = ssrc >> 8 & 255
        header[11] = ssrc & 255
        
        self.header = header
        
        # Get the payload from the argument
        self.payload = payload
        
    def decode(self, byteStream):
        """Decode the RTP packet."""
        self.header = bytearray(byteStream[:HEADER_SIZE])
        self.payload = byteStream[HEADER_SIZE:]
    
    def version(self):
        """Return RTP version."""
        return int(self.header[0] >> 6)

    def seqNum(self):
        """Return sequence (frame) number."""
        seqNum = self.header[2] << 8 | self.header[3]
        return int(seqNum)
    
    def timestamp(self):
        """Return timestamp."""
        timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
        return int(timestamp)
    
    def payloadType(self):
        """Return payload type."""
        pt = self.header[1] & 127
        return int(pt)
    
    def getPayload(self):
        """Return payload."""
        return self.payload
        
    def getPacket(self):
        """Return RTP packet."""
        return self.header + self.payload


class UncompressedRtp(RtpPacket):
    """uncompressed video rtp"""
    """https://tools.ietf.org/html/rfc4175"""
    extendedHeader = bytearray(UNCOMPRESSED_HEADER)

    def __init__(self):
        super(UncompressedRtp, self).__init__()
        self.pattern = bytearray(6)
    def extendedEncode(self, version, padding, extension, cc,
               seqnum, marker, pt, ssrc, payload,
               extendedSeq, length, field, lineNo,
               cont, offset):
        self.encode(version, padding, extension, cc,
               seqnum, marker, pt, ssrc, payload)
        self.extendedHeader[:HEADER_SIZE ] = self.header[:]
        self.extendedHeader[12] = (extendedSeq >> 8) & 255 #upper bits
        self.extendedHeader[13] = (extendedSeq & 255)
        self.pattern[0] = (length >> 8) & 255
        self.pattern[1] = length & 255
        self.pattern[2] = (field << 7) | (lineNo >> 8) & 255
        self.pattern[3] = lineNo & 255
        self.pattern[4] = (cont << 7) | (offset >> 8) & 255
        self.pattern[5] = offset & 255
        self.extendedHeader[14: 20] = self.pattern[:]
        self.extendedHeader[20: 26] = self.pattern[:]

        self.payload = payload

    def extendedSeq(self):
         exseq = self.extendedHeader[12] << 8 | self.extendedHeader [13]
         return int(exseq)

    def length(self):
        length = self.extendedHeader[14] << 8 | self.extendedHeader[15]
        return int(length)

    def field(self):
        return int(self.extendedHeader[16] >> 7)

    def lineNo(self):
        lineNo = self.extendedHeader[16] << 8 | self.extendedHeader[17]
        return int(lineNo)

    def continuation(self):
        return int(self.extendedHeader[18] >> 7)

    def offset(self):
        offset = self.extendedHeader[18] <<8 | self.extendedHeader[19]
        return int(offset)


    def checkValid(self):
        for i, j in (self.extendedHeader[14:20], self.extendedHeader[20: 26]):
            if int(i) != int(j):
                return False
            return True
