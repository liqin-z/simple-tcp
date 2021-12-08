## simple-tcp-over-udp


### Usage
Start newudpl to listen from 8080, and send to 8081
```
./newudpl -vv -i 'localhost':8080 -o '127.0.0.1':8081
```

Start receiver(server) to bind 8081, and send ack to 8080
```
python tcpserver.py outfile 8081 localhost 8080
```

Start sender(client) to bind 8080, and send to 41192
```
python tcpclient.py infile localhost 41192 50 8080
```


### Learn more about newudpl
http://www.cs.columbia.edu/~hgs/research/projects/newudpl/newudpl-1.4/newudpl.html