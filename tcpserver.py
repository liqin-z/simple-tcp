# data receiver
# tcpserver file listening_port address_for_acks port_for_acks
import struct
import sys
import array
import socket
from utils import TCPPacket


def myCheckSum(packet):
    print(packet)
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

        # unpack header -> tuples
        # check sequence number
        # TODO
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
        computed_checksum = myCheckSum(pkt_deep_copy)
        stored_checksum = struct.unpack(
            "H",
            tcp_header[16:18]
        )

        if computed_checksum == stored_checksum[0]:
            # print("Checksum passed!")
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