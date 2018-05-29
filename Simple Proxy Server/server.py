import socket
from http.client import HTTPException
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer
from threading import Thread
from select import select
from urllib.request import urlopen

TIMEOUT = 0.1
BUFFER_SIZE = 8192
BLACKLIST = {
    'rs.mail.ru',
    'r.mradx.net',
    't.mail.ru',
    'geekbrains.ru',
    'goto.msk.ru',
    'reklama5.ngs.ru'
}


class SimpleHTTPProxyHandler(SimpleHTTPRequestHandler):
    def do_CONNECT(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            host, port = tuple(self.path.split(':'))
            address = (host, int(port))
            try:
                if any([h in host for h in BLACKLIST]):
                    self.send_error(423, f'Host {host} is in black list.')
                    return
                client_socket.connect(address)
                self.send_response(200, 'Connection established')
                self.send_header('Proxy-agent', '')
                self.end_headers()

                connections = [self.connection, client_socket]
                while True:
                    rlist, wlist, xlist = select(connections, [], connections, TIMEOUT)
                    if xlist:
                        break
                    for r in rlist:
                        data = r.recv(BUFFER_SIZE)
                        if data:
                            cur_sock = connections[0] if r is connections[1] else connections[1]
                            cur_sock.sendall(data)

            except socket.error:
                self.send_error(404, 'Page is not found')
            except ConnectionAbortedError or HTTPException:
                print()
            finally:
                self.connection.close()

    def do_GET(self):
        self.copyfile(urlopen(self.path), self.wfile)


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass


if __name__ == '__main__':
    server = ThreadedTCPServer(('127.0.0.1', 8080), SimpleHTTPProxyHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()
