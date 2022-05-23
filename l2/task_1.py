"""
Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
«Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
"""

from chardet import detect
import re
import csv


def get_data(files):
    main_data = []
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)

    REG = r'\s+([\w\s\.-]+)\r'

    for file in files:
        with open(file, 'rb') as f:
            data_b = f.read()
            encoding = detect(data_b)['encoding']
            data = data_b.decode(encoding)

            os_prod_list.append(re.findall(f'^Изготовитель системы:{REG}$', data, re.MULTILINE)[0])
            os_name_list.append(re.findall(f'^Название ОС:{REG}$', data, re.MULTILINE)[0])
            os_code_list.append(re.findall(f'^Код продукта:{REG}$', data, re.MULTILINE)[0])
            os_type_list.append(re.findall(f'^Тип системы:{REG}$', data, re.MULTILINE)[0])

    for i in range(len(files)):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])
    # print(main_data)
    return main_data


def write_to_csv(file, files):
    with open(file, 'w', encoding='utf-8') as f:
        f_writer = csv.writer(f)
        f_writer.writerows(get_data(files))
    print(f'A file named \033[32m{file}\033[0m has been created!\n\033[32mEnjoy!\033[0m')


FILENAME = f'{input("Enter a file name (without extension): ")}.csv'
FILES = ['info_1.txt', 'info_2.txt', 'info_3.txt']
write_to_csv(FILENAME, FILES)
