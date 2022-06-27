import argparse
import select
import sys

from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from logs.server_log_config import LOGGER
from common.decorators import Log
from common.utils import get_message, send_message
from common.variables import ACCOUNT_NAME, ACTION, CONNECTION_TIMEOUT, DEFAULT_PORT, DESTINATION, ERROR, EXIT, \
    MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, PRESENCE, RESPONSE_200, RESPONSE_400, SENDER, TIME, USER


@Log
def process_client_message(message, messages_list, client, names, clients):
    """
    Принимает сообщение в виде словаря,
    проверяет корректность данных,
    возвращает ответ в виде словаря.
    :param names:
    :param clients:
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
            and USER in message:
        # Регистрация имени пользователя
        # Иначе ответ с ошибкой
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Это имя уже используется.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если обычное сообщение - добавляем в очередь. Ответ не требуется.
    elif ACTION in message \
            and message[ACTION] == MESSAGE \
            and DESTINATION in message \
            and TIME in message \
            and SENDER in message \
            and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    # Если клиент выходит.
    elif ACTION in message \
            and message[ACTION] == EXIT \
            and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
        # Иначе - Bad Request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Некорректный запрос'
        send_message(client, response)
        return


@Log
def process_message(message, names, listen_sockets):
    """
    Адресная отправка сообщений конкретному клиенту.
    Принимает словарь сообщение, список зарегистрированных пользователей, слушающие сокеты.
    Ничего не возвращает.
    :param message:
    :param names:
    :param listen_sockets:
    :return:
    """
    if message[DESTINATION] in names \
            and names[message[DESTINATION]] in listen_sockets:
        send_message(names[message[DESTINATION]], message)
        LOGGER.info(f'Сообщение пользователю {message[DESTINATION]} от {message[SENDER]}.')
    elif message[DESTINATION] in names \
            and names[message[DESTINATION]] not in listen_sockets:
        raise ConnectionError
    else:
        LOGGER.error(f'Пользователь {message[DESTINATION]} не зарегистрирован.')


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
        s.settimeout(CONNECTION_TIMEOUT)
        s.listen(MAX_CONNECTIONS)

        clients = []  # список клиентов
        messages = []  # очередь сообщений
        names = {}  # {client_name: client_socket}

        while True:
            # Ожидаем подключение. В случае таймаута - ловим исключение.
            try:
                client, client_addr = s.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Успешное соединение с {client_addr}')
                clients.append(client)

            recv_list = []
            send_list = []
            err_list = []
            # Проверка на наличие ожидающих клиентов.
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
                        process_client_message(get_message(client_with_msg), messages, client_with_msg, names, clients)
                    except Exception:
                        LOGGER.info(f'Пользователь {client_with_msg.getpeername()} отключился от сервера.')
                        clients.remove(client_with_msg)

            # Если есть сообщения - обрабатываем каждое.
            for i in messages:
                try:
                    process_message(i, names, send_list)
                except Exception:
                    LOGGER.info(f'Пользователь {i[DESTINATION]} отключился.')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()


if __name__ == '__main__':
    main()
