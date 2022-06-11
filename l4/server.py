"""
Функции сервера:
    принимает сообщение клиента; +
    формирует ответ клиенту; +
    отправляет ответ клиенту; +
    параметры командной строки:
        -p <port> — TCP-порт для работы (по умолчанию использует 7777);
        -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
"""

import sys
import json
from _socket import SOL_SOCKET, SO_REUSEADDR
from socket import AF_INET, SOCK_STREAM, socket
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, DEFAULT_PORT, ERROR, MAX_CONNECTIONS, PRESENCE, RESPONSE, TIME, USER


def process_client_message(message):
    """
    Принимает сообщение в виде словаря,
    проверяет корректность данных,
    возвращает ответ в виде словаря.
    :param message:
    :return:
    """
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            or message[USER][ACCOUNT_NAME] == 'Guest':
        return {
                RESPONSE: 200
        }
    return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
    }


def main():
    # обрабатываем порт
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65536:
            raise ValueError
    except IndexError:
        print(f'После параметра \'-p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print('Номер порта должен быть в диапазоне от 1024 до 65635.')
        sys.exit(1)

    # обрабатываем адрес
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print(f'После параметра \'-a\' необходимо указать ip адрес. По умолчанию - все доступные адреса.')
        sys.exit(1)

    # создаем сокет
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((listen_address, listen_port))

    # слушаем порт
    sock.listen(MAX_CONNECTIONS)

    try:
        while True:
            client, client_addr = sock.accept()

            try:
                msg_from_client = get_message(client)
                print(msg_from_client)
                msg_for_client = process_client_message(msg_from_client)
                send_message(client, msg_for_client)
            except (ValueError, json.JSONDecodeError):
                print('Некорректное сообщение от клиента.')
            finally:
                client.close()
    finally:
        sock.close()


if __name__ == '__main__':
    main()
