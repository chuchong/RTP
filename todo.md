TODO:

1. ~~reposition~~
2. ~~change of play speed~~
3. report
4. ~~分包~~
   1. 改进client策略
5. ~~full screen~~
6. search video (using http)
7. 实现音频 pydub
8. rtcp
9. 转ts

RTSP

```
RTSP header fields (see Section 18) include general-header, request-
   header, response-header, and message body header fields.

   The order in which header fields with differing field names are
   received is not significant.  However, it is "good practice" to send
   general-header fields first, followed by a request-header or
   response-header field, and ending with the message body header
   fields.

   Multiple header fields with the same field-name MAY be present in a
   message if and only if the entire field-value for that header field
   is defined as a comma-separated list.  It MUST be possible to combine
   the multiple header fields into one "field-name: field-value" pair,
   without changing the semantics of the message, by appending each
   subsequent field-value to the first, each separated by a comma.  The
   order in which header fields with the same field-name are received is
   therefore significant to the interpretation of the combined field
   value; thus, a proxy MUST NOT change the order of these field-values
   when a message is forwarded.
   
   Unknown message headers MUST be ignored (skipping over the header to
   the next protocol element, and not causing an error) by an RTSP
   server or client.  An RTSP proxy MUST forward unknown message
   headers.  Message headers defined outside of this specification that
   are required to be interpreted by the RTSP agent will need to use
   feature tags (Section 4.5) and include them in the appropriate
   Require (Section 18.43) or Proxy-Require (Section 18.37) header.
   
```

RTP for High Quality Pics

 https://tools.ietf.org/html/rfc4175 

```
Line No.: 15 bits

     Scan line number of encapsulated data, in network byte order.
     Successive RTP packets MAY contains parts of the same scan line
     (with an incremented RTP sequence number, but the same timestamp),
     if it is necessary to fragment a line.
     
     Identifies which field the scan line belongs to, for interlaced
     data.  F=0 identifies the first field and F=1 the second field.
     For progressive scan data (e.g., SMPTE 296M format video), F MUST
     always be set to zero.
     
     Continuation (C): 1 bit

     Determines if an additional scan line header follows the current
     scan line header in the RTP packet.  Set to 1 if an additional
     header follows, implying that the RTP packet is carrying data for
     more than one scan line.  Set to 0 otherwise.  Several scan lines
     MAY be included in a single packet, up to the path MTU limit.  The
     only way to determine the number of scan lines included per packet
     is to parse the payload headers.
     
     The initial value of the timestamp SHOULD be random
     
     The offset has a value of zero if
     the first sample in the payload corresponds to the start of the
     line, and increments by one for each pixel.

```

