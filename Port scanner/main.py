import argparse
import multiprocessing

from port_scanner import PortScanner


def main(destination, timeout, start, end, t_protocol):
    scanner = PortScanner(destination, timeout)
    pool = multiprocessing.Pool(4)
    scan = pool.imap(scanner.scan_tcp, range(start, end + 1)) if t_protocol == 'tcp' \
        else pool.imap(scanner.scan_udp, range(start, end + 1))

    for port, protocol in scan:
        if protocol:
            print(f'{port} port is open by protocol "{protocol}". Transport protocol: {t_protocol}')


def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-d',
        '--destination',
        required=True,
        type=str,
        help='Destination IPv4 or hostname'
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type=float,
        default=0.1,
        help='Response timeout'
    )
    parser.add_argument(
        '-s',
        '--start',
        type=int,
        default=1,
        help='Start number of port'
    )
    parser.add_argument(
        '-e',
        '--end',
        type=int,
        default=200,
        help='End number of port'
    )
    parser.add_argument(
        '-p',
        '--protocol',
        type=str,
        help='Transport protocol'
    )

    return parser


if __name__ == '__main__':
    parser = parse()
    args = parser.parse_args()
    main(args.destination, args.timeout, args.start, args.end, args.protocol)
