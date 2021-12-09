# data sender

# input format
# tcpclient file address_of_udpl port_number_of_udpl windowsize ack_port_number

import array
import random
import socket
import struct
import sys

from bitarray import bitarray
from bitarray.util import ba2int
from utils import TCPPacket

MSS = 576 # bytes
WINDOW_SIZE = int(sys.argv[4]) # bytes
CUR_BYTES_READ = 0
CUR_ACKED_NUM = 0
TIMEOUT = 3 # seconds

def sendPacket(argv, data, isfin=False):
    global CUR_BYTES_READ
    # test
    # print(data)
    addr_udpl = argv[2]    # dest_address
    port_udpl = argv[3]    # dest_port
    port_ack = argv[5]

    packet = TCPPacket(port_ack, port_udpl, WINDOW_SIZE, data)
    if CUR_BYTES_READ == MSS and packet.flag_syn == 0:
        # The first packet, I'm not implementing syn functionality here
        packet.updateFlag(syn=1)
        packet.updateState()
    if isfin:
        packet.updateFlag(fin=1)
        packet.updateState()

    header = packet.buildPacket()
    packet = header + data

    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)  # UDP

    sock.bind((addr_udpl, int(port_ack)))
    sock.sendto(packet, (addr_udpl, int(port_udpl)))


    # receive acks from server
    print("can i receive after i send?")
    received_ack_num, server_addr = sock.recvfrom(2048)
    print(received_ack_num.decode())
    print(server_addr)


# retransmission_time = datetime.timedelta(seconds=3) # adjust per TCP standard


# read binary data from a file
def readChunks(file, chunk_size):
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield data


def readFiles(file_name):
    global CUR_BYTES_READ
    global WINDOW_SIZE
    # for test
    # chunk_size = 2
    chunk_size = MSS - 20
    try:
        with open(file_name, mode="rb") as f:
            for data in readChunks(f, chunk_size):
                CUR_BYTES_READ += MSS
                while CUR_BYTES_READ > WINDOW_SIZE:
                    # wait for acks
                    pass
                else:
                    if len(data) == chunk_size:
                        sendPacket(sys.argv, data)
                    else:
                        # end of file, close the socket
                        sendPacket(sys.argv, data, isfin=True)

    except IOError:
        print("Failed to find the file '{}' under current directory!".format(file_name))
    return


if __name__ == "__main__":
    print(sys.argv)
    file_name = sys.argv[1]
    readFiles(file_name)
    # sendPacket(sys.argv)