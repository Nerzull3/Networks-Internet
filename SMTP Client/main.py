import base64
import socket
import ssl
import re


extensions = {'image': {'png': 'png', 'gif': 'gif', 'ico': 'x-icon', 'jpeg': 'jpeg', 'jpg': 'jpeg',
                        'svg': 'svg+xml', 'tiff': 'tiff', 'tif': 'tiff', 'webp': 'webp', 'bmp': 'bmp'},
             'video': {'avi': 'x-msvideo', 'mp3': 'mpeg', 'mpeg': 'mpeg', 'ogv': 'ogg', 'webm': 'webm'},
             'application': {'zip': 'zip', 'xml': 'xml', 'bin': 'octet-stream', 'bz': 'x-bzip', 'doc': 'msword',
                             'epub': 'epub+zip', 'js': 'javascript', 'json': 'json', 'pdf': 'pdf',
                             'ppt': 'vnd.ms-powerpoint', 'rar': 'x-rar-compressed', 'sh': 'x-sh', 'tar': 'x-tar'},
             'audio': {'wav': 'x-wav', 'oga': 'ogg'},
             'text': {'css': 'css', 'csv': 'csv', 'html': 'html', 'htm': 'html', 'txt': 'plain'}}


def main(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock = ssl.wrap_socket(sock)
        sock.settimeout(60)
        sock.connect(('smtp.yandex.ru', 465))

        try:
            print(send_recv(b'EHLO Nerzull321@yandex.ru', sock))
            print(send_recv(b'AUTH LOGIN', sock))
            print(send_recv(base64.b64encode(bytes(data['login'], encoding='utf-8')), sock))
            print(send_recv(base64.b64encode(bytes(data['password'], encoding='utf-8')), sock))
            print(send_recv(bytes(f'MAIL FROM: {data["from"]}', encoding='utf-8'), sock))
            print(send_recv(bytes(f'RCPT TO: {data["to"]}', encoding='utf-8'), sock))
            print(send_recv(b'DATA', sock))
            print(send_recv(create_message(data), sock))
        except socket.timeout or Exception:
            print('Error by sending!')


def parse_info():
    with open('config', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        data = {}
        for line in lines:
            d = line.split(':')
            if len(d) == 2:
                data.update({d[0]: d[1].strip()})

        return data


def parse_message():
    with open('message', 'r', encoding='utf-8') as f:
        message = ''
        line = f.readline()
        while line:
            if re.match('^\.+\n$', line):
                message += line[:-1] + '.\n'
            elif re.match('^\.+$', line):
                message += line + '.'
            else:
                message += line
            line = f.readline()
        return message


def send_recv(mes, sock):
    sock.send(mes + b'\n')
    return sock.recv(1024).decode('utf-8')


def create_message(data):
    if not data['formatted_attachments']:
        message = f"From: {data['from']}\n" \
                  f"To: {data['to']}\n" \
                  f"Subject: {data['subject']}\n" \
                  f"MIME-Version: 1.0\n" \
                  f"Content-Type: text/plain; charset=utf-8\n" \
                  f"Content-Transfer-Encoding: 8bit\n" \
                  f"\n" \
                  f"{parse_message()}\n" \
                  f"."
    else:
        message = f"From: {data['from']}\n" \
                  f"To: {data['to']}\n" \
                  f"Subject: {data['subject']}\n" \
                  f"MIME-Version: 1.0\n" \
                  f"Content-Type: multipart/mixed; boundary=\"{data['boundary']}\"\n" \
                  f"\n" \
                  f"--{data['boundary']}\n" \
                  f"Content-Type: text/plain; charset=utf-8\n" \
                  f"Content-Transfer-Encoding: 8bit\n" \
                  f"\n" \
                  f"{parse_message()}\n" \
                  f"{get_format(data)}\n" \
                  f"--{data['boundary']}--\n" \
                  f"."
    return bytes(message, encoding='utf-8')


def get_format(data):
    filenames = data['formatted_attachments'].split(',')
    message = ''
    for filename in filenames:
        filename = filename.strip()
        with open(filename, 'rb') as f:
            content = base64.b64encode(f.read())
        filetype, ext = get_type_and_extension(filename)

        message += f"--{data['boundary']}\n" \
                   f"Content-Disposition: attachment; filename=\"{filename}\"\n" \
                   f"Content-Transfer-Encoding: base64\n" \
                   f"Content-Type: {filetype}/{ext}; name=\"{filename}\"\n" \
                   f"\n" \
                   f"{content.decode()}\n"
    return message


def get_type_and_extension(filename):
    for (type, value) in extensions.items():
        for extension in value.keys():
            if extension == filename.split('.')[-1]:
                return type, value[extension]
    raise ValueError("Type or extension of file is incorrect")


if __name__ == '__main__':
    data = parse_info()
    main(data)
