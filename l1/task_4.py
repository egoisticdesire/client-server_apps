"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
в байтовое и выполнить обратное преобразование (используя методы encode и decode).
"""


def words_str_to_bytes(a):
    for i in a:
        str_to_bytes = i.encode('utf-8')
        bytes_to_str = str_to_bytes.decode('utf-8')
        print(f'encode: {str_to_bytes}')
        print(f'decode: {bytes_to_str}')
        print('====================')


WORDS = [
        'разработка',
        'администрирование',
        'protocol',
        'standard',
]

words_str_to_bytes(WORDS)
