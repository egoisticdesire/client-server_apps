import argparse
import sys
import json
import time

from socket import AF_INET, SOCK_STREAM, socket
from logs.client_log_config import LOGGER
from common.decorators import Log
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, DEFAULT_IP_ADDRESS, DEFAULT_PORT, ERROR, MESSAGE, MESSAGE_TEXT, \
    PRESENCE, RESPONSE, \
    SENDER, TIME, \
    USER


@Log
def message_from_server(message):
    """
    Обрабатываем сообщения других пользователей.
    :param message:
    :return:
    """
    if ACTION in message \
            and message[ACTION] == MESSAGE \
            and SENDER in message \
            and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(f'Некорректное сообщение с сервера: {message}')


@Log
def create_message(sock, account_name='Guest'):
    """
    Запрашиваем текст сообщения и возвращаем его.
    :param sock:
    :param account_name:
    :return:
    """
    msg = input('Сообщение для отправки или "q" для выхода: ')
    if msg == 'q':
        sock.close()
        LOGGER.info('Завершение по команде пользователя')
        print('До свидания!')
        sys.exit(0)
    msg_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MESSAGE_TEXT: msg
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {msg_dict}')
    return msg_dict


@Log
def create_presence(account_name='Guest'):
    """
    Генерируем запрос на присутствие клиента.
    :param account_name:
    :return:
    """
    out_msg = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                    ACCOUNT_NAME: account_name,
            }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out_msg


@Log
def process_server_message(message):
    """
    Принимает сообщение в виде словаря,
    проверяет корректность данных,
    возвращает ответ в виде словаря.
    :param message:
    :return:
    """
    LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'{message[RESPONSE]}: {message[ERROR]}'
    raise ValueError


@Log
def args_parser():
    """
    Парсим аргументы командной строки.
    Читаем параметры, возвращаем 3 параметра.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='send', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_addr = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # Проверяем порт
    if not 1023 < server_port < 65536:
        LOGGER.error(f'Порт {server_port} недопустим. Возможны варианты от 1024 до 65535.')
        sys.exit(1)

    # Проверяем режим работы
    if client_mode not in ('listen', 'send'):
        LOGGER.critical(f'Режим работы {client_mode} недопустим. Возможны варианты: listen или send.')
        sys.exit(1)

    return server_addr, server_port, client_mode


def main():
    server_addr, server_port, client_mode = args_parser()

    with socket(AF_INET, SOCK_STREAM) as s:
        LOGGER.info(f'Клиент запущен с параметрами: {server_addr}:{server_port}; в режиме: {client_mode}')
        try:
            s.connect((server_addr, server_port))
            send_message(s, create_presence())
            answer = process_server_message(get_message(s))
            LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except (ValueError, json.JSONDecodeError):
            LOGGER.error('Сообщение сервера не декодировано.')
            sys.exit(1)
        except TypeError:
            LOGGER.error('Попытка отправки некорректного сообщения на сервер.')
            sys.exit(1)
        except ConnectionRefusedError:
            LOGGER.error(f'Не удалось подключиться к серверу {server_addr}:{server_port}')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # начинаем обмен с ним, согласно требуемому режиму.
            # Основной цикл программы:
            if client_mode == 'send':
                print('Режим: отправка сообщений.')
            else:
                print('Режим: получение сообщений.')

            while True:
                if client_mode == 'send':
                    try:
                        send_message(s, create_message(s))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        LOGGER.error(f'Соединение с сервером {server_addr} было потеряно.')
                        sys.exit(1)
                if client_mode == 'listen':
                    try:
                        message_from_server(get_message(s))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        LOGGER.error(f'Соединение с сервером {server_addr} было потеряно.')
                        sys.exit(1)


if __name__ == '__main__':
    main()
