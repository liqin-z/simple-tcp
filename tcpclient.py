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
CUR_ACKED_NUM = 0
CACHE_ACK = []
SENT_NOT_ACKED = []  # packet seqs that is not acked
TIMEOUT = timedelta(seconds=10)  # seconds
seq_num = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.bind((sys.argv[2], int(sys.argv[5])))

def sendPacket(argv, data, seq_num, isfin=False):
    global CUR_BYTES_READ
    global CUR_ACKED_NUM
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

    # receive acks from server
    # update largest Acked number
    received_ack_num, server_addr = sock.recvfrom(2048)
    received_ack = int(received_ack_num.decode())
    if received_ack == CUR_ACKED_NUM:
        # missing pkg
        pass
    elif received_ack == CUR_ACKED_NUM + 1:
        CUR_ACKED_NUM += 1
        CUR_BYTES_READ -= MSS  # move window by 1 segment
    elif received_ack > CUR_ACKED_NUM + 1:
        if received_ack not in CACHE_ACK:
            CACHE_ACK.append(received_ack)
    else:
        pass


# send all packets in the given window
def sendPacketInWindow(seq_num, window_size_n, data_packets, chunk_size, threads):
    global SENT_NOT_ACKED
    for seq in range(seq_num, seq_num + window_size_n):
        if seq >= len(data_packets):
            return False  # end of data
        if seq in SENT_NOT_ACKED:
            continue  # still waiting for acks, clear when timeout
        else:
            SENT_NOT_ACKED.append(seq)
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
    global CUR_ACKED_NUM
    global CUR_BYTES_READ
    global SENT_NOT_ACKED
    global WINDOW_SIZE
    global seq_num
    # for test
    chunk_size = 2
    # chunk_size = MSS - 20
    data_packets = []

    def timeoutAction(seq_num, window_size_n, data_packets, chunk_size, threads):
        # reset timer
        t.cancel()
        t = Timer(TIMEOUT, timeoutAction, args=(seq_num, window_size_n, data_packets, chunk_size, threads))
        t.start()

        # update global variables
        for check_seq in range(seq_num, seq_num + window_size_n):
            # check if packets within current window is ACKED
            if check_seq in SENT_NOT_ACKED and \
                    check_seq + 1 > CUR_ACKED_NUM and \
                    check_seq + 1 not in CACHE_ACK:
                # safely resend the checked seq pkt
                SENT_NOT_ACKED.remove(check_seq)  # mark as not send -> send it again

        # resend packets in current window
        sendPacketInWindow(seq_num, window_size_n, data_packets, chunk_size, threads)

    try:
        with open(file_name, mode="rb") as f:
            for data in readChunks(f, chunk_size):
                data_packets.append(data)

            # number of packets in the window
            window_size_n = WINDOW_SIZE // MSS
            threads = []  # one thread for every sent packet

            # while seq_num < len(data_packets):
            # while CUR_ACKED_NUM <= cur_window_end:

            t = Timer(TIMEOUT, timeoutAction, args=[seq_num, window_size_n, data_packets, chunk_size, threads])

            while True:
                t.cancel()
                t.start()
                if not sendPacketInWindow(seq_num, window_size_n, data_packets, chunk_size, threads):
                    break

                while CUR_ACKED_NUM + 1 in CACHE_ACK:
                    t.cancel()
                    t.start()
                    # read ack from cache if out of order
                    CUR_ACKED_NUM += 1
                    seq_num = CUR_ACKED_NUM

                if CUR_ACKED_NUM > seq_num:
                    seq_num = CUR_ACKED_NUM
                    t.cancel()
                    t.start()
                    if not sendPacketInWindow(seq_num, window_size_n, data_packets, chunk_size, threads):
                        break

                # if timedelta(seconds=end_timer - start_timer) > TIMEOUT:
                #     start_timer = timer()
                #     if not sendPacketInWindow(seq_num, window_size_n, data_packets, chunk_size, threads):
                #         break
                # else:
                #     pass

                # immediately resend the unACKed packet
                # if CUR_ACKED_NUM != seq_num:
                #     seq_num = CUR_ACKED_NUM
                # # CUR_BYTES_READ += MSS
                # # while CUR_BYTES_READ > WINDOW_SIZE:
                # #     # wait for acks
                # #     pass
                # # else:
                # data = data_packets[seq_num]
                # if len(data) == chunk_size:
                #     sendPacket(sys.argv, data, seq_num)
                # else:
                #     # end of file, close the socket
                #     sendPacket(sys.argv, data, seq_num, isfin=True)
                # seq_num += 1

    except IOError:
        print("Failed to find the file '{}' under current directory!".format(file_name))
    return


if __name__ == "__main__":
    # print(sys.argv)
    file_name = sys.argv[1]
    readFiles(file_name)
    # sendPacket(sys.argv)
