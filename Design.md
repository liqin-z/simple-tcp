## Design Details

I have tested this design on my Macbook Pro with newudpl and it works well under bit error ~= 100, random packet loss rate ~= 50%, 
and out of order rate ~= 99%. 


### Overall Design
- I have defined my TCPPacket Class under ```utils.py```, where I use ```struct.pack``` to organize my TCP header, and use ```updateState``` and ```updateFlag``` to set flag for the packet.
I also leave the checksum function there so that the packet can use it to calculate the checksum.
- I have defined two ```threading.Thread``` class for sending data packets and receiving ack packets. When the ```tcpclient.py``` start to run, a non-stop ACK thread will be initialized and start receiving all the acks sent from the server. Then the program will read the file that is going to be sent to the server, and divides the file to multiple packets, each 100 bytes. 
Given window size, e.g. 400 bytes, I will have 4 packets in a window sent simultaneously by a dataThread. Everytime one packet is ACKed from server, the window moves forward and reset the timer.
When there is a timeout, every packet inside the window will be resent.
- ```tcpserver.py``` is a single thread always accepting packets from the client, extract the header and data, and choose to store the data to buffer or write to file based on its sequence number. 
- When the last packet is sent, a fin flag will be written to the TCPPacket, and the server and client will then close their socket.
We then can open the outfile and check its content compared to infile.


### How it Works
There are several important decisions made during the implementation.

Starting from the global variables.

```
PACKET_SIZE                 # Specify exactly the size of one TCP Packet
WINDOW_SIZE                 # Window size (Unit in bytes)
ACKED_SEQ                   # Maximum of received continuous sequence number
CACHE_ACK                   # All received acks
TIMEOUT                     # Resend all packets under current window after this time threshold
window_start                # Starting seq of the current window
packets                     # Store all the packets to be sent
window_move_flag            # A flag indicates weather current window has moved
```
These global variables are useful given that the program runs under a multithread environment, there should always be two threads running, one for receiving acks and the other for sending data.
Here we use ```ACKED_SEQ``` and ```CACHE_ACK``` to make sure the accumulative acks and the later acks will be correctly recorded, and I constantly update ```window_start``` to make sure current window is 
what program needs to send the packets. The ```window_move_flag``` is used to reset timer, send new packets when the window has moved. By constantly updating those global variables, the program can communicate between threads, and also between client and server.


### Design Tradeoffs
There are some poor design decisions have been made and can be improved further.
1. I first read all the file to the memory and then build TCPpackets to send. This is very time consuming when the file becomes very large. A feasible way of doing that is to only build TCP packets for the current window,
such that the program won't need to wait until all the data is read into memory and built into TCP packets, which makes it more efficient.
2. When the window move, I resend all the packets in that window, which will cause those sent not acked packets to be resent. I can definitely use a global variable to record the state of those sent packets, so thant there is no need to resend them.
Only when timeout happens, I should resend those packets.
### Handy Tools
```bash
socket.error: [Errno 48] Address already in use
-------------------------------------------------
ps -fA | grep python
kill <pid>
```