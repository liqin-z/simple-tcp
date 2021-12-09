# data receiver
# tcpserver file listening_port address_for_acks port_for_acks
import struct
import sys
import array
import socket
from utils import TCPPacket


def checkSum(packet):
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff

def receivePacket(argv):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)

    out_file_name = argv[1]
    port_listen = argv[2]
    ack_addr = argv[3]
    ack_port = argv[4]

    # receive packet from listening port
    sock.bind((ack_addr, int(port_listen)))
    while True:
        received_packet, udpl_addr = sock.recvfrom(2048)
        tcp_header = received_packet[:20]
        print(tcp_header)

        # unpack header
        # check sequence number
        seq_num = struct.unpack(
            "I",
            tcp_header[4:8]
        )
        print("first packet seq should be 0")
        print(seq_num)

        # compute checksum to verify correctness
        computed_checksum = checkSum(received_packet)
        print("computed checksum:", computed_checksum)
        stored_checksum = struct.unpack(
            "H",
            tcp_header[16:18]
        )
        print("stored checksum:", stored_checksum)

        if computed_checksum == stored_checksum:
            print("Checksum is passed")
            # checksum check pass
            data = received_packet[20:]
            print(data)

            # write data to a file
            with open('./'+out_file_name, 'wb+') as f:
                f.write(data)

            # send ACK to addr_ack, port_ack


        else:
            # the pkt is corrupted
            # immediately send previous ACKed num
            pass




if __name__ == "__main__":
    # print(sys.argv)
    receivePacket(sys.argv)