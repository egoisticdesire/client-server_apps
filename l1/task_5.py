"""
Написать код, который выполняет пинг веб-ресурсов yandex.ru, youtube.com и преобразовывает результат
из байтовового типа данных в строковый без ошибок для любой кодировки операционной системы.
"""

import chardet
import subprocess
import platform

param = '-n' if platform.system().lower() == 'windows' else '-c'
source = [
        'youtube.com',
        'google.com',
        'apple.com',
        'gb.ru',
]

while Exception:
    try:
        print('Select the resource to be pinged:')
        for idx, value in enumerate(source):
            print(f'\t{idx + 1}) {value}')

        position = int(input('\nEnter your choice: ')) - 1
        args = [
                'ping',
                param,
                '4',
                source[position],
        ]
        action = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in action.stdout:
            result = chardet.detect(line)
            # print(f'result = {result}')
            line = line.decode(result['encoding']).encode('utf-8')
            print(line.decode('utf-8'), end='')
        break
    except Exception:
        print(f'\033[31mWrong data. Please enter a number from 1 to {len(source)}.\033[0m\n')
