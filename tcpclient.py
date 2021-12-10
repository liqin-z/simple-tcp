# data sender
# tcpclient file address_of_udpl port_number_of_udpl windowsize ack_port_number

import array
import random
import socket
import struct
import sys
from time import time
from timeit import default_timer as timer
from threading import Thread
from threading import Timer
from datetime import timedelta

from bitarray import bitarray
from bitarray.util import ba2int
from utils import TCPPacket

MSS = 576  # bytes
WINDOW_SIZE = int(sys.argv[4])  # bytes
CUR_BYTES_READ = 0
ACKED_SEQ = 0
CACHE_ACK = set()
SENT_NOT_ACKED_SEQ = []  # packet seqs that is not acked
TIMEOUT = timedelta(seconds=10)  # seconds
window_start = 0
packets = None
window_move_flag = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.bind((sys.argv[2], int(sys.argv[5])))

class DATAThread(Thread):
    def __init__(self, addr, port):
        Thread.__init__(self)
        self.udpl_addr = addr
        self.udpl_port = port

    def run(self):
        global window_start
        global window_move_flag
        global packets
        global sock
        window_n = WINDOW_SIZE // MSS
        for i in range(window_n):
            if i + window_start >= len(packets):
                break
            print("index: ", i+window_start, " sent.")
            sock.sendto(packets[i+window_start], (self.udpl_addr, int(self.udpl_port)))

    def join(self, timeout=0):
        Thread.join(self, timeout)


class ACKThread(Thread):
    def __init__(self, end):
        Thread.__init__(self)
        self.end = end

    def run(self):
        while True:
            global ACKED_SEQ
            global window_start
            global window_move_flag

            received_ack_pkt, server_addr = sock.recvfrom(2048)
            ack_header = received_ack_pkt[:20]
            ack_num = struct.unpack(
                "I",
                ack_header[8:12]
            )[0]

            # print(ack_num)
            if ack_num not in CACHE_ACK:
                CACHE_ACK.add(ack_num)

            if ack_num - 1 >= window_start:
                window_start = ack_num
                window_move_flag = 1

            if window_start >= self.end:
                break

    def join(self, timeout=0):
        Thread.join(self, timeout)

def preparePacket(argv, data, seq_num, isfin=False):
    port_udpl = argv[3]
    port_ack = argv[5]

    packet = TCPPacket(port_ack, port_udpl, WINDOW_SIZE, data)
    if isfin:
        packet.updateFlag(fin=1)
        packet.updateState()

    packet.seq_num = seq_num
    header = packet.buildPacket()
    packet = header + data

    return packet


# read binary data from a file
def readChunks(file, chunk_size):
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield data


def readFiles(file_name):
    global ACKED_SEQ
    global CUR_BYTES_READ
    global SENT_NOT_ACKED_SEQ
    global WINDOW_SIZE
    global window_start
    global window_move_flag
    global packets

    # for test
    chunk_size = 2
    # chunk_size = MSS - 20
    data_packets = []


    try:
        with open(file_name, mode="rb") as f:
            for data in readChunks(f, chunk_size):
                data_packets.append(data)

            packets = [[] for i in range(len(data_packets))]
            for i in range(len(data_packets)):
                if i == len(data_packets) - 1:
                    packets[i] = preparePacket(sys.argv, data_packets[i], i, isfin=True)
                else:
                    packets[i] = preparePacket(sys.argv, data_packets[i], i, isfin=False)

            # number of packets in the window
            window_size_n = WINDOW_SIZE // MSS

            ackThread = ACKThread(len(data_packets))
            ackThread.start()
            t = time()

            while True:
                if window_start >= len(data_packets):
                    break
                if window_start not in CACHE_ACK and window_move_flag:
                    t = time() # reset timer
                    dataThread = DATAThread(sys.argv[2], sys.argv[3])
                    window_move_flag = 0
                    dataThread.start()
                    dataThread.join(10)
                if time() - t > 1:
                    t = time() # reset timer
                    dataThread = DATAThread(sys.argv[2], sys.argv[3])
                    window_move_flag = 0
                    dataThread.start()
                    dataThread.join(10)


    except IOError:
        print("Failed to find the file '{}' under current directory!".format(file_name))
    # ackThread.join()
    return


if __name__ == "__main__":
    # print(sys.argv)
    file_name = sys.argv[1]
    readFiles(file_name)
