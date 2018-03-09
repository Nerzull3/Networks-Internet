import socket
import struct
import time


TIME1970 = 2208988800


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect(('127.0.0.1', 123))

        packet = '\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                 '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                 '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                 '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                 '\x00\x00\x00\x00\x00\x00\x00\x00'.encode('utf-8')

        self.client.send(packet)
        data, addr = self.client.recvfrom(1024)

        unpack = struct.unpack("!12I", data)
        t = (unpack[10] + unpack[11] / 2 ** 32) - TIME1970
        print('Host time:  ', time.ctime())
        print('Server time: ' + time.ctime(t))


if __name__ == '__main__':
    client = Client()
