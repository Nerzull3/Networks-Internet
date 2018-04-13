import struct

from DNS_Question import DNSQuestion


class Answer:
    def __init__(self):
        self.host_name = None
        self.type = None
        self.request_class = None
        self.ttl = None
        self.data_length = None
        self.address = ''
        self.request = None

    def decode_info(self, message, offset):
        name_offset = struct.unpack_from('!H', message, offset)[0] & 0x1fff
        self.host_name = DNSQuestion.decode_domain_name(message, name_offset)[0]
        offset += 2
        self.type = struct.unpack('!H', message[offset:offset + 2])[0]
        offset += 2
        self.request_class = struct.unpack('!H', message[offset:offset + 2])[0]
        offset += 2
        self.ttl = struct.unpack('!I', message[offset: offset + 4])[0]
        offset += 4
        self.data_length = struct.unpack('!H', message[offset:offset + 2])[0]
        offset += 2
        for i in range(self.data_length):
            self.address += str(struct.unpack_from('!B', message, offset + i)[0]) + '.'
        self.address = self.address[:-1]
        self.request = Request(self.data_length, self.type, message, offset)
        return offset + self.data_length

    def print_answer(self, debug):
        if debug:
            print('     Name   : {0}'.format(self.host_name))
            print('     Type   : {0}'.format(self.type))
            print('     Class  : {0}'.format(self.request_class))
            print('     TTL    : {0}'.format(self.ttl))
        return self.host_name, self.type, self.request_class, self.ttl, self.request.print_data()


class Request:
    def __init__(self, data_length, type, message, offset):
        data = message[offset: offset + data_length]
        if type == 1:
            self.request = RequestA(data)
        elif type == 2:
            self.request = RequestNS(message, offset)
        elif type == 5:
            self.request = RequestCNAME(message, offset)
        elif type == 6:
            self.request = RequestSOA(message, offset)
        elif type == 7:
            self.request = RequestMB(message, offset)
        elif type == 12:
            self.request = RequestPTR(message, offset)
        elif type == 15:
            self.request = RequestMX(message, offset)
        elif type == 28:
            self.request = RequestAAAA(data)
        else:
            self.request = RequestBinary(data)

    def print_data(self):
        print(self.request)
        return self.request.get_info()


class RequestA:
    def __init__(self, data):
        self.ip = struct.unpack('4B', data)
        self.ip = ''.join([str(self.ip[i]) + '.' for i in range(4)])[:-1]

    def get_info(self):
        return self.ip

    def __str__(self):
        return '     Address: {0}'.format(self.ip)


class RequestNS:
    def __init__(self, message, offset):
        self.name_server = DNSQuestion.decode_domain_name(message, offset)[0]

    def get_info(self):
        return self.name_server

    def __str__(self):
        return '     NS: {0}'.format(self.name_server)


class RequestSOA:
    def __init__(self, message, offset):
        data = DNSQuestion.decode_domain_name(message, offset)
        self.primary_name_server = data[0]
        offset = data[1]
        data = DNSQuestion.decode_domain_name(message, offset)
        self.authority_mailbox = data[0]
        offset = data[1]
        self.serial_number = str(struct.unpack('!I', message[offset: offset + 4])[0])
        offset += 4
        self.refresh_interval = str(struct.unpack('!I', message[offset: offset + 4])[0])
        offset += 4
        self.retry_interval = struct.unpack('!I', message[offset: offset + 4])[0]
        offset += 4
        self.expire_limit = struct.unpack('!I', message[offset: offset + 4])[0]
        offset += 4
        self.minimum_TTL = struct.unpack('!I', message[offset: offset + 4])[0]

    def __str__(self):
        return '     Primary name server: {0}\n' \
               '     Responsible authority\'s mailbox: {1}\n' \
               '     Serial number: {2}\n' \
               '     Refresh interval: {3}\n' \
               '     Retry interval: {4}\n' \
               '     Expire limit: {5}\n' \
               '     Minimum TTL: {6}'\
            .format(
            self.primary_name_server,
            self.authority_mailbox,
            self.serial_number,
            self.refresh_interval,
            self.retry_interval,
            self.expire_limit,
            self.minimum_TTL
        )


class RequestMB:
    def __init__(self, message, offset):
        self.mailbox = DNSQuestion.decode_domain_name(message, offset)[0]

    def __str__(self):
        return '     MB: {0}'.format(self.mailbox)


class RequestPTR:
    def __init__(self, message, offset):
        self.name = DNSQuestion.decode_domain_name(message, offset)[0]
        print('     PTR: {0}'.format(self.name))
        exit(0)


class RequestCNAME:
    def __init__(self, message, offset):
        self.name = DNSQuestion.decode_domain_name(message, offset)[0]

    def __str__(self):
        return '     CNAME: {0}'.format(self.name)


class RequestMX:
    def __init__(self, message, offset):
        self.priority = struct.unpack('!H', message[offset:offset + 2])[0]
        offset += 2
        self.mail_exchanger = DNSQuestion.decode_domain_name(message, offset + 2)[0]

    def __str__(self):
        return '     MX: {0} {1}'.format(self.priority, self.mail_exchanger)


class RequestAAAA:
    def __init__(self, data):
        self.ip = ''
        dump = ''.join([str(hex(256 + byte))[3:] for byte in data])
        for i in range(8):
            value = dump[i * 4:i * 4 + 4]
            for j in range(4):
                if value[j] != '0':
                    value = value[j:]
                    break
                if j == 3:
                    value = ''
            self.ip += value + ':'
        self.ip = self.ip[:-1]
        self.__try_to_cut_ip()

    def __try_to_cut_ip(self):
        e = 0
        count = 0
        temp = []
        while e < len(self.ip):
            while self.ip[e] == ':':
                count += 1
                e += 1
            if count > 1:
                temp.append((count, e - count))
            count = 0
            e += 1

        if len(temp) == 1:
            value = temp[0]
            self.ip = self.ip[:value[1]] + self.ip[value[1] + value[0] - 2:]

    def __str__(self):
        return '     AAAA: {0}'.format(self.ip)


class RequestBinary:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return '     Data: {0}'.format(self.data)
