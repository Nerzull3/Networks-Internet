import argparse
import socket

from data_DNS_package import MessageFormat


def main(hostname, q_type):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)
        try:
            sock.connect(('127.0.0.1', 1024))
            message = MessageFormat(q_type, hostname)
            query = message.encode_message()
            sock.send(query)

            response = sock.recv(1024)
            message.decode_message(response)
            message.print_result(debug=True)

            print(response)
            print('OK!')

        except socket.timeout:
            print('Cannot connect to server 8.8.8.8')


def parse():
    parser = argparse.ArgumentParser(
        usage='-s <server name> -fs <forwarding server> [-d]'
    )

    parser.add_argument(
        '-hn',
        '--hostname',
        required=True,
        help='Enter host name'
    )
    parser.add_argument(
        '-q',
        '--query_type',
        required=True,
        help='Enter query type'
    )
    return parser


if __name__ == '__main__':
    parser = parse()
    args = parser.parse_args()
    query_type = 1 if args.query_type == 'A' else 2
    main(args.hostname, query_type)
