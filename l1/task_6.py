"""
Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
Далее забыть о том, что мы сами только что создали этот файл и исходить из того, что перед нами файл в
неизвестной кодировке. Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того, в какой кодировке он был создан.
"""

from chardet import detect

LINES = [
        'сетевое программирование',
        'сокет',
        'декоратор',
]
# записываем в файл данные
with open('test_file.txt', 'w', encoding='utf-8') as f:
    for line in LINES:
        f.write(f'{line}\n')
# открываем файл на чтение в байтовом типе
with open('test_file.txt', 'rb') as f:
    content = f.read()
# узнаем и записываем в переменную информацию о кодировке
encoding = detect(content)['encoding']
# открываем файл с этой кодировкой
with open('test_file.txt', encoding=encoding) as f:
    for line in f:
        print(line, end='')
