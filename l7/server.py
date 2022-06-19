import argparse
import select
import sys
import time

from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from logs.server_log_config import LOGGER
from common.decorators import Log
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, CONNECTION_TIMEOUT, DEFAULT_PORT, ERROR, MAX_CONNECTIONS, MESSAGE, \
    MESSAGE_TEXT, PRESENCE, RESPONSE, SENDER, TIME, USER


@Log
def process_client_message(message, messages_list, client):
    """
    Принимает сообщение в виде словаря,
    проверяет корректность данных,
    возвращает ответ в виде словаря.
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # Если сообщение о присутствии - принимаем, отвечаем
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    # Если обычное сообщение - добавляем в очередь. Ответ не требуется.
    elif ACTION in message \
            and message[ACTION] == MESSAGE \
            and TIME in message \
            and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    # Иначе - Bad Request
    else:
        send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad Request'
        })
        return


@Log
def args_parser():
    """
    Парсим аргументы командной строки.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_addr = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        LOGGER.error('Номер порта должен быть в диапазоне от 1024 до 65635.')
        sys.exit(1)

    return listen_addr, listen_port


def main():
    listen_address, listen_port = args_parser()

    # создаем сокет
    with socket(AF_INET, SOCK_STREAM) as s:
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((listen_address, listen_port))
        s.listen(MAX_CONNECTIONS)
        s.settimeout(CONNECTION_TIMEOUT)

        clients = []  # список клиентов
        messages = []  # очередь сообщений

        while True:
            # Ожидаем подключение. В случае таймаута - ловим исключение.
            try:
                client, client_addr = s.accept()
            except OSError:
                print(OSError.errno)  # todo: почему возвращается не None?
                pass
            else:
                LOGGER.info(f'Успешное соединение с {client_addr}')
                clients.append(client)

            recv_list = []
            send_list = []
            err_list = []

            try:
                if clients:
                    recv_list, send_list, err_list = select.select(clients, clients, [], 0)
            except OSError:
                pass

            # Принимаем сообщение.
            # Если есть сообщение - кладем в словарь.
            # Если ошибка - исключаем клиента.
            if recv_list:
                for client_with_msg in recv_list:
                    try:
                        process_client_message(get_message(client_with_msg), messages, client_with_msg)
                    except Exception:
                        LOGGER.info(f'Пользователь {client_with_msg.getpeername()} отключился от сервера.')
                        clients.remove(client_with_msg)

            # Если есть сообщения для отправки и ожидающие клиенты - отправляем им сообщение.
            if messages and send_list:
                msg = {
                        ACTION: MESSAGE,
                        SENDER: messages[0][0],
                        TIME: time.time(),
                        MESSAGE_TEXT: messages[0][1]
                }
                del messages[0]
                for waiting_client in send_list:
                    try:
                        send_message(waiting_client, msg)
                    except Exception:
                        LOGGER.info(f'Пользователь {client_with_msg.getpeername()} отключился от сервера.')
                        waiting_client.close()
                        clients.remove(waiting_client)


if __name__ == '__main__':
    main()
