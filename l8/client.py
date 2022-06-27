import argparse
import sys
import json
import threading

from time import sleep, time
from socket import AF_INET, SOCK_STREAM, socket
from logs.client_log_config import LOGGER
from common.decorators import Log
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, DEFAULT_IP_ADDRESS, DEFAULT_PORT, DESTINATION, ERROR, EXIT, MESSAGE, \
    MESSAGE_TEXT, PRESENCE, RESPONSE, SENDER, TIME, USER


@Log
def create_exit_message(account_name):
    """
    Создание словаря с сообщением о выходе
    :param account_name:
    :return:
    """
    return {
            ACTION: EXIT,
            TIME: time(),
            ACCOUNT_NAME: account_name
    }


@Log
def message_from_server(sock, username):
    """
    Обрабатываем сообщения других пользователей.
    :param username:
    :param sock:
    :return:
    """
    while True:
        try:
            message = get_message(sock)
            if ACTION in message \
                    and message[ACTION] == MESSAGE \
                    and SENDER in message \
                    and DESTINATION in message \
                    and MESSAGE_TEXT in message \
                    and message[DESTINATION] == username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n'
                      f'{message[MESSAGE_TEXT]}\n\nВыберите действие: ', end='')
            else:
                LOGGER.error(f'Некорректное сообщение с сервера: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            LOGGER.critical('Потеряно соединение с сервером.')
            break


@Log
def create_message(sock, account_name='Guest'):
    """
    Запрашиваем имя получателя и текст сообщения.
    Отправляем на сервер.
    :param sock:
    :param account_name:
    :return:
    """
    to_user = input('Имя получателя: ')
    msg = input('Сообщение для отправки: ')
    msg_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time(),
            MESSAGE_TEXT: msg
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {msg_dict}')
    try:
        send_message(sock, msg_dict)
        LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except Exception as e:
        print(e)
        LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


def print_help():
    print('Поддерживаемые команды:\n '
          'message, m - отправить сообщение.\n '
          'help, h - вывести подсказки по командам.\n '
          'exit, q - выход из программы.\n')


@Log
def user_interactive(sock, username):
    print_help()
    while True:

        action = input('Выберите действие: ')
        if action == 'message' or action == 'm':
            create_message(sock, username)
        elif action == 'help' or action == 'h':
            print_help()
        elif action == 'exit' or action == 'q':
            send_message(sock, create_exit_message(username))
            print('Соединение разорвано.')
            LOGGER.info('Завершение работы по команде пользователя.')
            sleep(0.5)
            break
        else:
            print('Неизвестная команда.\n '
                  'help - вывести поддерживаемые команды.\n')


@Log
def create_presence(account_name='Guest'):
    """
    Генерируем запрос на присутствие клиента.
    :param account_name:
    :return:
    """
    out_msg = {
            ACTION: PRESENCE,
            TIME: time(),
            USER: {
                    ACCOUNT_NAME: account_name
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
        elif message[RESPONSE] == 400:
            return f'400: {message[ERROR]}'
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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_addr = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # Проверяем порт
    if not 1023 < server_port < 65536:
        LOGGER.error(f'Порт {server_port} недопустим. Возможны варианты от 1024 до 65535.')
        sys.exit(1)

    return server_addr, server_port, client_name


def main():
    server_addr, server_port, client_name = args_parser()

    print(f'{client_name} подключился к чату.')

    if not client_name:
        client_name = input('Имя пользователя: ')

    LOGGER.info(f'Клиент запущен с параметрами: {server_addr}:{server_port}; имя пользователя: {client_name}')

    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((server_addr, server_port))
            send_message(s, create_presence(client_name))
            answer = process_server_message(get_message(s))
            LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            LOGGER.error('Сообщение сервера не декодировано.')
            sys.exit(1)
        except TypeError:
            LOGGER.error('Попытка отправки некорректного сообщения на сервер.')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            LOGGER.error(f'Не удалось подключиться к серверу {server_addr}:{server_port}')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно:
            # запускаем клиентский процесс приёма сообщений.
            receiver = threading.Thread(target=message_from_server, args=(s, client_name))
            receiver.daemon = True
            receiver.start()
            # запускаем отправку сообщений и взаимодействие с пользователем.
            user_interface = threading.Thread(target=user_interactive, args=(s, client_name))
            user_interface.daemon = True
            user_interface.start()

            # проверяем потоки на предмет соединения.
            while True:
                sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    main()
