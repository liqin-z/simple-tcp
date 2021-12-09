## simple-tcp-over-udp


### Usage
1. Start newudpl to listen from 8080, and send to 8081
```
./newudpl -vv -i 'localhost':8080 -o '127.0.0.1':8081
```

2. Start receiver(server) to bind 8081, and send ack to 8080
```
python tcpserver.py outfile 8081 localhost 8080
```

3. Start sender(client) to bind 8080, and send to 41192
```
python tcpclient.py infile localhost 41192 50 8080
```


### Program Design
There are several important decisions made during the implementation.

Starting from the global variables.
```
MSS                         # Maximum segment size 
WINDOW_SIZE                 # Window size 
CUR_BYTES_READ              # not used 
CUR_ACKED_SEQ               # record the maximum of received continuous sequence number
CACHE_ACK_SEQ               # record all the seq that is acked
SENT_NOT_ACKED              # packet seq_num that is sent but not acked, 
                            # the seq_num of current window will be cleared if timeout 
TIMEOUT                     # resend all packets under current window after this time threshold
```



### TODOs

- Distinguish sent but not acked
- Wait for ACKs within timeout range
- Timeout action -> clean all sent not acked
- ACK sender thread


### About newudpl
http://www.cs.columbia.edu/~hgs/research/projects/newudpl/newudpl-1.4/newudpl.html

### Common error
```bash
# Solving conflict port 
socket.error: [Errno 48] Address already in use
-------------------------------------------------
ps -fA | grep python
kill <pid>
```
