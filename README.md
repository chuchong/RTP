# RTP
THUSS-computer networking final work--rtp.
it's similar to final work of [nyu](http://www.nyu.edu/classes/jcf/CSCI-GA.2262-001/handouts/FinalProject-Spring2016.pdf),
but rather more complicated.
# environment
```
language: python3
packages: opencv + pyqt5
```
# run
```
python Server.py
python ClientLauncher.py
```
# feature
1. using opencv to capture jpg from a mp4 video
2. using RTP to send raw jpg data stream from server to client
3. client controls server by RTSP: SETUP PLAY PAUSE TAERDOWN GET_PARAMETER SET_PARAMETER
4. RTCP packetization has been implemented, if frac_lost > 50/255, then the server will decrease video quality and prolong sleep time between two packets
5. you can show video in full-screen mode, can buffer-load video, can set video quality, can reposition, can change speed of video in client
# implementation
1. GET_PARAMETER SET_PARAMETER in RTSP to ge/set fps/total frame etc
2. 3 threads in client to play video stream, one to receive udp packets, one to unpack rtp from udp, one to paint. The data is delivered by queue 
3. full-screen is another top widget, client/full-screen widget/serer all contain a DFA to determine its behavior.
# to the lower class
wish you guys survive junior year in THUSS :)
