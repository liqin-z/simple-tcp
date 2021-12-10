It has features like checksum, timer to support reliable data transfer, 
I have tested on my Macbook with newudpl and it works well under bit error ~= 100, random packet loss rate ~= 50%, 
and out of order rate ~= 99%. 


### High Level Design
- I have defined my TCPPacket Class under ```utils.py```, where I use struct to organize my TCP header, and use ```updateState``` and ```updateFlag``` to set flag for the packet.
- I have defined two ```threading.Thread``` class for sending data packets and receiving ack packets. When the ```tcpclient.py``` start to run, a non-stop ACK thread will be initialized and start receiving all the acks sent from the server. Then the program will read the file that is going to be sent to the server, and divides the file to multiple packets, each 100 bytes. 
Given window size, e.g. 400 bytes, I will have 4 packets in a window sent simultaneously by a dataThread. Everytime one packet is ACKed from server, the window moves forward and reset the timer.
When there is a timeout, every packet inside the window will be resent.
- ```tcpserver.py``` is a single thread always accepting packets from the client, extract the header and data, and choose to store the data to buffer or write to file based on its sequence number. 
- When the last packet is sent, a fin flag will be written to the TCPPacket, and the server and client will then close their socket.  


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

### Handy Tools
```bash
socket.error: [Errno 48] Address already in use
-------------------------------------------------
ps -fA | grep python
kill <pid>
```