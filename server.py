import socket
from SNTPpacket import SNTPFormat
from time import time


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def connect(self):
        self.server.bind(('127.0.0.1', 123))
        self.server.settimeout(120)

        while True:
            try:
                data, addr = self.server.recvfrom(1024)
            except socket.timeout:
                print('Waiting time has passed!')
                break

            sntp_packet = SNTPFormat(data, time())
            self.server.sendto(sntp_packet.encode_data(), addr)
        self.server.close()


if __name__ == '__main__':
    server = Server()
    server.connect()


