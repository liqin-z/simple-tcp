## simple-tcp-over-udp

This is my implementation of TCP based on a UDP socket.

It has features like checksum, timer to support reliable data transfer, 
I have tested on my Macbook with newudpl and it works well under bit error ~= 100, random packet loss rate ~= 50%, 
and out of order rate ~= 99%. 


### High Level Design
- I have defined my TCPPacket Class under ```utils.py```, where I use struct to organize my TCP header, and use ```updateState``` and ```updateFlag``` to set flag for the packet.
- I have defined two ```threading.Thread``` class for sending data packets and receiving ack packets. When the client starts, a non-stop ACK thread will be initialized and start receiving all the acks sent from the server. Then the program will read the file that is going to be sent to the server, and divides the file to multiple packets, each 100 bytes. 
Given window size, e.g. 400 bytes, I will have 4 packets in a window sent simultaneously by a dataThread. Everytime one packet is ACKed from server, the window moves forward and reset the timer.
When there is a timeout, every packet inside the window will be resent.
- When the last packet is sent, a fin flag will be written to the TCPPacket, and the server and client will then close their socket. Since there is no implementation of 4-way handshake, the flying packets may be discard and cause data incompleteness. 


### Usage
1. Start newudpl to listen from 8080, and send to 8081
```
./newudpl -vv -i 'localhost':8080 -o '127.0.0.1':8081 -O99 -B100 -L50
```

2. Start receiver(server) to bind 8081, and send ack to 8080
```
python tcpserver.py outfile 8081 localhost 8080
```

3. Start sender(client) to bind 8080, and send to 41192
```
python tcpclient.py infile localhost 41192 400 8080
```


### Low Level Specification
There are several important decisions made during the implementation.

Starting from the global variables.
```
MSS                         # Maximum segment size 
WINDOW_SIZE                 # Window size 
CUR_BYTES_READ              # not used 
ACKED_SEQ                   # record the maximum of received continuous sequence number
CACHE_ACK                   # record all the acks
TIMEOUT                     # resend all packets under current window after this time threshold
```



### About newudpl
http://www.cs.columbia.edu/~hgs/research/projects/newudpl/newudpl-1.4/newudpl.html

### Handy Tools
```bash
socket.error: [Errno 48] Address already in use
-------------------------------------------------
ps -fA | grep python
kill <pid>
```
