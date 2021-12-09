# data sender
# tcpclient file address_of_udpl port_number_of_udpl windowsize ack_port_number

import array
import random
import socket
import struct
import sys
import time
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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.bind((sys.argv[2], int(sys.argv[5])))


class ACKThread(Thread):
    def __init__(self, end):
        Thread.__init__(self)
        self.end = end
        print("ACK Thread is listening!")

    def run(self):
        while True:
            global ACKED_SEQ
            global window_start

            received_ack_pkt, server_addr = sock.recvfrom(2048)
            ack_header = received_ack_pkt[:20]
            ack_num = struct.unpack(
                "I",
                ack_header[8:12]
            )[0]

            print(ack_num)
            if ack_num not in CACHE_ACK:
                CACHE_ACK.add(ack_num)
            if ack_num == ACKED_SEQ + 1:
                ACKED_SEQ = ack_num

            # ack_num is 4, ACKED_SEQ is 3,
            # CACHE has [4,5,6,7] -> ACKED_SEQ becomes 6
            while ACKED_SEQ + 1 in CACHE_ACK:
                ACKED_SEQ += 1
            ACKED_SEQ -= 1
            window_start = ACKED_SEQ + 1

            if ACKED_SEQ >= self.end:
                break

    def join(self):
        Thread.join(self)


def sendPacket(argv, data, seq_num, isfin=False):
    global CUR_BYTES_READ
    global ACKED_SEQ
    global CACHE_ACK
    global sock
    # test
    # print(data)
    addr_udpl = argv[2]  # dest_address
    port_udpl = argv[3]  # dest_port
    port_ack = argv[5]

    packet = TCPPacket(port_ack, port_udpl, WINDOW_SIZE, data)
    if CUR_BYTES_READ == MSS and packet.flag_syn == 0:
        # The first packet, I'm not implementing syn functionality here
        packet.updateFlag(syn=1)
        packet.updateState()
    if isfin:
        packet.updateFlag(fin=1)
        packet.updateState()

    packet.seq_num = seq_num

    header = packet.buildPacket()
    packet = header + data

    sock.sendto(packet, (addr_udpl, int(port_udpl)))

# send all packets in the given window
def sendPacketInWindow(window_start, window_size_n, data_packets, chunk_size, threads):
    global SENT_NOT_ACKED_SEQ
    for seq in range(window_start, window_start + window_size_n):
        if seq >= len(data_packets):
            return False  # end of data
        if seq in SENT_NOT_ACKED_SEQ:
            continue  # still waiting for acks, clear when timeout
        else:
            SENT_NOT_ACKED_SEQ.append(seq)
        data = data_packets[seq]
        if len(data) == chunk_size:
            threads.append(
                Thread(target=sendPacket, args=(sys.argv, data, seq)))
        else:
            # end of file, close the socket
            threads.append(
                Thread(target=sendPacket, args=(sys.argv, data, seq, True)))
        threads[-1].start()

    for t in threads:
        t.join()
    return True


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
    # for test
    chunk_size = 2
    # chunk_size = MSS - 20
    data_packets = []

    def timeoutAction(window_start, window_size_n, data_packets, chunk_size, threads):
        # reset timer
        t.cancel()
        t = Timer(TIMEOUT, timeoutAction, args=(window_start, window_size_n, data_packets, chunk_size, threads))
        t.start()

        # update global variables
        for check_seq in range(window_start, window_start + window_size_n):
            # check if packets within current window is ACKED
            if check_seq in SENT_NOT_ACKED_SEQ and \
                    check_seq + 1 not in CACHE_ACK:
                # and check_seq + 1 > ACKED_SEQ \
                # resend the checked seq pkt if not in cache
                SENT_NOT_ACKED_SEQ.remove(check_seq)  # mark as not send -> send it again

        # resend packets in current window
        sendPacketInWindow(window_start, window_size_n, data_packets, chunk_size, threads)

    try:
        with open(file_name, mode="rb") as f:
            for data in readChunks(f, chunk_size):
                data_packets.append(data)

            ackThread = ACKThread(len(data_packets))
            ackThread.start()

            # number of packets in the window
            window_size_n = WINDOW_SIZE // MSS
            threads = []  # one thread for every sent packet

            # while window_start < len(data_packets):
            # while ACKED_SEQ <= cur_window_end:

            t = Timer(TIMEOUT, timeoutAction, args=[window_start, window_size_n, data_packets, chunk_size, threads])

            while True:
                t.start()
                if not sendPacketInWindow(window_start, window_size_n, data_packets, chunk_size, threads):
                    break

                while ACKED_SEQ + 1 in CACHE_ACK:
                    t.cancel()
                    t.start()
                    # read ack from cache if out of order
                    ACKED_SEQ += 1
                    window_start = ACKED_SEQ

                if ACKED_SEQ > window_start:
                    window_start = ACKED_SEQ
                    t.cancel()
                    t.start()
                    if not sendPacketInWindow(window_start, window_size_n, data_packets, chunk_size, threads):
                        break

    except IOError:
        print("Failed to find the file '{}' under current directory!".format(file_name))
    return


if __name__ == "__main__":
    # print(sys.argv)
    file_name = sys.argv[1]
    readFiles(file_name)
    # sendPacket(sys.argv)
