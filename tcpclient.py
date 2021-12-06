# data sender

# input format
# tcpclient file address_of_udpl port_number_of_udpl windowsize ack_port_number

# implement 20-byte header

import sys
import datetime

file_name = sys.argv[1]
addr_udpl = sys.argv[2]
port_udpl = sys.argv[3]
window_size = sys.argv[4] # unit in bytes
port_ack = sys.argv[5]

seq_num = 0
retrans_time = datetime.timedelta(seconds=3) # adjust per TCP standard
seg_size = 576

# read data from a file


check_sum = 0
# compute checksum
def compute_checksum(tcp_header, data):
    pass


# send data to emulator, addr_udpl, port_udpl




