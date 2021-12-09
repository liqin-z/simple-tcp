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

def sendPacket(argv, data):
    # test
    # print(data)
    addr_udpl = argv[2]    # dest_address
    port_udpl = argv[3]    # dest_port
    window_size = argv[4]
    port_ack = argv[5]

    packet = TCPPacket(port_ack, port_udpl, window_size, data)
    header = packet.buildPacket()
    packet = header + data

    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)  # UDP

    sock.bind((addr_udpl, int(port_ack)))
    sock.sendto(packet, (addr_udpl, int(port_udpl)))

# retransmission_time = datetime.timedelta(seconds=3) # adjust per TCP standard


# read binary data from a file
def readChunks(file, chunk_size):
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield data

def readFiles(file_name):
    # for test
    # chunk_size = 2
    chunk_size = MSS - 20
    try:
        with open(file_name, "rb") as f:
            for data in readChunks(f, chunk_size):
                sendPacket(sys.argv, data)
    except IOError:
        print("Failed to find the file '{}' under current directory!".format(file_name))
    return


if __name__ == "__main__":
    print(sys.argv)
    file_name = sys.argv[1]
    readFiles(file_name)
    # sendPacket(sys.argv)