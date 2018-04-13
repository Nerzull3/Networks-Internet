import struct


class DNSQuestion:
    def __init__(self, q_type, host_name):
        self.host_name = host_name
        self.type = q_type
        self.request_class = 1

    def encode_question(self):
        result = b''
        names = self.host_name.split('.')
        for name in names:
            result += struct.pack('B', len(name)) + bytes(name, 'utf-8')
        result += b'\x00'

        result += struct.pack('!H', self.type)
        result += struct.pack('!H', self.request_class)

        return result

    def decode_question(self, message, offset):
        name = self.decode_domain_name(message, offset)
        self.host_name = name[0]
        offset = name[1]
        self.type = struct.unpack('!H', message[offset:offset + 2])[0]
        offset += 2
        self.request_class = struct.unpack('!H', message[offset: offset + 2])[0]
        offset += 2
        return offset

    @staticmethod
    def decode_s_question(message, offset):
        name = DNSQuestion.decode_domain_name(message, offset)
        host_name = name[0]
        offset = name[1]
        q_type = struct.unpack('!H', message[offset:offset + 2])[0]
        return host_name, q_type

    @staticmethod
    def decode_domain_name(message, offset):
        result = ''
        i = offset
        offset = 0
        while message[i] > 0:
            if message[i] == 192:
                if offset == 0:
                    offset = i + 2
                i = message[i + 1]
            else:
                result += message[i + 1: i + 1 + message[i]].decode('utf-8')
                result += '.'
                i += message[i] + 1

        return (result[:-1], offset) if offset != 0 else (result[:-1], i + 1)

    def print_question(self, debug):
        if debug:
            print('     Name  : {0}'.format(self.host_name))
            print('     Type  : {0}'.format(self.type))
            print('     Class : {0}'.format(self.request_class))
