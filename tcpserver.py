# data receiver
# tcpserver file listening_port address_for_acks port_for_acks

import sys
import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def packetReciver(argv):
    file_name = argv[1]
    port_lstn = argv[2]
    addr_ack = argv[3]
    port_ack = argv[4]

# receive data from listening port


# write data to a file


# send ACK to addr_ack, port_ack


if __name__ == "__main__":
    packetReciver(sys.argv)