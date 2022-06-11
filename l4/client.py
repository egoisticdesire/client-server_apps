"""
Функции клиента:
    сформировать presence-сообщение; +
    отправить сообщение серверу; +
    получить ответ сервера; +
    разобрать сообщение сервера; +
    параметры командной строки скрипта client.py <addr> [<port>]:
        addr — ip-адрес сервера;
        port — tcp-порт на сервере, по умолчанию 7777.
"""

import sys
import json
from time import time
from socket import AF_INET, SOCK_STREAM, socket
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, DEFAULT_IP_ADDRESS, DEFAULT_PORT, ERROR, PRESENCE, RESPONSE, TIME, \
    USER


def presence_message(account_name='Guest'):
    out_msg = {
            ACTION: PRESENCE,
            TIME: time(),
            USER: {
                    ACCOUNT_NAME: account_name,
            }
    }
    return out_msg


def process_server_message(message):
    """
    Принимает сообщение в виде словаря,
    проверяет корректность данных,
    возвращает ответ в виде словаря.
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'{message[RESPONSE]}: {message[ERROR]}'
    raise ValueError


def main():
    # обрабатываем параметры командной строки
    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        print(f'Не указан ip адрес и/или номер порта. '
              f'Применено значение по-умолчанию - {DEFAULT_IP_ADDRESS}:{DEFAULT_PORT}.\n')
        server_addr = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('Значение порта может быть только числом в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # инициализируем сокет
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((server_addr, server_port))

    # отправляем сообщение
    send_message(sock, presence_message('Zohan'))

    # получаем ответ сервера
    try:
        answer = process_server_message(get_message(sock))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Сообщение сервера не декодировано.')


if __name__ == '__main__':
    main()
