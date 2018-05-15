import argparse
from json import loads
from urllib.request import urlopen


def main(method, params, fields):
    data = __send_recv(_KEY, method, params, fields, _VERSION)['response']
    
    if method.startswith('users.get'):
        __parse_response_items(data)
    else:
        __parse_response(data)


def __parse_response(data):
    print(f'count: {data["count"]}')
    users = data['items']
    __parse_response_items(users)


def __parse_response_items(items):
    for item in items:
        print('\n#############################################\n')
        for field in item.keys():
            print(f'{field}: {item[field]}')


def __send_recv(token, method, params, fields, version):
    url = f'https://api.vk.com/method/{method}?{"&".join(params)}'
    if fields:
        url += f'&fields={",".join(fields)}'
    url += f'&access_token={token}&v={version}'
    return loads(urlopen(url).read())


def __parse_cmd():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-m',
        '--method',
        nargs='?',
        help='Enter the method from VK API'
    )
    parser.add_argument(
        '-p',
        '--parameters',
        nargs='*',
        default='',
        help='Enter parameters for method'
    )
    parser.add_argument(
        '-f',
        '--fields',
        nargs='*',
        default='',
        help='Allow to filter objects by specified fields. For example: bdate city'
    )

    return parser


if __name__ == '__main__':
    parser = __parse_cmd()
    args = parser.parse_args()
    main(args.method, args.parameters, args.fields)
