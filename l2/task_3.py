"""
Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим в
кодировке ASCII (например, €);
Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию файла
с помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
"""

import yaml
from chardet import detect

YAML_IN = {
        'first_key': [
                'one',
                'two',
                'three',
        ],
        'second_key': 123,
        'third_key': {
                'third_key_one': '€1',
                'third_key_two': [
                        '€2',
                        '€3',
                        '€4',
                ],
                'third_key_three': '€5',
        }
}

with open('file.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(YAML_IN, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

with open('file.yaml', 'rb') as f:
    data_b = f.read()
    encoding = detect(data_b)['encoding']
    data = data_b.decode(encoding)
    YAML_OUT = yaml.load(data, Loader=yaml.SafeLoader)

print(YAML_IN == YAML_OUT)
