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

### TODOs

- Distinguish sent but not acked
- Wait for ACKs within timeout range


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
