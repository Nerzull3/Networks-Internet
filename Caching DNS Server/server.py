import socket
import time
import pickle
import argparse

from DNS_Question import DNSQuestion
from data_DNS_package import MessageFormat


class DNSServer:
    def __init__(self, ip_server, forwarding_server, cache_file, debug):
        self.server_ip = ip_server
        self.cache = {1: {}, 2: {}}
        self.client_ip = None
        self.forwarding_server = forwarding_server
        self.cache_file = cache_file
        self.debug = debug

    def start_working(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(15)
            sock.bind((self.server_ip, 1024))
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)

            while True:
                try:
                    data, self.client_ip = sock.recvfrom(1024)
                    print('Пакет получен!')
                    # раскодировать пакет и достать имя и тип запроса
                    hostname, q_type = DNSQuestion.decode_s_question(data, 12)
                    # если лежит в кэше
                    current_time = int(time.time())
                    if self.is_exist_in_cache(q_type, hostname) and self.cache[q_type][hostname][1] >= current_time:
                        print('In if!')
                        # to take data from cache
                        print(self.cache[q_type][hostname])
                        sock.sendto(self.cache[q_type][hostname][0], self.client_ip)
                        print('Пакет отправлен!\n')
                    elif self.is_exist_in_cache(q_type, hostname) and self.cache[q_type][hostname][1] < current_time:
                        self.cache[q_type].pop(hostname)
                        print('In else!')
                        data_from_dns = self.ask_to_dns(q_type, hostname)
                        sock.sendto(data_from_dns, self.client_ip)
                        print('Пакет отправлен!\n')
                    else:
                        print('In else!')
                        data_from_dns = self.ask_to_dns(q_type, hostname)
                        sock.sendto(data_from_dns, self.client_ip)
                        print('Пакет отправлен!\n')
                except socket.timeout or KeyboardInterrupt:
                    with open(self.cache_file, 'wb') as f:
                        pickle.dump(self.cache, f)
                    break

    def is_exist_in_cache(self, q_type, hostname):
        return hostname in self.cache[q_type].keys()

    def write_in_cache(self, data, response):
        for answers in data:
            for answer in answers:
                self.cache[answer[1]].update({answer[0]: (response, answer[3] + int(time.time()))})

    def ask_to_dns(self, q_type, host):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)
            try:
                sock.connect((self.forwarding_server, 53))
                message = MessageFormat(q_type, host)
                query = message.encode_message()
                sock.send(query)

                response = sock.recv(1024)
                message.decode_message(response)

                data_to_cache = message.print_result(self.debug)
                self.write_in_cache(data_to_cache, response)
                print(data_to_cache)
                print(self.cache)

                # to send a DNS packet
                return response

            except socket.timeout:
                print(f'Cannot connect to server {self.forwarding_server}')


def parse():
    parser = argparse.ArgumentParser(
        usage='-s <server name> -fs <forwarding server> [-d]'
    )

    parser.add_argument(
        '-s',
        '--server',
        required=True,
        help='Enter forwarding server number'
    )
    parser.add_argument(
        '-fs',
        '--forwarding_server',
        required=True,
        help='Enter server number'
    )
    parser.add_argument(
        '-d',
        '--debug',
        required=False,
        nargs='?',
        help='Debug mode'
    )
    return parser


if __name__ == '__main__':
    parser = parse()
    args = parser.parse_args()
    server = DNSServer(ip_server=args.server,
                       forwarding_server=args.forwarding_server,
                       cache_file='cache.txt',
                       debug=True if args.debug else False)
    server.start_working()
