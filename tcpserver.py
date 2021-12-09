# data receiver
# tcpserver file listening_port address_for_acks port_for_acks

import struct
import sys
import array
import socket
from utils import TCPPacket
from utils import checkSum
from collections import OrderedDict

BUFFER = OrderedDict() # this should be exactly the same as data_packets in sender
CUR_ACKED_NUM = 0
EXPECTED_SEQ = 0

def updateExpectedSeq(seq):
    global CUR_ACKED_NUM
    res = seq + 1
    while res in BUFFER:
        res += 1
    CUR_ACKED_NUM = res
    return res

def receivePacket(argv):
    global CUR_ACKED_NUM
    global EXPECTED_SEQ
    global BUFFER

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

        # get packet sequence number
        seq_num = struct.unpack(
            "I",
            tcp_header[4:8]
        )[0]

        # compute checksum to verify correctness
        # set chksum field to 0 to perform checksum to validate
        pkt_deep_copy = bytearray(received_packet[:])
        pkt_deep_copy[16:18] = struct.pack(
            "H",
            0
        )
        computed_checksum = checkSum(pkt_deep_copy)
        stored_checksum = struct.unpack(
            "H",
            tcp_header[16:18]
        )[0]

        # prepare an ack tcp-pkt to send
        ack_packet = TCPPacket(port_listen, ack_port, 0, bytes(0))

        # checksum passed, store data
        if computed_checksum == stored_checksum:
            data = received_packet[20:]

            # write data to memory
            if seq_num not in BUFFER:
                BUFFER[seq_num] = data

            # seq is expected, then write data to a file
            if seq_num == EXPECTED_SEQ:
                EXPECTED_SEQ = updateExpectedSeq(seq_num)
                for i in range(seq_num, EXPECTED_SEQ):
                    with open('./' + out_file_name, 'ab') as f:
                        f.write(BUFFER[i])

            # send ACK to addr_ack, port_ack
            ack_packet.ack_num = CUR_ACKED_NUM
            ack_packet.updateFlag(ack=1)

            # get flags
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
            # above are not used for functionality in PA2
            flag_fin = bin_flags[-1]

            if flag_fin:
                # end connection
                ack_packet.updateFlag(fin=1)
                ack_packet.updateState()
                sock.sendto(ack_packet.buildPacket(), (ack_addr, ack_port))
                break
            else:
                ack_packet.updateState()
                sock.sendto(ack_packet.buildPacket(), (ack_addr, ack_port))
        else:
            # corrupted, send previous ACKed num
            ack_packet.ack_num = CUR_ACKED_NUM
            ack_packet.updateFlag(ack=1)
            ack_packet.updateState()
            sock.sendto(ack_packet.buildPacket(), (ack_addr, ack_port))

    sock.close()


if __name__ == "__main__":
    # print(sys.argv)
    receivePacket(sys.argv)
