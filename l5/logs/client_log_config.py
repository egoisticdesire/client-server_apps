import logging
import sys
import os
from common.variables import ENCODING, LOGGING_LVL

sys.path.insert(0, os.path.join(os.getcwd(), '..'))
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client.log')

LOGGER = logging.getLogger('client')
FORMATTER = logging.Formatter('{asctime} :: {levelname:8s} :: {name} :: {message}', style='{', datefmt='%Y-%m-%d %H:%M')

FILE_HANDLER = logging.FileHandler(PATH, encoding=ENCODING)
FILE_HANDLER.setFormatter(FORMATTER)

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.setLevel(LOGGING_LVL)

if __name__ == '__main__':
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
    LOGGER.warning('Предупреждение')
    LOGGER.error('Ошибка')
    LOGGER.critical('Критическая ошибка')
