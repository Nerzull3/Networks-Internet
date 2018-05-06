import socket
import ssl
import re
import base64


FROM = re.compile('From: ([\S]+)')
TO = re.compile('To: ([\S]+)')
SUBJECT = re.compile('Subject: ([\S]+)')
MIME_VERSION = re.compile('MIME-Version: ([\d.]+)')
DATE = re.compile('Date: ([\S ]+)')

header_types = [FROM, TO, SUBJECT, MIME_VERSION, DATE]


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        sock = ssl.wrap_socket(sock)
        sock.connect(('pop.yandex.ru', 995))

        user, password = __parse_config()
        print(__send_recv(f'USER {user}', sock))
        print(__send_recv(f'PASS {password}', sock))

        while True:
            try:
                cmd = input('Enter command: ')
                __execute_cmd_type(cmd, sock)

            except socket.error:
                print('ERROR!')
                break


def __execute_cmd_type(cmd, sock):
    if cmd == '-h':
        __get_commands_info()
    elif cmd == 'STAT':
        print(__send_recv(cmd, sock))
    elif cmd.startswith('LIST'):
        print(__send_recv(cmd, sock))
    elif cmd.startswith('TOP'):
        receive = __send_recv(cmd, sock)
        __parse_receive(receive)
        print(receive)
    elif cmd.startswith('RETR'):
        print(__send_recv(cmd, sock))
    elif cmd.startswith('DELE'):
        print(__send_recv(cmd, sock))
    elif cmd == 'NOOP':
        print(__send_recv(cmd, sock))
    elif cmd == 'RSET':
        print(__send_recv(cmd, sock))
    elif cmd.startswith('QUIT'):
        print(__send_recv('QUIT', sock))
        print('Disconnect from the server...\n')
        quit(0)
    else:
        print(f'Entered incorrect command: {cmd}\n')


def __send_recv(command, sock):
    result = b''

    try:
        sock.send((command + '\n').encode())
    except socket.timeout:
        print('Message was not sent!')
        quit(0)
    while True:
        try:
            data = sock.recv(1024)
            result += data
            if not data:
                break
        except socket.timeout:
            break

    return result.decode()


def __parse_config():
    with open('config', 'r') as f:
        lines = f.read().splitlines()
        return tuple([line.split(': ')[1] for line in lines])


def __parse_receive(receive):
    index = receive.find('------==--bound')
    headers = receive[:index]
    __parse_headers(headers)
    content = receive[index:]
    __parse_content(content)


def __parse_headers(headers):
    result = []
    for header in header_types:
        result.append(re.search(header, headers).group(1))

    __write_message_headers(result)
    print(result)


def __parse_content(content):
    def __find_all(string, substring):
        start = 0
        while True:
            start = string.find(substring, start)
            if start == -1:
                return
            yield start
            start += len(substring)

    parts = list(__find_all(content, 'Content-Transfer-Encoding: '))

    for i in range(len(parts)):
        part = content[parts[i]:parts[i + 1]] if i < len(parts) - 1 else content[parts[i]:]
        encoding = re.search('Content-Transfer-Encoding: ([\S]+)', part).group(1)
        name = re.search('Content-Type: .+?/.+?; ([\S]+)', part).group(1)

        filename = re.search('\"(.+)\"', name).group(1) if name.startswith('name=') else 'message.txt'
        regex = re.compile('(?<={}\r\n)[\S \r\n]+(?=\n------==--bound)'.format(name))
        part = re.search(regex, part).group()

        __write_message_body(part, filename, encoding != '8bit')


def __write_message_headers(headers):
    with open(f'{headers[2]}.txt', 'w', encoding='utf-8') as f:
        for line in headers:
            f.write(f'{line}\n')


def __write_message_body(message, filename, is_base64):
    with open(filename, 'wb') as f:
        result = base64.b64decode(message) if is_base64 else message.encode()
        f.write(result)


def __get_commands_info():
    print("""Command Set:
                STAT                    Get mailbox status. The result is a tuple of 2 integers: 
                                        (message count, mailbox size).
                
                LIST [msg]              Request message list, result is in the form 
                                        (response, ['msg_num octets', ...], octets).
                                        
                TOP msg [amount]        Retrieves the message header plus how much lines of the message 
                                        after the header of message number. 
                                        Result is in form (response, ['line', ...], octets).
                
                RETR msg                Retrieve whole message number and set its seen flag. 
                                        Result is in form (response, ['line', ...], octets).
                
                DELE msg                Flag message number which for deletion.
                
                NOOP                    Do nothing. Might be used as a keep-alive.
                
                RSET                    Remove any deletion marks for the mailbox.
                
                QUIT                    Sign off: commit changes, unlock mailbox, drop connection.
        """)


if __name__ == '__main__':
    main()
