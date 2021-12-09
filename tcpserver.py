# data receiver
# tcpserver file listening_port address_for_acks port_for_acks

import struct
import sys
import array
import socket
from utils import TCPPacket
from utils import checkSum

CUR_ACKED_NUM = 0


def receivePacket(argv):
    global CUR_ACKED_NUM
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)

    out_file_name = argv[1]
    port_listen = argv[2]
    ack_addr = argv[3]
    ack_port = int(argv[4])

    # receive packet from listening port
    sock.bind((ack_addr, int(port_listen)))
    while True:
        received_packet, udpl_addr = sock.recvfrom(2048)
        tcp_header = received_packet[:20]

        # unpack header -> tuples
        # check sequence number
        seq_num = struct.unpack(
            "I",
            tcp_header[4:8]
        )[0]

        # compute checksum to verify correctness
        # change to bytearray because byte is immutable
        # set chksum field to 0 to perform checksum to validate
        pkt_deep_copy = bytearray(received_packet[:])
        pkt_deep_copy[16:18] = struct.pack(
            "H",
            0
        )
        computed_checksum = checkSum(pkt_deep_copy)
        # print("c:", computed_checksum)

        stored_checksum = struct.unpack(
            "H",
            tcp_header[16:18]
        )[0]
        # print("s:", stored_checksum)

        if computed_checksum == stored_checksum:
            # print("Checksum passed!")
            data = received_packet[20:]

            # write data to a file
            with open('./' + out_file_name, 'wb+') as f:
                f.write(data)

            # send ACK to addr_ack, port_ack
            sock.sendto(str(seq_num + 1).encode(), (ack_addr, ack_port))
            CUR_ACKED_NUM = seq_num + 1
        else:
            # the pkt is corrupted
            # immediately send previous ACKed num
            sock.sendto(str(CUR_ACKED_NUM).encode(), (ack_addr, ack_port))

        flags = struct.unpack(
            "H",
            tcp_header[12:14]
        )[0]

        bin_flags = bin(flags).replace("0b", "")
        while len(bin_flags) < 16:
            bin_flags = "0" + bin_flags

        flag_ack = bin_flags[-5]
        flag_rst = bin_flags[-3]
        flag_syn = bin_flags[-2]
        # above are not used for functionality
        flag_fin = bin_flags[-1]

        if flag_fin:
            break

    sock.close()


if __name__ == "__main__":
    # print(sys.argv)
    receivePacket(sys.argv)
