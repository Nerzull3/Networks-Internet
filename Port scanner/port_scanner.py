import socket
import re
import struct


class PortScanner:
    DNS_PACKET = b'\xff\x75\x01\x00\x00\x01\x00\x00\x00\x00' \
                 b'\x00\x00\x07\x61\x76\x61\x74\x61\x72\x73' \
                 b'\x03\x6d\x64\x73\x06\x79\x61\x6e\x64\x65' \
                 b'\x78\x03\x6e\x65\x74\x00\x00\x01\x00\x01'

    TCP_PACKETS = {
        'POP3': b'AUTH',
        'SMTP': b'EHLO',
        'HTTP': b'\0',
        'DNS': DNS_PACKET
    }

    UDP_PACKETS = {
        'SNTP': b'\x1b' + 47 * b'\0',
        'DNS': DNS_PACKET
    }

    CHECKER = {
        'HTTP': lambda packet: b'HTTP' in packet,
        'SMTP': lambda packet: re.match(b'[0-9]{3}', packet),
        'POP3': lambda packet: packet.startswith(b'+'),
        'DNS': lambda packet: packet.startswith(b'\xff\x75'),
        'SNTP': lambda packet: PortScanner.__check_on_sntp(packet)
    }

    def __init__(self, destination, timeout):
        self.timeout = timeout
        self.remote_server_ip = socket.gethostbyname(destination)
        print(f'Remote server: {self.remote_server_ip} ({destination})')

    def scan_tcp(self, port_num):
        socket.setdefaulttimeout(self.timeout)
        for protocol, packet in PortScanner.TCP_PACKETS.items():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.connect((self.remote_server_ip, port_num))
                except socket.timeout:
                    return port_num, None
                try:
                    if protocol == 'DNS':
                        packet = struct.pack('!H', len(packet)) + packet

                    sock.send(packet)
                    packet = sock.recv(1024)

                    if protocol == 'DNS':
                        packet = packet[2:]

                    if PortScanner.CHECKER[protocol](packet):
                        return port_num, protocol
                    return port_num, 'Unknown protocol'
                except socket.error:
                    continue
        return port_num, None

    def scan_udp(self, port_num):
        socket.setdefaulttimeout(self.timeout)
        for protocol, packet in PortScanner.UDP_PACKETS.items():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(packet, (self.remote_server_ip, port_num))
                try:
                    if PortScanner.CHECKER[protocol](sock.recv(1024)):
                        return port_num, protocol
                    return port_num, 'Unknown protocol'
                except socket.error:
                    continue
        return port_num, None

    @staticmethod
    def __check_on_sntp(packet):
        try:
            struct.unpack('!BBBb11I', packet)
            return True
        except struct.error:
            return False
