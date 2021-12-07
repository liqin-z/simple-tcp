# data sender

# input format
# tcpclient file address_of_udpl port_number_of_udpl windowsize ack_port_number

import datetime
import struct
import sys
import socket
import random


class TCPPacket:
    # TCP HEADER
    def __init__(self, src_port, dst_port, window):
        self.src_port = src_port                    # 16 bits
        self.dst_port = dst_port                    # 16 bits
        self.seq_num = self.get_start_seq_num()     # 32 bits
        self.ack_num = 0                            # 32 bits
        self.data_offset = 0                        # 4 bits
        self.reserved_field = 0                      # 3 bits
        self.flag_ns = 0                             # 1 bit
        self.flag_cwr = 0                            # 1 bit
        self.flag_ece = 0                            # 1 bit
        self.flag_urg = 0                            # 1 bit
        self.flag_ack = 0                            # 1 bit
        self.flag_psh = 0                            # 1 bit
        self.flag_rst = 0                            # 1 bit
        self.flag_syn = 0                            # 1 bit
        self.flag_fin = 0                             # 1 bit
        self.window = window       # 2 bytes
        self.checksum = 0          # 2 bytes
        self.urgent_pointer = 0    # 2 bytes

    def build(self) -> bytes:
        packet = struct.pack(
            '!HHIIBBHHH',
            self.src_port,  # Source Port
            self.dst_port,  # Destination Port
            0,              # Sequence Number
            0,              # ACK Number
            5 << 4,         # Data Offset
            self.flags,      # Flags
            8192,           # Window
            0,              # Checksum (initial value)
            0               # Urgent pointer
        )

        pseudo_hdr = struct.pack(
            '!4s4sHH',
            socket.inet_aton(self.src_host),    # Source Address
            socket.inet_aton(self.dst_host),    # Destination Address
            socket.IPPROTO_TCP,                 # PTCL
            len(packet)                         # TCP Length
        )

        checksum = chksum(pseudo_hdr + packet)

        packet = packet[:16] + struct.pack('H', checksum) + packet[18:]

        return packet

    @staticmethod
    def get_start_seq_num():
        return random.randint(0, 4294967295)

def packetSender(argv):

    addr_udpl = argv[2]
    port_udpl = argv[3]
    window_size = argv[4] # unit in bytes
    port_ack = argv[5]

    file_name = argv[1]
    file_bytes = readFiles(file_name)

    pkt = TCPPacket(port_ack, port_udpl, window_size)



seq_num = 0
retrans_time = datetime.timedelta(seconds=3) # adjust per TCP standard
seg_size = 576

# read binary data from a file
def readFiles(file_name):
    file_bytes = bytearray()
    try:
        with open(file_name, "rb") as f:
            file_bytes += f.read()
    except IOError:
        print("Did not find the file under correct directory!")
    return file_bytes





def chksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff


if __name__ == "__main__":
    # packetSender(sys.argv)
    dst = '192.168.1.1'
    pak = TCPPacket(
        '192.168.1.42',
        20,
        dst,
        666,
        0b000101001  # Merry Christmas!
    )

    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP

    sock.bind((UDP_IP, UDP_PORT))  # wait for connection

    #
    # s.sendto(pak.build(), (dst, 0))
