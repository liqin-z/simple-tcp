## simple-tcp-over-udp

This is my implementation of TCP based on a UDP socket.

```
.
├── tcpclient.py            # data sender
├── tcpserver.py            # data receiver
├── utils.py                # define the TCPPacket Class 
├── infile                  # file used to read data from
└── outfile                 # file used to save transmitted data
```

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

### Known Bugs
Since there is no implementation of 4-way handshake, after receiver get the fin flag in the last packet, the socket will be immediately closed, and the flying packets may be discarded and cause data incompleteness.

### Features
- Handle out of ordered packets using buffer at the receiver side.
- Discard corrupted packets using checksum to validate the transmitted packets.
- Timer on client side, resend all packets in current window if timeout.
- All flag bit is usable, update packet state by setting flag values.

### About newudpl
http://www.cs.columbia.edu/~hgs/research/projects/newudpl/newudpl-1.4/newudpl.html

---

Check more design details in ```Design.md```