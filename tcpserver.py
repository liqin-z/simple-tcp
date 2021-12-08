# data receiver
# tcpserver file listening_port address_for_acks port_for_acks

import sys
import socket

def receivePacket(argv):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)

    out_file_name = argv[1]
    port_listen = argv[2]
    addr_ack = argv[3]
    port_ack = argv[4]

    # receive data from listening port
    sock.bind((addr_ack, int(port_listen)))
    while True:
        filebytes, addr_udpl = sock.recvfrom(2048)
        # ack_to_send = ""
        data = filebytes[20:]
        print(data)

        # write data to a file
        with open('./'+out_file_name, 'wb+') as f:
            f.write(data)
            break

        # send ACK to addr_ack, port_ack


if __name__ == "__main__":
    # print(sys.argv)
    receivePacket(sys.argv)