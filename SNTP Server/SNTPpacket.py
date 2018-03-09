import struct
from time import time


TIME1970 = 2208988800
with open('LieTime.txt', 'r') as f:
    DELAY = int(f.readlines()[0].strip('\n'))


class SNTPFormat:
    def __init__(self, data, receive_time):
        self.flags = None
        self.stratum = 2
        self.poll_interval = None
        self.precision = -5
        self.root_delay = None
        self.root_dispersion = None
        self.reference_id = None
        self.originate_timestamp = None
        self.reference_timestamp = None
        self.receive_timestamp = None
        self.transmit_timestamp = None

        self.decode_data(data, receive_time)

    def encode_data(self):
        return struct.pack('!3Bb11I',
                           self.flags,
                           self.stratum,
                           self.poll_interval,
                           self.precision,
                           self.root_delay,
                           self.root_dispersion,
                           self.reference_id,
                           int(self.reference_timestamp),
                           self.__get_fractional(self.reference_timestamp),
                           int(self.originate_timestamp),
                           self.__get_fractional(self.originate_timestamp),
                           int(self.receive_timestamp),
                           self.__get_fractional(self.receive_timestamp),
                           int(self.transmit_timestamp),
                           self.__get_fractional(self.transmit_timestamp)
                           )

    def decode_data(self, data, rec_time):
        unpack_data = struct.unpack('!3Bb11I', data)
        self.flags = unpack_data[0]
        self.stratum = unpack_data[1]
        self.poll_interval = unpack_data[2]
        self.precision = unpack_data[3]
        self.root_delay = unpack_data[4]
        self.root_dispersion = unpack_data[5]
        self.reference_id = unpack_data[6]
        self.reference_timestamp = rec_time + TIME1970
        self.originate_timestamp = unpack_data[10] + unpack_data[11] * 2 ** 32
        self.receive_timestamp = rec_time + TIME1970 + DELAY
        self.transmit_timestamp = time() + TIME1970 + DELAY

    @staticmethod
    def __get_fractional(timestamp):
        return int((timestamp - int(timestamp)) * 2 ** 32)
