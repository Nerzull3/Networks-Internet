import struct
import random


class MessageHeader:
    def __init__(self):
        self.length = 12
        self.message_ID = random.randint(0, 65535)
        self.recursion_flag = 1
        self.flags = 0x0100
        self.questions_count = 1
        self.answers_count = 0
        self.access_rights_count = 0
        self.additional_info_count = 0

    def encode_header(self):
        return struct.pack('!6H', self.message_ID,
                                  self.flags,
                                  self.questions_count,
                                  self.answers_count,
                                  self.access_rights_count,
                                  self.additional_info_count)

    def decode_header(self, message):
        self.message_ID = struct.unpack('!H', message[0:2])[0]
        self.flags = struct.unpack('!H', message[2:4])[0]
        self.questions_count = struct.unpack('!H', message[4:6])[0]
        self.answers_count = struct.unpack('!H', message[6:8])[0]
        self.access_rights_count = struct.unpack('!H', message[8:10])[0]
        self.additional_info_count = struct.unpack('!H', message[10:12])[0]

    def print_data(self):
        print('     Message ID: {0}'.format(hex(self.message_ID)))
        print('     Flags: {0}'.format(hex(self.flags)))
        print('     Recursion: {0}'.format(self.recursion_flag))
        print('     Questions count: {0}'.format(self.questions_count))
        print('     Answers count: {0}'.format(self.answers_count))
        print('     Access rights count: {0}'.format(self.access_rights_count))
        print('     Additional information count: {0}'.format(self.additional_info_count))