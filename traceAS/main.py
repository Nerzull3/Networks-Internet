import socket
from json import loads
from urllib.request import urlopen

PRIVATE_IP_ADDRS = {
    ('10.0.0.0', '10.255.255.255'),
    ('127.0.0.0', '127.255.255.255'),
    ('172.16.0.0', '172.31.255.255'),
    ('192.168.0.0', '192.168.255.255')
}


class TraceAS:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.sock.settimeout(5)
        self.ttl = 1
        self.cur_addr = None
        self.echo_query = b'\x08\x00\x0b\x27\xeb\xd8\x01\x00'

    def get_trace(self, destination):
        self.sock.setsockopt(socket.SOL_IP, socket.IP_TTL, self.ttl)
        try:
            self.sock.sendto(self.echo_query, (destination, 43))
            ip = self.sock.recvfrom(1024)[1]
            self.cur_addr = ip[0]
            self.ttl += 1
            return self.cur_addr
        except socket.timeout:
            self.ttl += 1
            return '***'

    @staticmethod
    def is_public_ip(ip):
        for diapason in PRIVATE_IP_ADDRS:
            if diapason[0] <= ip <= diapason[1]:
                return False
        return True

    """ Visiting the site http://ipinfo.io """
    @staticmethod
    def get_info_by_ip(ip):
        data = loads(urlopen(f'http://ipinfo.io/{ip}/json').read())
        return f'{data["country"]}, {data["region"]}, {data["city"]}, {data["org"]}'


if __name__ == '__main__':
    traceAS = TraceAS()
    dest = socket.gethostbyname(input('Enter the destination: '))
    print(f'Destination: {dest}\n')
    ip = None

    while ip != dest:
        ip = traceAS.get_trace(dest)

        if ip == '***':
            print(f'{traceAS.ttl - 1}. {ip}'
                  f'{" "*(20 - len(ip) - len(str(traceAS.ttl - 1)))}'
                  f'Query interval exceeded.')
        elif traceAS.is_public_ip(ip):
            print(f'{traceAS.ttl - 1}. {ip}'
                  f'{" "*(20 - len(ip) - len(str(traceAS.ttl - 1)))}'
                  f'{traceAS.get_info_by_ip(ip)}')
        else:
            print(f'{traceAS.ttl - 1}. {ip}')

    traceAS.sock.close()
