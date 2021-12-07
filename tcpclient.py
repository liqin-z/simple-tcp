# data sender

# input format
# tcpclient file address_of_udpl port_number_of_udpl windowsize ack_port_number

import datetime
import struct
import sys
import socket
import random
import array

class TCPPacket:
    # TCP SEGMENT STRUCTURE
    def __init__(self, src_port, dst_port, window_size, data):
        self.src_port = src_port                    # 16 bits
        self.dst_port = dst_port                    # 16 bits
        self.seq_num = self.get_start_seq_num()     # 32 bits
        self.ack_num = 0                            # 32 bits
        self.data_offset = 0                        # 4 bits
        self.reserved_field = 0                      # 3 bits
        self.flag_ns = 0                             # 1 bit - ignore
        self.flag_cwr = 0                            # 1 bit - ignore
        self.flag_ece = 0                            # 1 bit - ignore
        self.flag_urg = 0                            # 1 bit - ignore
        self.flag_ack = 0                            # 1 bit
        self.flag_psh = 0                            # 1 bit - ignore
        self.flag_rst = 0                            # 1 bit - ignore
        self.flag_syn = 0                            # 1 bit
        self.flag_fin = 0                             # 1 bit
        self.window_size = window_size              # 16 bits
        self.checksum = 0                           # 16 bits
        self.urg_pointer = 0                        # 16 bits
        self.data = data

    def build(self) -> bytes:

        flags = struct.pack(
            '!BBBBBBBBB',
            self.flag_ns,
            self.flag_cwr,
            self.flag_ece,
            self.flag_urg,
            self.flag_ack,
            self.flag_psh,
            self.flag_rst,
            self.flag_syn,
            self.flag_fin
        )

        print(int(self.src_port))
        print(int(self.dst_port))

        packet = struct.pack(
            # '!HHIIBHHH',
            'HH',
            int(self.src_port),      # Source Port
            int(self.dst_port),      # Destination Port
            # self.seq_num,       # Sequence Number
            # self.ack_num,       # ACK Number
            # self.data_offset,   # Data Offset
            # flags,               # Flags
            # self.window_size,   # Window
            # self.checksum,      # Checksum (init)
            # self.urg_pointer    # Urgent pointer
        )

        # pseudo_hdr = struct.pack(
        #     '!4s4sHH',
        #     socket.inet_aton(self.src_host),    # Source Address
        #     socket.inet_aton(self.dst_host),    # Destination Address
        #     socket.IPPROTO_TCP,                 # PTCL
        #     len(packet)                         # TCP Length
        # )

        # checksum = chksum(pseudo_hdr + packet)

        # packet = packet[:16] + struct.pack('H', checksum) + packet[18:]

        # return struct.unpack('!BBBBBBBBB',pack)
        return struct.unpack('HH',packet)


    @staticmethod
    def get_start_seq_num():
        return random.randint(0, 4294967295)

    # Computed over TCP header and data
    def chksum(packet) -> int:
        if len(packet) % 2 != 0:
            packet += b'\0'

        res = sum(array.array("H", packet))
        res = (res >> 16) + (res & 0xffff)
        res += res >> 16

        return (~res) & 0xffff


def packetSender(argv):
    file_name = argv[1]
    file_bytes = readFiles(file_name)

    addr_udpl = argv[2]    # dest_address
    port_udpl = argv[3]    # dest_port
    window_size = argv[4]
    port_ack = argv[5]

    pkt = TCPPacket(port_ack, port_udpl, window_size, file_bytes)
    print(pkt.build())
    return

    UDP_IP = "127.0.0.1"
    UDP_PORT = 12000
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)  # UDP

    sock.bind((UDP_IP, UDP_PORT))
    sock.sendto(pkt.build(), addr_udpl)


# retransmission_time = datetime.timedelta(seconds=3) # adjust per TCP standard
# seg_size = 576

# read binary data from a file
def readFiles(file_name):
    file_bytes = bytearray()
    try:
        with open(file_name, "rb") as f:
            file_bytes += f.read()
    except IOError:
        print("Did not find the file under correct directory!")
    return file_bytes


if __name__ == "__main__":
    print(sys.argv)
    packetSender(sys.argv)