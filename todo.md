TODO:

1. reposition
2. change of play speed
3. report
4. full screen
5. search video (using http)
6. 实现音频 pydub
7. 分包
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