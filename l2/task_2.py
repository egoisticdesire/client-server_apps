"""
Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными. Для этого:

Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
цена (price), покупатель (buyer), дата (date). Функция должна предусматривать запись данных в виде словаря в
файл orders.json. При записи данных указать величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""

import json
import random
from datetime import datetime
from chardet import detect


def write_order_to_json(order):
    with open('orders.json', 'rb') as f:
        encoding = detect(f.read())['encoding']

    with open('orders.json', 'r', encoding=encoding) as f:
        data = json.load(f)

    with open('orders.json', 'w', encoding=encoding) as f:
        orders = data['orders']
        orders.append(order)
        json.dump(data, f, indent=4)


ORDER = {
        'item_id': f'{random.randint(1, 100000)}',
        'quantity': f'{random.randint(1, 1000)}',
        'price': f'${random.randint(1, 100000)}',
        'buyer_id': f'{random.randint(1, 100000)}',
        'date': datetime.today().strftime('%Y-%m-%d')
}

write_order_to_json(ORDER)
