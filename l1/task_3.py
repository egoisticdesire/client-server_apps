"""
Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
Важно: решение должно быть универсальным, т.е. не зависеть от того, какие конкретно слова мы исследуем.
"""


def words_cant_be_bytes(a):
    for i in a:
        print(f'"\033[32m{i}\033[0m" - возможно записать в байтовом типе') \
            if i.isascii() \
            else print(f'"\033[31m{i}\033[0m" - невозможно записать в байтовом типе')

WORDS = [
        'attribute',
        'класс',
        'функция',
        'type',
]

words_cant_be_bytes(WORDS)

# while True:
#     words_cant_be_bytes(input('\nEnter your word: ').split())
